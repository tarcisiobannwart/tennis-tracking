# Comando: Validar Backend Python

Valida se o codigo Python segue os padroes de arquitetura e boas praticas do Tennis Tracking.

> **NOTA**: O Tennis Tracking usa **MongoDB + Motor** (async). Validacoes SQLAlchemy devem ser adaptadas para MongoDB patterns.

## Integracao com Jira

Quando problemas sao encontrados:
1. Perguntar se deseja criar issue no Jira (rastreabilidade)
2. Se sim, criar issue via `/create-jira`
3. Executar correcao automatica
4. Commit vinculado a issue
5. Issue movida para Done automaticamente

## Instrucoes

Arquivo/pasta a validar: `$ARGUMENTS`
- Se vazio: valida arquivos modificados (git diff)
- Se informado: valida arquivo ou pasta especifica

## Regras de Validacao

### CRITICO (bloqueia commit)

| ID | Regra | Descricao |
|----|-------|-----------|
| PC01 | Funcao sync com DB | Services devem ser `async def` |
| PC02 | Await faltando | Todas chamadas async precisam de `await` |
| PC03 | SQL injection | Usar ORM, nao strings formatadas |
| PC04 | Credencial hardcoded | Usar settings/environment |
| PC05 | Business logic em route | Logica deve estar nos services |
| PC06 | Catch generico | Nao usar `except Exception:` |

### ALTO (warning)

| ID | Regra | Descricao |
|----|-------|-----------|
| PA01 | Type hint faltando | Todas funcoes precisam type hints |
| PA02 | Docstring faltando | Funcoes publicas precisam docstring |
| PA03 | Field sem description | Schemas precisam Field com description |
| PA04 | Schema sem from_attributes | Response schemas precisam `from_attributes=True` |
| PA05 | Import nao organizado | Separar stdlib/third-party/local |
| PA06 | Return tuple em service | Usar exceptions, nao tuples |

### MEDIO (sugestao)

| ID | Regra | Descricao |
|----|-------|-----------|
| PM01 | Logger print | Usar `logger` nao `print` |
| PM02 | Magic number | Usar enums/constantes |
| PM03 | Nome nao descritivo | Nomes devem ser claros |
| PM04 | Comentario TODO | Resolver ou criar issue |

## Validacoes por Tipo de Arquivo

### Models (`backend/app/models/*.py`)

```python
# CORRETO
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome do cliente"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="Status: 0=Inativo, 1=Ativo"
    )

    # Relationships com TYPE_CHECKING
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact",
        back_populates="client",
        lazy="selectin",
    )

# INCORRETO
class Client(Base):
    id = Column(Integer, primary_key=True)  # Sem Mapped[]
    name = Column(String(255))               # Sem type hint
    # Sem __tablename__
    # Sem comment
```

### Schemas (`backend/app/schemas/*.py`)

```python
# CORRETO
from pydantic import BaseModel, Field, ConfigDict

class ClientCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome do cliente"
    )
    status: int = Field(
        default=1,
        ge=0,
        le=10,
        description="Status: 0=Inativo, 1=Ativo"
    )

class ClientResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # OBRIGATORIO para Response
    )

    id: int
    name: str
    status: int

# INCORRETO
class ClientCreate(BaseModel):
    name: str  # Sem Field
    status: int = 1  # Sem description

class ClientResponse(BaseModel):
    # Sem from_attributes - nao converte ORM
    id: int
```

### Services (`backend/app/services/*.py`)

```python
# CORRETO
from sqlalchemy.ext.asyncio import AsyncSession

class ClientService:
    """Servico de gestao de clientes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, client_id: int) -> Client:
        """
        Busca cliente por ID.

        Args:
            client_id: ID do cliente

        Returns:
            Cliente encontrado

        Raises:
            ClientNotFoundError: Se nao encontrar
        """
        query = select(Client).where(Client.id == client_id)
        result = await self.db.execute(query)
        client = result.scalar_one_or_none()

        if not client:
            raise ClientNotFoundError(client_id=client_id)

        return client

    async def create(self, data: ClientCreate, user_id: int) -> Client:
        """Cria cliente."""
        client = Client(**data.model_dump())
        self.db.add(client)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(client)
        return client

# INCORRETO
class ClientService:
    def __init__(self, db):  # Sem type hint
        self.db = db

    def get_by_id(self, id):  # Sync! Sem type hints
        # SQL injection!
        result = self.db.execute(f"SELECT * FROM clients WHERE id = {id}")
        return result

    async def create(self, data):
        try:
            # ...
        except Exception:  # Catch generico
            return None, "Erro"  # Return tuple
```

### Routers (`backend/app/routers/*.py`)

```python
# CORRETO
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user, require_permission

router = APIRouter()

@router.get(
    "/clients/{client_id}",
    response_model=ClientResponse,
    summary="Buscar cliente por ID",
)
async def get_client(
    client_id: int = Path(..., description="ID do cliente"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> ClientResponse:
    """
    Retorna dados de um cliente especifico.

    - **client_id**: ID unico do cliente
    """
    service = ClientService(db)
    return await service.get_by_id(client_id)

# INCORRETO
@router.get("/clients/{id}")  # Sem response_model, sem summary
async def get_client(id: int, db = Depends(get_db)):  # Sem type hints
    # Business logic no route!
    query = select(Client).where(Client.id == id)
    result = await db.execute(query)
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(404)  # Deveria ser exception customizada
    return client
```

## Padroes de Busca (Regex)

```python
# PC01: Funcao sync em service
/class\s+\w+Service[\s\S]*?def\s+(get|create|update|delete|list)\w*\s*\([^)]*\):/

# PC02: Await faltando
/self\.db\.(execute|flush|commit|refresh)\s*\((?!.*await)/

# PC03: SQL com f-string
/execute\s*\(\s*f["'][^"']*\{/

# PC04: Credenciais hardcoded
/(password|secret|api_key|token)\s*=\s*["'][^"']+["']/i

# PC06: Catch generico
/except\s+Exception\s*:/

# PA01: Funcao sem type hints
/def\s+\w+\s*\([^)]*\)\s*:/  # Sem -> return type

# PA03: Field sem description
/Field\s*\([^)]*\)(?![^)]*description\s*=)/

# PM01: Print statement
/print\s*\(/
```

## Processo de Validacao

### Passo 1: Identificar Arquivos

```bash
git diff --name-only HEAD | grep -E '\.py$' | grep -E 'backend/app/' | grep -vE '(__pycache__|tests/)'
```

### Passo 2: Classificar por Tipo

| Path Pattern | Tipo | Validacoes |
|--------------|------|------------|
| `backend/app/models/*.py` | Model | PC01, PA01, tablename, Mapped |
| `backend/app/schemas/*.py` | Schema | PA03, PA04, Field |
| `backend/app/services/*.py` | Service | PC01-06, PA01-02, PA06 |
| `backend/app/routers/*.py` | Router | PC05, PA01, response_model |

### Passo 3: Gerar Relatorio

```
RELATORIO DE VALIDACAO - Python Backend Tennis Tracking
============================================================

Arquivo: backend/app/services/client_service.py (Service)

CRITICO (1 problema)
|- PC01: Linha 45 - Funcao sync com DB
        def get_by_id(self, id):
        Correcao: async def get_by_id(self, id: int) -> Client:

ALTO (2 problemas)
|- PA01: Linha 45 - Type hints faltando
|- PA02: Linha 45 - Docstring faltando

============================================================
RESUMO: 1 criticos | 2 altos | 0 medios
VALIDACAO FALHOU
```

## Integracao com /commit

Quando chamado pelo comando `/commit`:
1. Validar arquivos .py modificados
2. Se CRITICOS > 0: bloquear commit
3. Se apenas ALTOS: warning, permitir com confirmacao
4. Se apenas MEDIOS: informativo, permitir commit

## Modo Automatico (--auto-fix)

Correcoes automaticas disponiveis:
- Reorganizar imports (isort)
- Substituir `print` por `logger`
- Adicionar `model_config` basico em schemas

## Mapeamento de Epics

| Modulo Backend | Epic Jira |
|----------------|-----------|
| routers/clients.py, services/client_service.py | TT-11 (Clientes) |
| routers/hr.py, services/payroll_service.py | TT-12 (RH) |
| routers/accounting.py, routers/costs.py | TT-13 (Financeiro) |
| services/contaazul_service.py | TT-13 (Financeiro) |
| routers/jira.py, services/jira_service.py | TT-14 (CRM) |
| routers/functions.py, services/faas_service.py | TT-15 (Infraestrutura) |
| routers/observability.py, services/grafana_service.py | TT-15 (Infraestrutura) |
| routers/users.py, routers/auth.py | TT-16 (Configuracoes) |

## Exemplo de Uso

```bash
/validate-backend                                    # Valida arquivos modificados
/validate-backend backend/app/services/client_service.py  # Valida arquivo especifico
/validate-backend backend/app/                       # Valida pasta
/validate-backend --auto-fix                         # Corrige automaticamente
```
