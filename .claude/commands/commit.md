# Comando: Commit and Push

Faca commit e push das alteracoes com validacao de Design System (React) e padroes Python.

## Agents Utilizados

| Tipo de Arquivo | Agent | Validador |
|-----------------|-------|-----------|
| `.tsx/.jsx` | `agent-react` | `design-validator` |
| `.py` | `agent-python` | `python-validator` |
| `.md` | `agent-docs` | - |
| `.sql` | `agent-db` | - |

## Integracao Jira

- Se encontrar problemas, pode criar issue no Jira via `scripts/jira_helper.py`
- Vincula commit a issue `[TT-XXX]`
- Projeto Jira: **TT** (Tennis Tracking)

## Argumentos

`$ARGUMENTS`

- Vazio: commit de todas as alteracoes
- `--dry-run`: apenas mostra o que seria commitado
- `--skip-validation`: pula validacao de Design System e Python
- `--skip-tests`: pula execucao de testes
- `--auto-fix`: corrige problemas automaticamente
- `TT-XXX`: associa commit a issue Jira especifica

## Fluxo de Execucao

```
┌─────────────────────────────────────────────────────────────────┐
│                       /commit [args]                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Analisar git diff e git status                             │
│     - Listar arquivos alterados                                │
│     - Classificar por tipo (React, Python, SQL, Docs)          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Mapear modulo(s) afetado(s)                                │
│     - Identificar epic TT-XX relacionado                       │
│     - Determinar tipo de commit (feat/fix/refactor/docs)       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┴────────────────┐
              │                              │
        Tem .tsx/.jsx?                  Tem .py?
              │                              │
              ▼                              ▼
┌─────────────────────────┐  ┌───────────────────────────────────┐
│  3a. Validar React      │  │  3b. Validar Python               │
│  - Dark mode classes    │  │  - Async/await                    │
│  - Spinner padroes      │  │  - Type hints                     │
│  - Imports corretos     │  │  - SQL injection                  │
│  - Acessibilidade       │  │  - Padroes de service             │
└────────────┬────────────┘  └────────────────┬──────────────────┘
             │                                │
             └────────────┬───────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Executar testes (se --skip-tests NAO informado)            │
│     - Frontend: cd frontend && npm test (se houver .tsx/.jsx)  │
│     - Backend: cd backend && pytest (se houver .py)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┴────────────────┐
              │                              │
        Validacao OK?                  Validacao FALHOU?
              │                              │
              ▼                              ▼
┌─────────────────────────┐  ┌───────────────────────────────────┐
│  5a. Gerar mensagem     │  │  5b. Reportar problemas           │
│      de commit          │  │      - Listar erros               │
│                         │  │      - Sugerir correcoes          │
│                         │  │      - Criar issue Jira?          │
└────────────┬────────────┘  └───────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Executar git add + git commit + git push                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Exibir resumo final                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Mapeamento de Arquivos para Modulos

| Path do Arquivo | Modulo | Epic |
|-----------------|--------|------|
| `backend/app/api/routes/*` | routes | (por contexto) |
| `backend/app/services/*` | services | (por contexto) |
| `backend/app/models/*` | models | (por contexto) |
| `backend/app/schemas/*` | schemas | (por contexto) |
| `backend/app/core/*` | core | - |
| `web/src/components/*` | components | - |
| `web/src/pages/*` | pages | - |
| `web/src/services/*` | services | - |
| `Models/*` | cv-models | - |
| `scripts/*` | scripts | - |
| `docs/*` | docs | - |

## Passos Detalhados

### 1. Analisar Alteracoes

```bash
git status
git diff --stat
git diff --name-only
```

Classificar cada arquivo alterado pelo tipo:
- **React**: `.tsx`, `.jsx`, `.ts` (em `frontend/src/`)
- **Python**: `.py` (em `backend/app/`)
- **SQL**: `.sql` (em `scripts/migrations/`)
- **Docs**: `.md` (em `docs/`)
- **Config**: `.env`, `docker-compose.yml`, `Dockerfile`, etc.

### 2. Validar Design System (arquivos React)

Para cada arquivo `.tsx`/`.jsx` em `frontend/src/pages/` ou `frontend/src/components/`:

#### Verificacoes CRITICAS (bloqueiam commit)

| Verificacao | Padrao Correto | Padrao Incorreto | Acao |
|-------------|----------------|-------------------|------|
| Dark mode: background | `bg-gray-50 dark:bg-gray-900` | `bg-gray-50` (sem dark) | BLOQUEAR |
| Dark mode: texto | `text-gray-900 dark:text-gray-100` | `text-gray-900` (sem dark) | BLOQUEAR |
| Dark mode: border | `border-gray-200 dark:border-gray-700` | `border-gray-200` (sem dark) | BLOQUEAR |
| Dark mode: cards | `bg-white dark:bg-gray-800` | `bg-white` (sem dark) | BLOQUEAR |
| Spinner inline | Usar `<LoadingSpinner />` | `<div className="spinner">` | BLOQUEAR |
| Modal inline | Usar `<Modal />` | Modal customizado | BLOQUEAR |
| Color hardcoded | Usar variavel Tailwind | `style={{color: '#xxx'}}` | BLOQUEAR |

#### Verificacoes de WARNING (nao bloqueiam)

| Verificacao | Padrao Esperado | Acao |
|-------------|-----------------|------|
| Console.log | Nenhum em producao | WARNING |
| TODO/FIXME | Deve ter issue vinculada | WARNING |
| Acessibilidade aria-label | Presente em botoes/links | WARNING |
| Key em lists | `key={uniqueId}` | WARNING |

#### Formato de Saida - Validacao React

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VALIDACAO REACT - Design System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivo: frontend/src/pages/Clients/ClientDetail.tsx

CRITICO:
|- Linha 158: bg-gray-50 sem dark mode
|  Correcao: bg-gray-50 dark:bg-gray-800
|
|- Linha 203: border-gray-200 sem dark mode
|  Correcao: border-gray-200 dark:border-gray-700

WARNING:
|- Linha 45: console.log encontrado
|  Recomendacao: remover antes de producao

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resultado: FALHOU (2 criticos, 1 warning)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3. Validar Python (arquivos backend)

Para cada arquivo `.py` em `backend/app/`:

#### Verificacoes CRITICAS (bloqueiam commit)

| Verificacao | Padrao Correto | Padrao Incorreto | Acao |
|-------------|----------------|-------------------|------|
| Funcao sync em service | `async def get_by_id(` | `def get_by_id(` | BLOQUEAR |
| Await faltando | `await self.db.execute(` | `self.db.execute(` | BLOQUEAR |
| SQL injection | `select(Model).where(Model.id == id)` | `f"SELECT * WHERE id = {id}"` | BLOQUEAR |
| Import relativo | `from app.models.client import Client` | `import models` | BLOQUEAR |
| Commit sem await | `await self.db.commit()` | `self.db.commit()` | BLOQUEAR |

#### Verificacoes de WARNING (nao bloqueiam)

| Verificacao | Padrao Esperado | Acao |
|-------------|-----------------|------|
| Type hints | Todas as funcoes tipadas | WARNING |
| Docstrings | Servicos complexos documentados | WARNING |
| Print statement | Usar logger | WARNING |
| Tratamento de excecao | Except especifico, nao bare except | WARNING |

#### Formato de Saida - Validacao Python

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VALIDACAO PYTHON - Backend Patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivo: backend/app/services/client_service.py

CRITICO:
|- Linha 45: Funcao sync em service async
|  Encontrado: def get_active_clients(self):
|  Correcao: async def get_active_clients(self):
|
|- Linha 67: Await faltando em operacao de banco
|  Encontrado: result = self.db.execute(query)
|  Correcao: result = await self.db.execute(query)

WARNING:
|- Linha 12: Funcao sem type hint de retorno
|  Encontrado: async def create(self, data):
|  Recomendacao: async def create(self, data: ClientCreate) -> Client:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resultado: FALHOU (2 criticos, 1 warning)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Executar Testes (se --skip-tests NAO informado)

Se houver arquivos React alterados:

```bash
cd frontend && npm test -- --watchAll=false --passWithNoTests
```

Se houver arquivos Python alterados:

```bash
cd backend && pytest -v --tb=short
```

#### Formato de Saida - Testes

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TESTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontend: OK (12 testes passaram)
Backend:  OK (8 testes passaram)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Se testes falharem:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TESTES FALHARAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend: FALHOU
  - test_client_service.py::test_create_client - AssertionError
  - test_client_service.py::test_list_clients - ConnectionError

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Corrigir e tentar novamente
[2] Criar issue no Jira e commitar sem testes
[3] Commitar com --skip-tests
[4] Cancelar
```

### 5. Se Problemas Encontrados (Validacao ou Testes)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VALIDACAO FALHOU - Correcoes necessarias
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivo: frontend/src/pages/Clients/ClientDetail.tsx

CRITICO:
|- Linha 158: bg-gray-50 sem dark mode
|  Correcao: bg-gray-50 dark:bg-gray-800

Arquivo: backend/app/services/client_service.py

CRITICO:
|- Linha 45: Funcao sync em service async
|  Correcao: async def get_active_clients(self):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Criar issue no Jira e corrigir automaticamente
[2] Apenas corrigir (sem Jira)
[3] Ignorar e commitar mesmo assim (--skip-validation)
[4] Cancelar
```

### Opcao 1 - Criar Issue no Jira

```bash
python scripts/jira_helper.py create \
  --type Task \
  --summary "[Fix] Corrigir dark mode em ClientDetail.tsx" \
  --description "Encontrados problemas de dark mode durante commit.\n\n## Problemas\n- Linha 158: bg-gray-50 sem dark mode\n\n## Criterios de Aceite\n- [ ] Todas as classes bg-* tem variante dark:\n- [ ] Todas as classes text-* tem variante dark:" \
  --priority Medium \
  --labels "fix,dark-mode,frontend" \
  --parent TT-11 \
  --sp 1
```

### 6. Gerar Mensagem de Commit

#### Formato da Mensagem

```
tipo(modulo): Descricao curta em portugues [TT-XX]

## Resumo das Alteracoes

### Funcionalidades
- Item 1 descritivo
- Item 2 descritivo

### Arquivos Modificados
- frontend/src/pages/Clients/ClientDetail.tsx
- backend/app/services/client_service.py

### Notas Tecnicas
- Detalhes relevantes para revisao

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

#### Tipos de Commit

| Tipo | Quando Usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correcao de bug |
| `refactor` | Refatoracao sem mudanca de comportamento |
| `style` | Formatacao, espacamento, CSS |
| `docs` | Documentacao |
| `test` | Adicao/correcao de testes |
| `chore` | Tarefas gerais (configs, deps, CI) |
| `perf` | Melhoria de performance |

#### Determinacao Automatica do Modulo

O modulo eh determinado pelo path dos arquivos alterados:

```
backend/app/api/routes/*         → api
backend/app/services/*           → services
backend/app/models/*             → models
backend/app/schemas/*            → schemas
backend/app/core/*               → core
web/src/components/*             → ui
web/src/pages/*                  → pages
web/src/services/*               → frontend-services
Models/*                         → cv-models
scripts/*                        → scripts
docs/*                           → docs
```

Se multiplos modulos, usar o mais relevante ou combinar: `feat(clients,api): ...`

### 7. Executar Commit e Push

```bash
# Verificar branch atual
git branch --show-current

# Adicionar arquivos (NUNCA incluir .env, credentials, etc)
git add <arquivos_especificos>

# Commit com mensagem formatada (via HEREDOC)
git commit -m "$(cat <<'EOF'
tipo(modulo): Descricao [TT-XX]

## Resumo das Alteracoes

### Funcionalidades
- Item 1

### Arquivos Modificados
- path/to/file

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# Push para branch atual
git push origin <branch-atual>
```

### 8. Exibir Resumo Final

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 COMMIT REALIZADO COM SUCESSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit:  abc1234
Branch:  main
Arquivos: 5 alterados (+120 -45)
Design System: Validado
Python: Validado
Testes: Passaram (20 total)

## Resumo
- Componente ClientDetail criado com dark mode
- Endpoint de listagem de clientes implementado
- Service de clientes com paginacao

Push enviado para origin/main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Exemplo Completo de Commit

### Cenario: Implementacao de listagem de clientes

**Entrada:**
```
/commit
```

**Saida:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ANALISE DE ALTERACOES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivos alterados (4):
  M  web/src/pages/Videos/VideoList.tsx             (React)
  A  backend/app/services/video_service.py          (Python)
  A  backend/app/api/routes/videos.py               (Python)
  M  backend/app/main.py                            (Python)

Modulos: api, services
Tipo sugerido: feat

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VALIDACAO REACT - Design System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivo: web/src/pages/Videos/VideoList.tsx
Resultado: OK (sem problemas encontrados)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VALIDACAO PYTHON - Backend Patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivo: backend/app/services/video_service.py
Resultado: OK

Arquivo: backend/app/api/routes/videos.py
Resultado: OK

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 COMMIT REALIZADO COM SUCESSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit:  f7b2c3d
Branch:  main
Arquivos: 4 alterados (+280 -12)
Design System: Validado
Python: Validado

## Resumo
- Pagina de listagem de videos com filtros e paginacao
- Service de videos com CRUD completo
- Endpoint /api/videos registrado no main.py

Push enviado para origin/main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Regras

1. **NUNCA** fazer commit de arquivos sensiveis (`.env`, `credentials.json`, `.pfx`, chaves API, tokens)
2. **SEMPRE** usar portugues na mensagem de commit
3. **SEMPRE** incluir `[TT-XX]` se a alteracao estiver relacionada a uma issue do Jira
4. **SEMPRE** incluir `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>` na mensagem
5. **SEMPRE** validar Design System em arquivos React (a menos que `--skip-validation`)
6. **SEMPRE** validar padroes Python em arquivos backend (a menos que `--skip-validation`)
7. **SEMPRE** rodar testes se existirem (a menos que `--skip-tests`)
8. Problemas **CRITICOS** bloqueiam o commit (devem ser corrigidos antes)
9. Problemas de **WARNING** sao reportados mas nao bloqueiam
10. **NUNCA** usar `git add -A` sem antes verificar que nao ha arquivos sensiveis
11. **SEMPRE** usar `git add <arquivos_especificos>` ao inves de `git add .`
12. **SEMPRE** verificar se o build Docker funciona para alteracoes significativas (backend/frontend)
13. Commits seguem **Conventional Commits** em portugues: `tipo(modulo): descricao [TH-XX]`
14. Se `--auto-fix` for passado, corrigir problemas automaticamente sem perguntar
