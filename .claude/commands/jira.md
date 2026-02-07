# Comando: Jira (Buscar Proxima Issue)

Busca a proxima issue prioritaria do backlog, classifica o modelo adequado (haiku/sonnet/opus) e delega para um Task agent com o modelo otimizado.

## Argumentos

`$ARGUMENTS`

- Vazio: busca a issue de maior prioridade
- `TT-123`: trabalha em issue especifica
- `--list`: lista as 5 proximas issues com classificacao de modelo
- `--sprint`: mostra issues do sprint atual
- `--my`: mostra issues atribuidas a mim

## Ferramenta de Acesso ao Jira

**IMPORTANTE**: Use o script `scripts/jira_helper.py` para todas as operacoes com Jira.

```bash
# Buscar issues pendentes (retorna labels e story_points)
python3 scripts/jira_helper.py pending --max 10 --json

# Buscar com JQL customizado
python3 scripts/jira_helper.py search "project = TT AND status = 'To Do'" --max 5 --json

# Buscar issue especifica
python3 scripts/jira_helper.py get TT-123 --json

# Transicionar status
python3 scripts/jira_helper.py transition TT-123 21  # In Progress
python3 scripts/jira_helper.py transition TT-123 31  # Done
python3 scripts/jira_helper.py transition TT-123 32  # Review

# Adicionar comentario
python3 scripts/jira_helper.py comment TT-123 "Comentario"
```

## Fluxo de Execucao

```
┌─────────────────────────────────────────────────────────┐
│                    /jira                                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  1. Buscar issues To Do priorizadas                     │
│     python3 scripts/jira_helper.py search "..." --json  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  2. Classificar modelo (tabela de complexidade)         │
│     + Detectar modulo da issue                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  3. Exibir issue com classificacao e confirmar          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  4. Transicionar para In Progress                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  5. Lancar Task agent com modelo classificado           │
│     (haiku para docs, sonnet para features, opus para   │
│      seguranca/arquitetura)                             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  6. Ao concluir: commit + push + transicionar Done      │
└─────────────────────────────────────────────────────────┘
```

## Passos Detalhados

### 1. Buscar Issues Disponiveis

```bash
# Issues pendentes (excluindo Epics)
python3 scripts/jira_helper.py search "project = TT AND status = 'To Do' AND issuetype NOT IN (Epic) ORDER BY priority DESC, created ASC" --max 10 --json
```

Se `--sprint`:
```bash
python3 scripts/jira_helper.py search "project = TT AND sprint in openSprints() AND status != 'Done'" --max 10 --json
```

Se `TT-123` (issue especifica):
```bash
python3 scripts/jira_helper.py get TT-123 --json
```

Se `--list`: Mostrar as 5 primeiras com classificacao e perguntar qual executar.

### 2. Classificar Modelo da Issue

Aplicar as regras **em ordem** (primeira match ganha):

| # | Condicao | Modelo |
|---|----------|--------|
| 1 | Label contem: `security`, `auth`, `permission` | **opus** |
| 2 | Label contem: `architecture`, `refactor-major` | **opus** |
| 3 | Story Points >= 3 | **opus** |
| 4 | Label contem: `docs`, `documentation`, `translate`, `i18n` | **haiku** |
| 5 | Label contem: `config`, `chore` | **haiku** |
| 6 | Summary contem (case-insensitive): `traduc`, `i18n`, `readme`, `changelog`, `typo` | **haiku** |
| 7 | Story Points == 1 | **haiku** |
| 8 | Default (nenhuma regra acima) | **sonnet** |

### 3. Detectar Modulo da Issue

| Keywords (em labels ou summary) | Modulo |
|--------------------------------|--------|
| ball, bola, tracking, rastreamento | `ball_tracking` |
| court, quadra, detection, deteccao | `court_detection` |
| player, jogador, detection | `player_detection` |
| video, processamento, pipeline | `video_processing` |
| training, treino, analytics | `training_analytics` |
| frontend, react, component, page, tela | `frontend` |
| backend, api, endpoint, service, fastapi | `backend` |
| mobile, ios, android, kotlin, swift | `mobile` |
| docs, documentation, documentacao, readme | `docs` |
| devops, infra, docker, ci, deploy | `devops` |
| streaming, rtmp, hls, mediamtx | `streaming` |
| test, teste, e2e | `test` |

### 4. Exibir Issue Selecionada

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROXIMA ISSUE: TT-123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Titulo: [Titulo da issue]
Tipo: Tarefa | Subtask
Prioridade: High | Medium | Low
Story Points: X
Labels: [lista]
Modulo: tmf_person
Modelo: sonnet (regra: default)

Descricao:
[Conteudo resumido da issue]

Criterios de Aceite:
- [ ] Criterio 1
- [ ] Criterio 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Iniciar execucao? (S/N)
```

### 5. Transicionar para In Progress

```bash
python3 scripts/jira_helper.py transition TT-123 21
python3 scripts/jira_helper.py comment TT-123 "🤖 Desenvolvimento iniciado via Claude Code (modelo: {modelo})"
```

### 6. Lancar Task Agent com Modelo Adequado

Lancar um Task agent usando a ferramenta Task com o modelo classificado:

**Configuracao do Task agent:**
- `subagent_type`: "general-purpose"
- `model`: conforme classificacao (haiku/sonnet/opus)
- `description`: "Jira {ISSUE_KEY}"

**Prompt do agent:**

```
Voce e um agent de desenvolvimento. Execute a issue do Jira abaixo.

Issue: {ISSUE_KEY}
Summary: {summary}
Modulo: {modulo}

1. BUSCAR descricao completa:
   python3 scripts/jira_helper.py get {ISSUE_KEY} --json

2. IMPLEMENTAR conforme requisitos da issue:
   - Analisar a descricao e o tipo da issue
   - Implementar as mudancas necessarias
   - Seguir os padroes do projeto (ver CLAUDE.md)

3. COMMIT e PUSH:
   - git add dos arquivos modificados (especificos, nao usar git add .)
   - git commit -m "tipo(modulo): descricao [{ISSUE_KEY}]"
   - git pull --rebase origin main
   - git push origin main
   - Se push falhar, retry ate 3x

4. TRANSICIONAR para Done:
   python3 scripts/jira_helper.py transition {ISSUE_KEY} 31
   python3 scripts/jira_helper.py comment {ISSUE_KEY} "✅ Implementacao concluida

   Alteracoes: [resumo das mudancas]
   Commit: [hash do commit]
   Modelo: {modelo}"

REGRAS:
- NUNCA fazer git add . (apenas arquivos especificos)
- SEMPRE referenciar [{ISSUE_KEY}] no commit
- Seguir padroes de commit: tipo(modulo): descricao [TT-XXX]
- Tipos de commit: feat, fix, refactor, docs, test, chore
```

### 7. Exibir Resultado

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TT-123 CONCLUIDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Alteracoes:
- [Lista de mudancas do agent]

Modelo: sonnet
Commit: abc1234

Issue movida para Done
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Exemplo de Saida - Lista (--list)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BACKLOG TH - Top 5 Issues
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| # | Issue | Prioridade | Summary | SP | Modelo | Modulo |
|---|-------|------------|---------|-----|--------|--------|
| 1 | TT-145 | High | Bug: Login Safari | 2 | sonnet | tmf_person |
| 2 | TT-142 | Medium | Filtro por data | 3 | opus | tmf_report |
| 3 | TT-139 | Medium | Performance listagem | 2 | sonnet | tmf_resource |
| 4 | TT-138 | Low | Tooltip nos botoes | 1 | haiku | frontend |
| 5 | TT-135 | Low | Refactor auth | 3 | opus | tmf_person |

Qual issue deseja executar? (1-5 ou numero da issue)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Regras

1. **SEMPRE** usar `scripts/jira_helper.py` para acessar o Jira
2. **SEMPRE** classificar modelo antes de executar
3. **SEMPRE** transicionar para In Progress antes de comecar
4. **SEMPRE** adicionar comentarios de inicio e fim
5. **SEMPRE** transicionar para Done apos conclusao
6. **SEMPRE** usar o modelo classificado no Task agent
7. **NUNCA** executar sem confirmar com usuario (exceto se --auto)
8. Se issue tiver subtasks, executar na ordem correta
9. Se bloqueado, adicionar comentario e sugerir proxima issue
