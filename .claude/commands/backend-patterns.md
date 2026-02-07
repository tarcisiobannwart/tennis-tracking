# Backend Patterns - Tennis Tracking

Guia completo de padroes e convencoes para o backend Python/FastAPI do Tennis Tracking. Este documento serve como referencia obrigatoria ao criar ou modificar codigo backend.

> **NOTA**: O Tennis Tracking usa **MongoDB + Motor** (async). Exemplos SQLAlchemy neste documento devem ser adaptados para MongoDB. Consulte `backend/app/services/` e `backend/app/models/`.

## Arquitetura

```
backend/app/
├── main.py              # Entry point FastAPI, registro de routers, middleware, lifespan
├── config.py            # Pydantic Settings (le de .env)
├── database.py          # SQLAlchemy async engine, session factory, get_db()
├── auth/                # Autenticacao e autorizacao
│   ├── dependencies.py  # get_current_user, require_permission, require_ceo
│   ├── service.py       # AuthService (JWT, password hashing)
│   └── utils.py         # Utilitarios de autenticacao
├── models/              # SQLAlchemy ORM models
│   ├── base.py          # Base declarative, TimestampMixin
│   ├── user.py          # User, Role, Permission
│   ├── tenant.py        # Tenant, TenantSecrets, TenantToken
│   ├── person.py        # Person (pessoas/funcionarios)
│   ├── crm.py           # Opportunity, Contact
│   ├── integration.py   # Integration configs
│   └── ...              # Demais models
├── schemas/             # Pydantic validation (request/response)
│   └── [matching models]
├── services/            # Business logic e integracoes externas
│   └── [um service por dominio]
├── routers/             # FastAPI endpoints (thin layer)
│   └── [um router por dominio]
└── scripts/             # Utilitarios CLI
    └── [scripts de setup, migracao, etc]
```

## Models (SQLAlchemy)

### Estrutura Obrigatoria

```python
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Client(Base, TimestampMixin):
    """Model para clientes/tenants do sistema."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    document: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="client", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}')>"
```

### TimestampMixin

O projeto usa `TimestampMixin` definido em `app/models/base.py` para campos `created_at` e `updated_at`:

```python
from app.models.base import Base, TimestampMixin

class MyModel(Base, TimestampMixin):
    __tablename__ = "my_table"
    # created_at e updated_at sao adicionados automaticamente
```

### Regras de Models

| Regra | Correto | Incorreto |
|-------|---------|-----------|
| Type hints | `id: Mapped[int] = mapped_column(Integer, ...)` | `id = Column(Integer, ...)` |
| Tablename | `__tablename__ = "clients"` | Sem `__tablename__` |
| Imports | `from app.models.base import Base` | `from sqlalchemy.ext.declarative import declarative_base` |
| Nullable | `Mapped[Optional[str]]` para campos nullable | `Mapped[str]` para campo que pode ser NULL |
| Indexes | `index=True` em campos de busca frequente | Sem index em campos de filtro |
| Timestamps | Herdar de `TimestampMixin` | Criar campos `created_at` manualmente |
| Repr | Implementar `__repr__` | Sem representacao string |
| Docstring | Docstring descrevendo o model | Sem documentacao |
| Tenant | `tenant_id` obrigatorio em models multi-tenant | Sem `tenant_id` |
| Relationships | `lazy="selectin"` para evitar N+1 | `lazy="joined"` ou sem lazy |

### Model com Enum

```python
import enum
from sqlalchemy import Enum

class ClientStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    status: Mapped[ClientStatus] = mapped_column(
        Enum(ClientStatus), default=ClientStatus.ACTIVE, nullable=False
    )
```

## Schemas (Pydantic)

### Estrutura Base

```python
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ClientBase(BaseModel):
    """Schema base para Client."""
    name: str = Field(..., min_length=2, max_length=255, description="Nome do cliente")
    document: Optional[str] = Field(None, max_length=20, description="CPF ou CNPJ")
    email: Optional[str] = Field(None, description="Email de contato")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    notes: Optional[str] = Field(None, description="Observacoes")


class ClientCreate(ClientBase):
    """Schema para criacao de Client."""
    tenant_id: str = Field(..., description="ID do tenant")

    @field_validator("document")
    @classmethod
    def validate_document(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) not in (11, 14):
            raise ValueError("Documento deve ter 11 (CPF) ou 14 (CNPJ) digitos")
        return v


class ClientUpdate(BaseModel):
    """Schema para atualizacao parcial de Client."""
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Nome do cliente")
    document: Optional[str] = Field(None, max_length=20, description="CPF ou CNPJ")
    email: Optional[str] = Field(None, description="Email de contato")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    notes: Optional[str] = Field(None, description="Observacoes")
    is_active: Optional[bool] = Field(None, description="Status ativo/inativo")


class ClientResponse(ClientBase):
    """Schema de resposta para Client."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### Paginacao

O projeto usa schemas padrao de paginacao para endpoints que retornam listas:

```python
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parametros de paginacao recebidos via query string."""
    page: int = Field(1, ge=1, description="Numero da pagina (1-based)")
    per_page: int = Field(20, ge=1, le=100, description="Itens por pagina (max 100)")
    search: Optional[str] = Field(None, description="Termo de busca")
    sort_by: Optional[str] = Field(None, description="Campo de ordenacao")
    sort_order: Optional[str] = Field("asc", description="Direcao: asc ou desc")


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada generica."""
    items: List[T]
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Pagina atual")
    per_page: int = Field(..., description="Itens por pagina")
    pages: int = Field(..., description="Total de paginas")

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
```

### Regras de Schemas

| Regra | Correto | Incorreto |
|-------|---------|-----------|
| Field description | `Field(..., description="Nome do cliente")` | `Field(...)` sem description |
| from_attributes | Em Response schemas: `ConfigDict(from_attributes=True)` | Ausente em Response |
| Separacao | Create/Update/Response schemas separados | Schema unico para tudo |
| Validacao | `field_validator` para regras de negocio | Sem validacao |
| Optional | `Optional[str] = Field(None, ...)` para campos opcionais | `str = Field(None, ...)` |
| Docstring | Docstring descrevendo o schema | Sem documentacao |
| Update parcial | Todos os campos `Optional` em Update schemas | Campos obrigatorios em Update |
| Tipos | Usar tipos corretos (int, str, datetime) | Tudo como `str` |

## Services (Business Logic)

### Estrutura Padrao

```python
import logging
from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, PaginationParams

logger = logging.getLogger(__name__)


class ClientService:
    """Service para operacoes de clientes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, client_id: int, tenant_id: str) -> Client:
        """Busca cliente por ID com validacao de tenant."""
        query = select(Client).where(
            Client.id == client_id,
            Client.tenant_id == tenant_id
        )
        result = await self.db.execute(query)
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente {client_id} nao encontrado"
            )

        return client

    async def list(
        self,
        tenant_id: str,
        params: PaginationParams
    ) -> Tuple[List[Client], int]:
        """Lista clientes com paginacao e filtros."""
        query = select(Client).where(Client.tenant_id == tenant_id)

        # Busca por texto
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Client.name.ilike(search_term),
                    Client.email.ilike(search_term),
                    Client.document.ilike(search_term),
                )
            )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Ordenacao
        if params.sort_by:
            column = getattr(Client, params.sort_by, None)
            if column:
                if params.sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        else:
            query = query.order_by(Client.created_at.desc())

        # Paginacao
        offset = (params.page - 1) * params.per_page
        query = query.offset(offset).limit(params.per_page)

        result = await self.db.execute(query)
        clients = list(result.scalars().all())

        return clients, total

    async def create(self, data: ClientCreate) -> Client:
        """Cria novo cliente."""
        # Validar unicidade do documento
        if data.document:
            existing = await self._get_by_document(data.document, data.tenant_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Documento {data.document} ja cadastrado"
                )

        client = Client(**data.model_dump())
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)

        logger.info(f"Cliente criado: {client.id} - {client.name}")
        return client

    async def update(self, client_id: int, data: ClientUpdate, tenant_id: str) -> Client:
        """Atualiza cliente existente."""
        client = await self.get_by_id(client_id, tenant_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        await self.db.commit()
        await self.db.refresh(client)

        logger.info(f"Cliente atualizado: {client.id}")
        return client

    async def delete(self, client_id: int, tenant_id: str) -> None:
        """Remove cliente (soft delete)."""
        client = await self.get_by_id(client_id, tenant_id)
        client.is_active = False
        await self.db.commit()

        logger.info(f"Cliente desativado: {client.id}")

    async def _get_by_document(self, document: str, tenant_id: str) -> Optional[Client]:
        """Busca cliente por documento (interno)."""
        query = select(Client).where(
            Client.document == document,
            Client.tenant_id == tenant_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
```

### Regras de Services

| Regra | Correto | Incorreto |
|-------|---------|-----------|
| Async | `async def get_by_id(self, ...)` | `def get_by_id(self, ...)` |
| Await | `await self.db.execute(query)` | `self.db.execute(query)` |
| DI | `def __init__(self, db: AsyncSession)` | DB global ou import direto |
| Tenant | Sempre filtrar por `tenant_id` | Query sem filtro de tenant |
| Logger | `logger.info(...)` | `print(...)` |
| HTTP Exceptions | `raise HTTPException(status_code=404, ...)` | `return None` sem tratamento |
| Type hints | Todos os parametros e retornos tipados | Sem type hints |
| Docstrings | Em todas as funcoes publicas | Sem documentacao |
| Metodos privados | Prefixo `_` para metodos internos | Metodo interno como publico |
| Commit | `await self.db.commit()` com `await self.db.refresh()` | Commit sem refresh |

### Tratamento de Erros no Service

```python
from fastapi import HTTPException, status


class ClientService:

    async def get_by_id(self, client_id: int, tenant_id: str) -> Client:
        """Busca com tratamento de erro padronizado."""
        client = ...  # query

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente {client_id} nao encontrado"
            )

        if client.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este recurso"
            )

        return client

    async def create(self, data: ClientCreate) -> Client:
        """Criacao com validacao de conflito."""
        existing = await self._get_by_document(data.document, data.tenant_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Documento {data.document} ja cadastrado"
            )

        try:
            client = Client(**data.model_dump())
            self.db.add(client)
            await self.db.commit()
            await self.db.refresh(client)
            return client
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Erro ao criar cliente: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar cliente"
            )
```

## Routers (FastAPI Endpoints)

### Estrutura Padrao

```python
import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.auth.dependencies import get_current_user, require_permission
from app.models.user import User
from app.schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse,
    PaginationParams, PaginatedResponse
)
from app.services.client_service import ClientService

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    page: int = Query(1, ge=1, description="Pagina"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por pagina"),
    search: Optional[str] = Query(None, description="Termo de busca"),
    sort_by: Optional[str] = Query(None, description="Campo de ordenacao"),
    sort_order: Optional[str] = Query("asc", description="Direcao: asc/desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("clients:view")),
):
    """Lista clientes do tenant com paginacao."""
    params = PaginationParams(
        page=page,
        per_page=per_page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    service = ClientService(db)
    clients, total = await service.list(current_user.tenant_id, params)

    return PaginatedResponse(
        items=clients,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page) if total > 0 else 1
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("clients:view")),
):
    """Busca cliente por ID."""
    service = ClientService(db)
    return await service.get_by_id(client_id, current_user.tenant_id)


@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("clients:create")),
):
    """Cria novo cliente."""
    data.tenant_id = current_user.tenant_id
    service = ClientService(db)
    return await service.create(data)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("clients:edit")),
):
    """Atualiza cliente existente."""
    service = ClientService(db)
    return await service.update(client_id, data, current_user.tenant_id)


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("clients:delete")),
):
    """Remove cliente (soft delete)."""
    service = ClientService(db)
    await service.delete(client_id, current_user.tenant_id)
```

### Registrando Router no main.py

```python
# backend/app/main.py
from app.routers.clients import router as clients_router

app.include_router(clients_router)
```

### Regras de Routers

| Regra | Correto | Incorreto |
|-------|---------|-----------|
| response_model | `response_model=ClientResponse` | Sem response_model |
| Depends | `db: AsyncSession = Depends(get_db)` | DB diretamente |
| Service | `service = ClientService(db)` | Logica de negocio no endpoint |
| Permission | `Depends(require_permission("clients:view"))` | Sem verificacao de permissao |
| Tenant | Usar `current_user.tenant_id` | Confiar em tenant_id do request |
| Status code | `status_code=201` para POST, `204` para DELETE | 200 para tudo |
| Docstring | Descricao do endpoint | Sem documentacao |
| Prefix | `/api/` prefix | Sem prefix padrao |
| Tags | `tags=["Clients"]` | Sem tags |
| Query params | `Query(1, ge=1, description="...")` | Parametros sem validacao |

## Errors (Custom Exceptions)

### Excecoes Customizadas

```python
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Recurso nao encontrado."""
    def __init__(self, resource: str, resource_id: int | str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} {resource_id} nao encontrado"
        )


class ConflictException(HTTPException):
    """Conflito (recurso ja existe)."""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class ForbiddenException(HTTPException):
    """Acesso negado."""
    def __init__(self, message: str = "Acesso negado"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class ValidationException(HTTPException):
    """Erro de validacao de negocio."""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )
```

### Uso no Service

```python
from app.errors import NotFoundException, ConflictException

class ClientService:

    async def get_by_id(self, client_id: int, tenant_id: str) -> Client:
        client = ...  # query
        if not client:
            raise NotFoundException("Cliente", client_id)
        return client

    async def create(self, data: ClientCreate) -> Client:
        existing = await self._get_by_document(data.document, data.tenant_id)
        if existing:
            raise ConflictException(f"Documento {data.document} ja cadastrado")
        ...
```

### Mapeamento de Status HTTP

| Situacao | Status Code | Classe |
|----------|-------------|--------|
| Recurso nao encontrado | 404 | `NotFoundException` |
| Recurso ja existe | 409 | `ConflictException` |
| Sem permissao | 403 | `ForbiddenException` |
| Dados invalidos (negocio) | 422 | `ValidationException` |
| Dados invalidos (formato) | 422 | Pydantic automatico |
| Nao autenticado | 401 | `get_current_user` automatico |
| Erro interno | 500 | Exception handler global |

## Autenticacao e Autorizacao

### Dependencies Disponiveis

```python
from app.auth.dependencies import (
    get_current_user,        # Retorna User autenticado ou 401
    require_permission,       # Verifica permissao especifica
    require_any_permission,   # Verifica se tem alguma das permissoes
    require_role_level,       # Verifica nivel minimo de role
    require_ceo,              # Restringe a CEO apenas
    get_optional_user,        # Retorna User ou None (nao falha)
    get_ceo_user,             # Convenience: require_ceo()
)
```

### Exemplos de Uso

```python
# Endpoint que requer autenticacao
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Endpoint que requer permissao especifica
@router.get("/clients")
async def list_clients(
    current_user: User = Depends(require_permission("clients:view"))
):
    ...

# Endpoint que requer qualquer uma das permissoes
@router.get("/reports")
async def get_reports(
    current_user: User = Depends(require_any_permission(["reports:view", "admin:access"]))
):
    ...

# Endpoint exclusivo para CEO
@router.get("/admin/settings")
async def admin_settings(
    current_user: User = Depends(get_ceo_user)
):
    ...

# Endpoint publico (sem autenticacao)
@router.get("/health")
async def health():
    return {"status": "ok"}

# Endpoint com autenticacao opcional
@router.get("/public-data")
async def public_data(
    current_user: Optional[User] = Depends(get_optional_user)
):
    if current_user:
        # Retorna dados extras para autenticados
        ...
    return {"data": "publico"}
```

## Database Patterns

### Queries Comuns

```python
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import selectinload


# Busca simples
query = select(Client).where(Client.id == client_id)
result = await self.db.execute(query)
client = result.scalar_one_or_none()

# Busca com filtros multiplos
query = select(Client).where(
    and_(
        Client.tenant_id == tenant_id,
        Client.is_active == True,
        Client.status == ClientStatus.ACTIVE
    )
)

# Busca com OR
query = select(Client).where(
    or_(
        Client.name.ilike(f"%{search}%"),
        Client.email.ilike(f"%{search}%")
    )
)

# Contagem
count_query = select(func.count()).select_from(
    select(Client).where(Client.tenant_id == tenant_id).subquery()
)
total = (await self.db.execute(count_query)).scalar_one()

# Ordenacao
query = query.order_by(desc(Client.created_at))

# Paginacao
query = query.offset((page - 1) * per_page).limit(per_page)

# Eager loading de relationships
query = select(Client).options(
    selectinload(Client.contacts)
).where(Client.id == client_id)

# Lista de resultados
result = await self.db.execute(query)
items = list(result.scalars().all())

# Resultado unico
result = await self.db.execute(query)
item = result.scalar_one_or_none()
```

### Transacoes

```python
# Operacao simples (auto-commit via session)
client = Client(**data.model_dump())
self.db.add(client)
await self.db.commit()
await self.db.refresh(client)

# Operacao com rollback explicito
try:
    self.db.add(client)
    self.db.add(contact)
    await self.db.commit()
except Exception:
    await self.db.rollback()
    raise
```

## Anti-Patterns a Evitar

### Python/FastAPI

```python
# =========================================
# SQL Injection - NUNCA fazer isso
# =========================================
await db.execute(f"SELECT * FROM clients WHERE id = {id}")        # ERRADO
await db.execute(text(f"SELECT * FROM clients WHERE name = '{name}'"))  # ERRADO

# Correto: usar ORM
query = select(Client).where(Client.id == id)                     # CORRETO
await db.execute(query)


# =========================================
# Funcao sync em service async - NUNCA
# =========================================
def get_client(self, id: int):                    # ERRADO - sync
    return self.db.query(Client).filter(...).first()

async def get_client(self, id: int) -> Client:    # CORRETO - async
    result = await self.db.execute(select(Client).where(Client.id == id))
    return result.scalar_one_or_none()


# =========================================
# Await faltando - NUNCA
# =========================================
result = self.db.execute(query)                    # ERRADO - sem await
result = await self.db.execute(query)              # CORRETO


# =========================================
# Business logic no endpoint - NUNCA
# =========================================
@router.post("/clients")
async def create_client(data: ClientCreate, db = Depends(get_db)):
    # 50 linhas de logica aqui...                   # ERRADO
    existing = await db.execute(select(Client).where(...))
    if existing.scalar():
        raise HTTPException(409, "...")
    client = Client(**data.model_dump())
    db.add(client)
    await db.commit()
    # mais logica...

# CORRETO - delegar para service
@router.post("/clients")
async def create_client(data: ClientCreate, db = Depends(get_db)):
    service = ClientService(db)
    return await service.create(data)


# =========================================
# Print ao inves de logger - NUNCA
# =========================================
print(f"Creating client: {data}")                  # ERRADO
logger.info(f"Creating client: {data.name}")       # CORRETO


# =========================================
# Confiar em tenant_id do request - NUNCA
# =========================================
@router.get("/clients")
async def list_clients(tenant_id: str):            # ERRADO - tenant do request
    ...

@router.get("/clients")
async def list_clients(
    current_user: User = Depends(get_current_user)  # CORRETO - tenant do user
):
    tenant_id = current_user.tenant_id
    ...


# =========================================
# Bare except - NUNCA
# =========================================
try:
    await service.create(data)
except:                                            # ERRADO - bare except
    pass

try:
    await service.create(data)
except ValueError as e:                            # CORRETO - except especifico
    raise HTTPException(422, str(e))


# =========================================
# Import circular - NUNCA
# =========================================
# Em models/client.py
from app.services.client_service import ClientService  # ERRADO

# Models NUNCA importam services. Services importam models.


# =========================================
# DB global - NUNCA
# =========================================
db = AsyncSessionLocal()                           # ERRADO - sessao global

# CORRETO - usar dependency injection
def __init__(self, db: AsyncSession):
    self.db = db


# =========================================
# Response sem model - EVITAR
# =========================================
@router.get("/clients")
async def list_clients(...):                       # ERRADO - sem response_model
    return clients

@router.get("/clients", response_model=list[ClientResponse])
async def list_clients(...):                       # CORRETO
    return clients
```

## Checklist de Validacao

Use esta checklist ao criar ou revisar codigo backend.

### Model

- [ ] Herda de `Base` e `TimestampMixin`
- [ ] Usa `Mapped[type]` com `mapped_column()`
- [ ] Tem `__tablename__` definido
- [ ] Tem `tenant_id` (se multi-tenant)
- [ ] Campos importantes com `index=True`
- [ ] `__repr__` implementado
- [ ] Docstring presente
- [ ] Relationships com `lazy="selectin"`
- [ ] Nullable correto (`Optional` vs obrigatorio)

### Schema

- [ ] `Field()` com `description=` em todos os campos
- [ ] Response schema tem `ConfigDict(from_attributes=True)`
- [ ] Schemas separados: Create / Update / Response
- [ ] `field_validator` para validacoes de negocio
- [ ] Update schema com todos os campos `Optional`
- [ ] Docstring descritivo em cada schema
- [ ] Tipos corretos (nao tudo como `str`)

### Service

- [ ] Todas as funcoes sao `async def`
- [ ] Usa `await` em todas as operacoes de I/O
- [ ] Injecao de dependencia via `__init__(self, db: AsyncSession)`
- [ ] Filtro por `tenant_id` em todas as queries
- [ ] Tratamento de erros com `HTTPException` ou excecoes customizadas
- [ ] `logger` ao inves de `print`
- [ ] Docstrings em todas as funcoes publicas
- [ ] Type hints em parametros e retornos
- [ ] `await self.db.commit()` seguido de `await self.db.refresh()`
- [ ] Metodos internos com prefixo `_`

### Router

- [ ] `response_model=` em todos os endpoints GET/POST/PUT
- [ ] `Depends(get_db)` para sessao do banco
- [ ] `Depends(require_permission(...))` ou `Depends(get_current_user)`
- [ ] Delega logica para Service (endpoint thin)
- [ ] `status_code=201` para POST de criacao
- [ ] `status_code=204` para DELETE
- [ ] Docstring em cada endpoint
- [ ] Prefixo `/api/` no router
- [ ] `tags=["NomeDoModulo"]` para documentacao Swagger
- [ ] Query params com `Query()` e validacoes
- [ ] Nunca confia em `tenant_id` do request body

### Geral

- [ ] Sem SQL injection (usa ORM)
- [ ] Sem `print()` (usa `logger`)
- [ ] Sem funcoes sync em contexto async
- [ ] Sem import circular (models nao importam services)
- [ ] Sem bare `except:`
- [ ] Sem DB global (usa DI)
- [ ] Sem dados sensiveis em logs (senhas, tokens)
- [ ] Migration SQL criada para novos campos/tabelas
