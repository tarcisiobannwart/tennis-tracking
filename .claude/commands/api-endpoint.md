# Comando: Criar Endpoint de API

Crie um novo endpoint de API no backend Python/FastAPI do Tennis Tracking.

> **NOTA**: O Tennis Tracking usa **MongoDB + Motor** (async), sem multi-tenancy. Exemplos SQLAlchemy devem ser adaptados para MongoDB. Consulte `backend/app/`.

## Estrutura do Backend

```
backend/app/
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
├── routers/         # FastAPI routers
├── auth/            # Autenticacao e autorizacao
│   ├── dependencies.py  # get_current_user, require_permission
│   └── utils.py         # JWT, password hashing
├── config.py        # Settings (pydantic-settings)
├── database.py      # SQLAlchemy async engine, session, get_db()
└── main.py          # Entry point, registra routers
```

## Instrucoes

Entrada do usuario: `$ARGUMENTS`

### Passo 1: Identificar o Modulo

Determine o modulo correto baseado nos epics do projeto:
- **TT-11 (Clientes)**: clients, contacts, contracts
- **TT-12 (RH)**: employees, payslips, payroll
- **TT-13 (Financeiro)**: invoices, payments, costs, accounting, contaazul
- **TT-14 (CRM)**: opportunities, campaigns, leads
- **TT-15 (Infraestrutura)**: functions, observability, logs, tenants
- **TT-16 (Configuracoes)**: users, roles, permissions, security

### Passo 2: Criar/Atualizar Model (se necessario)

```python
# backend/app/models/{entity}.py
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class EntityName(Base):
    __tablename__ = "entity_names"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome da entidade"
    )
    tenant_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="ID do tenant (multi-tenancy)"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="Status: 0=Inativo, 1=Ativo"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        comment="Data de criacao"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Data de atualizacao"
    )
```

**Importante**: Sempre incluir `tenant_id` para isolamento multi-tenant.

### Passo 3: Criar Schema Pydantic

```python
# backend/app/schemas/{entity}.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class EntityCreate(BaseModel):
    """Schema para criacao."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome da entidade"
    )
    status: int = Field(
        default=1,
        ge=0,
        le=10,
        description="Status: 0=Inativo, 1=Ativo"
    )

class EntityUpdate(BaseModel):
    """Schema para atualizacao parcial."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Nome da entidade"
    )
    status: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        description="Status: 0=Inativo, 1=Ativo"
    )

class EntityResponse(BaseModel):
    """Schema para response."""
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    status: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
```

### Passo 4: Criar Service

```python
# backend/app/services/{entity}_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.{entity} import EntityName
from app.schemas.{entity} import EntityCreate, EntityUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class EntityService:
    """Servico de gestao de entidades."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[EntityName], int]:
        """
        Lista entidades com paginacao e filtros.

        Args:
            tenant_id: ID do tenant
            skip: Offset para paginacao
            limit: Limite de registros
            search: Termo de busca

        Returns:
            Tupla (lista de entidades, total)
        """
        query = select(EntityName).where(
            EntityName.tenant_id == tenant_id
        )

        if search:
            query = query.where(
                EntityName.name.ilike(f"%{search}%")
            )

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Aplicar paginacao
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return items, total

    async def get_by_id(self, entity_id: int, tenant_id: str) -> EntityName:
        """
        Busca entidade por ID.

        Args:
            entity_id: ID da entidade
            tenant_id: ID do tenant

        Returns:
            Entidade encontrada

        Raises:
            HTTPException: Se nao encontrar (404)
        """
        query = select(EntityName).where(
            EntityName.id == entity_id,
            EntityName.tenant_id == tenant_id,
        )
        result = await self.db.execute(query)
        entity = result.scalar_one_or_none()

        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entidade {entity_id} nao encontrada"
            )

        return entity

    async def create(self, data: EntityCreate, tenant_id: str) -> EntityName:
        """Cria entidade."""
        entity = EntityName(
            **data.model_dump(),
            tenant_id=tenant_id,
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(entity)
        logger.info(f"Entidade criada: {entity.id} (tenant: {tenant_id})")
        return entity

    async def update(
        self, entity_id: int, data: EntityUpdate, tenant_id: str
    ) -> EntityName:
        """Atualiza entidade."""
        entity = await self.get_by_id(entity_id, tenant_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)

        await self.db.commit()
        await self.db.refresh(entity)
        logger.info(f"Entidade atualizada: {entity.id}")
        return entity

    async def delete(self, entity_id: int, tenant_id: str) -> None:
        """Deleta entidade."""
        entity = await self.get_by_id(entity_id, tenant_id)
        await self.db.delete(entity)
        await self.db.commit()
        logger.info(f"Entidade deletada: {entity_id}")
```

### Passo 5: Criar Router

```python
# backend/app/routers/{entity}.py
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user, require_permission
from app.schemas.{entity} import EntityCreate, EntityUpdate, EntityResponse
from app.services.{entity}_service import EntityService
from typing import List, Optional

router = APIRouter(
    prefix="/api/{entities}",
    tags=["{Entities}"],
)

@router.get(
    "",
    response_model=dict,
    summary="Listar entidades",
)
async def list_entities(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(20, ge=1, le=100, description="Limite"),
    search: Optional[str] = Query(None, description="Busca por nome"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Lista entidades com paginacao e filtros."""
    service = EntityService(db)
    items, total = await service.list(
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        search=search,
    )
    return {
        "success": True,
        "data": [EntityResponse.model_validate(i) for i in items],
        "total": total,
    }

@router.get(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Buscar entidade por ID",
)
async def get_entity(
    entity_id: int = Path(..., description="ID da entidade"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> EntityResponse:
    """Retorna dados de uma entidade especifica."""
    service = EntityService(db)
    return await service.get_by_id(entity_id, current_user.tenant_id)

@router.post(
    "",
    response_model=EntityResponse,
    status_code=201,
    summary="Criar entidade",
)
async def create_entity(
    data: EntityCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> EntityResponse:
    """Cria uma nova entidade."""
    service = EntityService(db)
    return await service.create(data, current_user.tenant_id)

@router.put(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Atualizar entidade",
)
async def update_entity(
    entity_id: int = Path(..., description="ID da entidade"),
    data: EntityUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> EntityResponse:
    """Atualiza dados de uma entidade."""
    service = EntityService(db)
    return await service.update(entity_id, data, current_user.tenant_id)

@router.delete(
    "/{entity_id}",
    status_code=204,
    summary="Deletar entidade",
)
async def delete_entity(
    entity_id: int = Path(..., description="ID da entidade"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Deleta uma entidade."""
    service = EntityService(db)
    await service.delete(entity_id, current_user.tenant_id)
```

### Passo 6: Registrar Router no main.py

```python
# backend/app/main.py
from app.routers.{entity} import router as entity_router

app.include_router(entity_router)
```

Verificar se ja existe um padrao de registro em `backend/app/main.py` e seguir o mesmo.

## Convencoes

### Imports do Projeto TMF

```python
# Database
from app.database import Base, get_db

# Auth
from app.auth.dependencies import get_current_user, require_permission

# Config
from app.config import settings

# Models
from app.models.{entity} import EntityName

# Schemas
from app.schemas.{entity} import EntityCreate, EntityUpdate, EntityResponse

# Services
from app.services.{entity}_service import EntityService
```

### Padroes de Response

```python
# Listagem com paginacao
{
    "success": True,
    "data": [...],
    "total": 42
}

# Item unico
{
    "id": 1,
    "name": "...",
    ...
}

# Erro
{
    "detail": "Mensagem de erro"
}
```

### Multi-Tenancy

**CRITICO**: Sempre filtrar por `tenant_id` do usuario autenticado:
```python
# CORRETO - usa tenant do usuario
tenant_id=current_user.tenant_id

# INCORRETO - confia no request
tenant_id=request.query_params.get("tenant_id")
```

### Permissoes

```python
# Endpoint protegido por permissao
@router.get("/admin")
async def admin_only(
    user = Depends(require_permission("admin:access"))
):
    pass
```

## Porta do Backend

- **Desenvolvimento**: http://localhost:11000
- **Swagger/Docs**: http://localhost:11000/docs
- **ReDoc**: http://localhost:11000/redoc

## Exemplo de Uso

```bash
/api-endpoint Criar CRUD de campanhas para o modulo CRM
/api-endpoint Adicionar endpoint de exportacao de relatorio financeiro
/api-endpoint Criar endpoint para sincronizacao ContaAzul
```
