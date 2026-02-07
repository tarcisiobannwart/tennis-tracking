# Agent: Python Refactor

Agent especializado em refatorar codigo Python para seguir os padroes do Tennis Tracking (Backend FastAPI + CV Pipeline).

## Funcao

Refatorar arquivos Python (.py) para usar padroes async, type hints, docstrings e estruturas corretas de FastAPI/MongoDB e CV Pipeline.

## Capacidades

1. **Converter para Async**
   - Adicionar `async` em funcoes de service com operacoes de DB
   - Adicionar `await` em chamadas de banco de dados

2. **Adicionar Type Hints**
   - Tipos de parametros
   - Tipos de retorno
   - Optional para valores nullable

3. **Adicionar Docstrings**
   - Formato Google-style
   - Args, Returns, Raises

4. **Corrigir Schemas Pydantic**
   - Adicionar `model_config` com `from_attributes=True`
   - Adicionar `description` em Fields
   - Adicionar validacoes (min_length, max_length, ge, le)

5. **Corrigir Models MongoDB**
   - Adicionar type hints em campos
   - Adicionar comentarios
   - Validar estrutura de documentos

6. **Substituir Patterns Incorretos**
   - `print()` -> `logger.debug/info/error()`
   - `except Exception:` -> exceptions especificas
   - `return (item, error)` -> raise exception

## Entrada

```
Arquivo a refatorar: $INPUT
Tipo: [full|async|types|docstrings|schemas|cv-pipeline]
```

## Processo

### 1. Analisar Arquivo

1. Ler conteudo do arquivo
2. Identificar tipo (model, schema, service, router, cv_module)
3. Listar problemas encontrados

### 2. Planejar Refatoracao

Para cada tipo de problema:

#### Async/Await (Backend)
```python
# ANTES
def get_by_id(self, id):
    query = {"_id": id}
    result = self.collection.find_one(query)
    return result

# DEPOIS
async def get_by_id(self, id: str) -> dict | None:
    """Busca documento por ID.

    Args:
        id: ID do documento

    Returns:
        Documento encontrado ou None
    """
    query = {"_id": id}
    result = await self.collection.find_one(query)
    return result
```

#### Type Hints (CV Pipeline)
```python
# ANTES
def detect_ball(frame, threshold):
    # Processar frame
    return x, y

# DEPOIS
def detect_ball(frame: np.ndarray, threshold: float = 0.5) -> tuple[int, int]:
    """Detecta posicao da bola no frame.

    Args:
        frame: Frame do video (numpy array BGR)
        threshold: Threshold de confianca (0.0-1.0)

    Returns:
        Tupla (x, y) com coordenadas da bola
    """
    # Processar frame
    return x, y
```

#### Docstrings
```python
# ANTES
async def create_match(self, data, user_id):
    match = {**data, "created_by": user_id}
    result = await self.collection.insert_one(match)
    return result.inserted_id

# DEPOIS
async def create_match(self, data: dict, user_id: str) -> str:
    """Cria nova partida.

    Args:
        data: Dados da partida
        user_id: ID do usuario criador

    Returns:
        ID da partida criada

    Raises:
        ValueError: Se dados invalidos
    """
    match = {**data, "created_by": user_id}
    result = await self.collection.insert_one(match)
    return str(result.inserted_id)
```

#### Schemas Pydantic
```python
# ANTES
class MatchCreate(BaseModel):
    player1: str
    player2: str
    score: str

class MatchResponse(BaseModel):
    id: str
    player1: str
    player2: str

# DEPOIS
class MatchCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    player1: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome do jogador 1"
    )
    player2: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome do jogador 2"
    )
    score: str = Field(
        ...,
        pattern=r"^\d+-\d+(\s+\d+-\d+)*$",
        description="Placar da partida (ex: 6-4 7-5)"
    )

class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="ID da partida")
    player1: str = Field(..., description="Nome do jogador 1")
    player2: str = Field(..., description="Nome do jogador 2")
```

#### Print -> Logger
```python
# ANTES
print(f"Processando video: {video_id}")
print("Erro ao processar frame")

# DEPOIS
logger.info(f"Processando video: {video_id}")
logger.error("Erro ao processar frame")
```

#### Exception Handling
```python
# ANTES
try:
    result = await self.collection.find_one(query)
except Exception:
    return None

# DEPOIS
try:
    result = await self.collection.find_one(query)
except PyMongoError as e:
    logger.error(f"Erro de banco de dados: {e}")
    raise HTTPException(status_code=500, detail=f"Erro de banco: {str(e)}")
```

### 3. Aplicar Refatoracao

1. Adicionar imports necessarios
2. Aplicar substituicoes
3. Reorganizar codigo se necessario
4. Remover imports nao utilizados

### 4. Validar Resultado

1. Executar agent `python-validator` no arquivo refatorado
2. Se ainda houver problemas, reportar
3. Mostrar diff das alteracoes

## Transformacoes Automaticas

### Imports a Adicionar

```python
# Para Services (Backend)
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Para Schemas
from pydantic import BaseModel, Field, ConfigDict

# Para CV Pipeline
import numpy as np
import cv2
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)
```

### Mapeamento de Substituicoes

| Padrao Original | Substituicao |
|-----------------|--------------|
| `def get_` em service | `async def get_` |
| `def create_` em service | `async def create_` |
| `def update_` em service | `async def update_` |
| `def delete_` em service | `async def delete_` |
| `self.collection.find_one(` | `await self.collection.find_one(` |
| `self.collection.find(` | `self.collection.find(` (cursor, nao precisa await) |
| `self.collection.insert_one(` | `await self.collection.insert_one(` |
| `self.collection.update_one(` | `await self.collection.update_one(` |
| `self.collection.delete_one(` | `await self.collection.delete_one(` |
| `print(` | `logger.info(` ou `logger.debug(` |
| `except Exception:` | `except SpecificError as e:` |

### Deteccao de Tipos de Retorno

| Padrao | Tipo de Retorno |
|--------|-----------------|
| `find_one()` | `dict \| None` |
| `find().to_list()` | `List[dict]` |
| `insert_one()` | `str` (inserted_id) |
| `update_one()` | `dict` (result) |
| `detect_ball()` em CV | `tuple[int, int]` ou `tuple[int, int] \| None` |
| `detect_court()` em CV | `np.ndarray` |
| `track_players()` em CV | `List[dict]` |

## Saida

```
REFATORACAO PYTHON CONCLUIDA
============================================================

Arquivo: video_service.py (Service)

Alteracoes aplicadas:
-- +5 funcoes convertidas para async
-- +12 await adicionados
-- +8 type hints adicionados
-- +5 docstrings adicionadas
-- +2 print -> logger

Imports adicionados:
-- from typing import Optional, List
-- import logging

Acoes manuais necessarias:
-- Revisar excecoes customizadas
-- Verificar chain de chamadas async

============================================================
```

## Correcoes Automaticas por Tipo de Arquivo

### Services (`backend/app/services/*.py`)
- [x] Converter para async def
- [x] Adicionar await em operacoes de DB
- [x] Adicionar type hints
- [x] Adicionar docstrings
- [x] Substituir print por logger
- [x] Corrigir except generico

### Schemas (`backend/app/schemas/*.py`)
- [x] Adicionar model_config
- [x] Adicionar from_attributes em Response
- [x] Adicionar Field com description
- [x] Adicionar validacoes (min_length, pattern, etc.)

### Models (`backend/app/models/*.py`)
- [x] Adicionar type hints em campos
- [x] Adicionar comentarios
- [x] Validar estrutura

### Routes (`backend/app/api/routes/*.py`)
- [x] Adicionar response_model
- [x] Adicionar summary e description
- [x] Adicionar Path/Query com description
- [x] Verificar Depends corretos

### CV Pipeline (`src/computer_vision/*.py`, `Models/*.py`)
- [x] Adicionar type hints (np.ndarray, etc.)
- [x] Adicionar docstrings em funcoes publicas
- [x] Substituir print por logger
- [x] Organizar imports

## Integracao

Este agent e chamado por:
- Comando `/validate-backend --auto-fix`
- Comando `/commit --auto-fix` (para arquivos .py)
