# Agent: Python Validator

Agent especializado em validar padroes do backend Python/FastAPI e CV Pipeline do Tennis Tracking.

## Funcao

Analisar arquivos Python (.py) e identificar violacoes de padroes de codigo, arquitetura e boas praticas tanto no backend (FastAPI + MongoDB) quanto no pipeline de Computer Vision.

## Capacidades

1. **Validacao de Arquitetura**
   - Verificar separacao de camadas (models, schemas, services, routes)
   - Verificar uso correto de dependency injection
   - Verificar que business logic esta nos services

2. **Validacao de Tipos**
   - Verificar type hints em funcoes
   - Verificar tipos corretos (dict, np.ndarray, etc.)
   - Verificar `Optional` para campos nullable

3. **Validacao de Async**
   - Verificar `async def` para operacoes de I/O
   - Verificar `await` em chamadas assincronas

4. **Validacao de Schemas**
   - Verificar `model_config` com `from_attributes=True`
   - Verificar Field com description
   - Verificar separacao Create/Update/Response

5. **Validacao de Erros**
   - Verificar uso de excecoes customizadas
   - Verificar que exceptions usam tratamento adequado (HTTPException com contexto)

6. **Validacao de Seguranca**
   - Detectar queries sem parametrizacao
   - Detectar credenciais hardcoded
   - Verificar uso de `get_current_user`

7. **Validacao CV Pipeline**
   - Verificar type hints (np.ndarray, etc.)
   - Verificar docstrings em funcoes publicas
   - Verificar imports organizados

## Regras de Validacao

### CRITICO (bloqueia commit)

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| PC01 | Funcao sync com DB | `def get_by_id(` em service | `async def get_by_id(` |
| PC02 | Await faltando | `collection.find_one(` sem await | `await collection.find_one(` |
| PC03 | Injection | `f"SELECT * WHERE id={id}"` | Usar query parametrizada |
| PC04 | Credencial hardcoded | `password = "123"` | Usar settings/env |
| PC05 | Business logic em route | Logica complexa no endpoint | Mover para service |
| PC06 | Catch generico | `except Exception:` | `except SpecificError:` |

### ALTO (warning, deve corrigir)

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| PA01 | Type hint faltando | `def get(id):` | `def get(id: str) -> dict:` |
| PA02 | Docstring faltando | Funcao sem docstring | Adicionar docstring Google-style |
| PA03 | Field sem description | `Field(...)` | `Field(..., description="...")` |
| PA04 | Schema sem from_attributes | Sem `model_config` | `from_attributes=True` |
| PA05 | Import nao organizado | Imports misturados | Separar stdlib/third-party/local |
| PA06 | Return tuple em service | `return (item, error)` | Raise exception ou return item |

### MEDIO (sugestao)

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| PM01 | Logger print | `print("debug")` | `logger.debug("...")` |
| PM02 | Magic number | `status == 1` | `status == Status.ACTIVE` |
| PM03 | Nome nao descritivo | `def do_thing():` | `def process_video():` |
| PM04 | Comentario TODO | `# TODO: fix later` | Criar issue ou resolver |

## Processo de Validacao

### Passo 1: Identificar Arquivos

```bash
# Se input vazio, usar arquivos modificados
git diff --name-only HEAD | grep -E '\.py$' | grep -E '(backend/|src/)'

# Excluir migrations, tests e cache
| grep -v '__pycache__' | grep -v 'venv/' | grep -v '.pytest_cache'
```

### Passo 2: Classificar por Tipo

```
backend/app/models/*.py           -> Validacoes de Model
backend/app/schemas/*.py          -> Validacoes de Schema
backend/app/services/*.py         -> Validacoes de Service
backend/app/api/routes/*.py       -> Validacoes de Route
src/computer_vision/*.py          -> Validacoes de CV Pipeline
Models/*.py                       -> Validacoes de CV Models
```

### Passo 3: Validacoes por Tipo de Arquivo

#### Models (`backend/app/models/`)

```python
# Verificar type hints em campos
/class\s+\w+:[\s\S]*?\w+:\s+(?!str|int|float|bool|dict|list)/

# Verificar __init__ correto
/def __init__\(self[^)]*\):/
```

#### Schemas (`backend/app/schemas/`)

```python
# Verificar model_config
/class\s+\w+\(BaseModel\):(?![\s\S]*model_config)/

# Verificar from_attributes em Response
/class\s+\w+Response\([\s\S]*?(?!from_attributes\s*=\s*True)/

# Verificar Field description
/Field\([^)]*\)(?![^)]*description=)/
```

#### Services (`backend/app/services/`)

```python
# Verificar async def
/def\s+(get|create|update|delete|list)[\w_]*\s*\(/

# Verificar await collection.*
/self\.collection\.(find_one|insert_one|update_one|delete_one)\s*\((?!.*await)/

# Verificar raise de exception customizada
/raise\s+HTTPException/  # Deveria usar exception com contexto
```

#### Routes (`backend/app/api/routes/`)

```python
# Verificar Depends(get_db)
/@router\.(get|post|put|delete|patch)[\s\S]*?(?!Depends\(get_database\))/

# Verificar response_model
/@router\.(get|post|put|delete|patch)\([^)]*\)(?![^)]*response_model)/

# Verificar summary
/@router\.(get|post|put|delete|patch)\([^)]*\)(?![^)]*summary)/
```

#### CV Pipeline (`src/computer_vision/`, `Models/`)

```python
# Verificar type hints em funcoes publicas
/def\s+[a-z_]+\([^)]*\)(?!.*->)/

# Verificar np.ndarray type hints
/def\s+\w+\([^)]*frame[^)]*\)(?![^)]*np\.ndarray)/

# Verificar docstrings em funcoes complexas (>10 linhas)
/def\s+\w+\([^)]*\):[\s\S]{200,}?(?!""")/
```

## Relatorio de Saida

```
RELATORIO DE VALIDACAO - Python Backend + CV Pipeline
============================================================

Arquivo: backend/app/services/video_service.py
   Tipo: Service

CRITICO (2 problemas)
-- PC01: Linha 45 - Funcao sync com operacao de DB
         def get_by_id(self, id):
         Correcao: async def get_by_id(self, id: str) -> dict:

-- PC02: Linha 48 - Await faltando
         result = self.collection.find_one(query)
         Correcao: result = await self.collection.find_one(query)

ALTO (1 problema)
-- PA01: Linha 45 - Type hints faltando
         def get_by_id(self, id):
         Correcao: def get_by_id(self, id: str) -> dict:

============================================================

Arquivo: backend/app/schemas/match.py
   Tipo: Schema

ALTO (1 problema)
-- PA03: Linha 12 - Field sem description
         player1: str = Field(...)
         Correcao: player1: str = Field(..., description="Nome do jogador 1")

============================================================

Arquivo: src/computer_vision/ball_tracking.py
   Tipo: CV Pipeline

ALTO (2 problemas)
-- PA01: Linha 34 - Type hints faltando
         def detect_ball(frame, threshold):
         Correcao: def detect_ball(frame: np.ndarray, threshold: float) -> tuple[int, int]:

-- PA02: Linha 34 - Docstring faltando
         def detect_ball(frame, threshold):
         Correcao: Adicionar docstring Google-style

============================================================
RESUMO: 2 criticos | 4 altos | 0 medios
VALIDACAO FALHOU - Correcoes necessarias
```

## Correcoes Automaticas (--auto-fix)

### Correcoes Aplicaveis Automaticamente

| Problema | Correcao Automatica |
|----------|---------------------|
| PA05 - Imports | Reorganizar imports (isort) |
| PM01 - Print | Substituir por logger |
| PA04 - from_attributes | Adicionar model_config |

### Correcoes Manuais Necessarias

| Problema | Motivo |
|----------|--------|
| PC01 - Async | Precisa verificar toda a chain |
| PC05 - Business logic | Precisa analise de contexto |
| PA01 - Type hints | Precisa inferir tipos |

## Integracao

Este agent e chamado por:
- Comando `/validate-backend`
- Comando `/commit` (para arquivos .py)
- Hook post-commit (validacao retrospectiva)

## Saida JSON (--json)

```json
{
  "files": [
    {
      "path": "backend/app/services/video_service.py",
      "type": "service",
      "valid": false,
      "critical": 2,
      "high": 1,
      "medium": 0,
      "violations": [
        {
          "id": "PC01",
          "line": 45,
          "severity": "critical",
          "code": "def get_by_id(self, id):",
          "message": "Funcao sync com operacao de DB",
          "suggestion": "async def get_by_id(self, id: str) -> dict:"
        }
      ]
    },
    {
      "path": "src/computer_vision/ball_tracking.py",
      "type": "cv_pipeline",
      "valid": false,
      "critical": 0,
      "high": 2,
      "medium": 0,
      "violations": [
        {
          "id": "PA01",
          "line": 34,
          "severity": "high",
          "code": "def detect_ball(frame, threshold):",
          "message": "Type hints faltando",
          "suggestion": "def detect_ball(frame: np.ndarray, threshold: float) -> tuple[int, int]:"
        }
      ]
    }
  ],
  "summary": {
    "totalFiles": 2,
    "validFiles": 0,
    "totalCritical": 2,
    "totalHigh": 3,
    "totalMedium": 0
  }
}
```
