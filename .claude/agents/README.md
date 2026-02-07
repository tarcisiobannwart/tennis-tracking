# Agents Tennis Tracking

Este diretorio contem agents especializados para o projeto Tennis Tracking.

## Agents Globais Disponiveis

Os seguintes agents globais estao disponiveis em `~/.claude/agents/`:

| Agent | Arquivo | Especializacao |
|-------|---------|----------------|
| React | `agent-react.md` | Frontend React/TypeScript |
| UI/UX | `agent-ui.md` | Design de interfaces, TailwindCSS |
| Python | `agent-python.md` | Backend FastAPI |
| DevOps | `agent-devops.md` | Docker, K8s, CI/CD |
| Docs | `agent-docs.md` | Documentacao tecnica |
| QA | `agent-qa.md` | Testes e qualidade |

## Agents do Projeto

Agents especificos do Tennis Tracking:

| Agent | Arquivo | Funcao |
|-------|---------|--------|
| **Jira Manager** | `jira-manager.md` | Gestor de projeto, backlog e delegacao |
| Design Validator | `design-validator.md` | Validar padroes do Design System |
| React Refactor | `react-refactor.md` | Refatorar codigo React |
| React Page Creator | `react-page-creator.md` | Criar paginas React padronizadas |
| Python Validator | `python-validator.md` | Validar codigo Python (Backend + CV Pipeline) |
| Python Refactor | `python-refactor.md` | Refatorar codigo Python (Backend + CV Pipeline) |
| Test Page Creator | `test-page-creator.md` | Criar testes para paginas React |

## Mapeamento Comando -> Agent

| Comando | Agent(s) Acionado(s) |
|---------|---------------------|
| `/jira` | `jira-manager` -> agents conforme tarefa |
| `/create-jira` | `jira-manager` |
| `/commit` | `design-validator` (React) + `python-validator` (Python) |
| `/validate-design` | `design-validator` + `agent-ui` |
| `/validate-backend` | `python-validator` + `agent-python` |
| `/react-page` | `react-page-creator` + `agent-react` + `agent-ui` |
| `/refactor-list-page` | `react-refactor` |
| `/test-page` | `test-page-creator` |
| `/api-endpoint` | `agent-python` |
| `/backend-patterns` | `agent-python` |

## Como Usar

Nos comandos, referencie o agent apropriado:

```markdown
## Agent

Este comando utiliza os seguintes agents:
- **Principal**: `agent-react` (especialista React)
- **Suporte**: `agent-ui` (design e acessibilidade)
- **Validacao**: `design-validator` (padroes do projeto)
```

## Fluxo de Execucao

### Fluxo com Jira (recomendado)

```
/jira ou /create-jira
        |
        v
+-------------------+
|   jira-manager    |  <- Gestor de Projeto
|   (backlog)       |
+---------+---------+
          |
          v
+-------------------+
|  Agent Principal  |  <- agent-react, agent-python, etc.
+---------+---------+
          |
          v
+-------------------+
| Agent de Suporte  |  <- agent-ui, agent-qa, etc.
+---------+---------+
          |
          v
+-------------------+
|    Validacao      |  <- design-validator, python-validator
+---------+---------+
          |
          v
    Issue -> Done
```

### Fluxo Direto (comandos especificos)

```
Comando -> Agent Principal -> Agent de Suporte -> Validacao
   |            |                |                |
   |            v                v                v
   |      Executa tarefa   Verifica padroes   Valida resultado
   |            |                |                |
   +------------+----------------+----------------+
                         |
                         v
                    Resultado
```

## Estrutura de Epicos por Modulo

| Modulo | Epico | Descricao |
|--------|-------|-----------|
| Video | TT-11 | Processamento e analise de videos |
| Players | TT-12 | Gestao de jogadores e ranking |
| Matches | TT-13 | Partidas e estatisticas |
| Training | TT-14 | Sistema de treinos |
| Analytics | TT-15 | Insights e previsoes com IA |
| Streaming | TT-16 | Streaming ao vivo (MediaMTX) |
| Infraestrutura | TT-17 | Migrations, logs, observabilidade |
| Configuracoes | TT-18 | Usuarios, times, permissoes, 2FA |
