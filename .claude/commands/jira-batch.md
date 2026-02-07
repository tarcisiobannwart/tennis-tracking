# Comando: Jira Batch V2 (Executar Issues com Modelo Inteligente)

Executa todas as issues pendentes (nao-Epics) com classificacao inteligente de modelo (haiku/sonnet/opus) e execucao paralela por modulo. Mesma logica do `/jira-loop`, mas execucao unica (sem polling).

## Argumentos

`$ARGUMENTS`

- Vazio: executa todas as issues pendentes
- `--max N`: limita a N issues (ex: `--max 5`)
- `--max-parallel N`: maximo de agents paralelos (padrao: 3)
- `--skip TT-123,TT-456`: pula issues especificas
- `--model-override MODEL`: forcar modelo para todas as issues (haiku/sonnet/opus)
- `--dry-run`: apenas lista e classifica as issues sem executar

## Arquitetura

```
ORQUESTRADOR (modelo principal)
├── 1. Busca issues (jira_helper.py)
├── 2. Classifica complexidade (tabela de decisao)
├── 3. Agrupa por modulo (evitar conflitos git)
├── 4. Lanca Task agents em paralelo (max 3)
│     ├── Task Agent 1 (haiku):  issues docs/config
│     ├── Task Agent 2 (sonnet): issues frontend
│     └── Task Agent 3 (opus):   issues backend/auth
├── 5. Aguarda conclusao
└── 6. Exibe resumo final
```

## Fluxo de Execucao Detalhado

### Passo 1: Buscar Issues Pendentes

```bash
python3 scripts/jira_helper.py search "project = TT AND status = 'To Do' AND issuetype NOT IN (Epic) ORDER BY priority DESC, created ASC" --max 50 --json
```

Parsear JSON. Filtrar issues do `--skip`. Limitar ao `--max` se definido.

Se subtasks de uma tarefa pai existirem, executar subtasks primeiro.

**Se nenhuma issue encontrada**: exibir mensagem e encerrar.

### Passo 2: Classificar Modelo de Cada Issue

Para cada issue, aplicar as regras **em ordem** (primeira match ganha):

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

Se `--model-override` estiver definido, ignorar tabela e usar o modelo especificado.

### Passo 3: Detectar Modulo de Cada Issue

Analisar labels e summary (case-insensitive) para determinar o modulo:

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

Se nenhuma keyword corresponder, usar `general`.

**IMPORTANTE**: Se uma issue tiver keywords de multiplos modulos, usar o PRIMEIRO match da tabela.

### Passo 4: Exibir Resumo e Agrupar

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JIRA BATCH V2 - Execucao com Modelo Inteligente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total: {N} issues
Paralelo: Max {max_parallel} agents simultaneos

| Issue | Summary | Labels | SP | Modelo | Modulo |
|-------|---------|--------|----|--------|--------|
| TT-601 | Atualizar docs | docs | 1 | haiku | docs |
| TT-602 | Fix login | auth | 2 | sonnet | tmf_person |
...

Batches planejados:
  Batch 1 [3 agents]: docs(2→haiku), tmf_person(1→sonnet), tmf_product(1→sonnet)
  Batch 2 [1 agent]:  tmf_resource(1→opus)

{Se dry-run: "DRY-RUN: Nenhuma execucao realizada." e encerrar}

Iniciando execucao...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Agrupamento**:
1. Agrupar issues pelo modulo detectado
2. Dentro de cada grupo, manter a ordem de prioridade original
3. Para o modelo do grupo, usar o modelo MAIS FORTE necessario (opus > sonnet > haiku)
4. Criar batches de no maximo `max_parallel` grupos por vez

### Passo 5: Executar Batches

Para cada batch:

**5a. Lancar Task agents em paralelo** usando a ferramenta Task:

Para cada grupo no batch, lancar UM Task agent com o modelo classificado. O prompt do agent deve conter:

```
Voce e um agent de desenvolvimento. Execute as seguintes issues do Jira SEQUENCIALMENTE.

Para CADA issue abaixo:

1. TRANSICIONAR para In Progress:
   python3 scripts/jira_helper.py transition {ISSUE_KEY} 21
   python3 scripts/jira_helper.py comment {ISSUE_KEY} "🤖 [BATCH-V2] Desenvolvimento iniciado (modelo: {modelo})"

2. BUSCAR descricao completa:
   python3 scripts/jira_helper.py get {ISSUE_KEY} --json

3. IMPLEMENTAR conforme requisitos da issue:
   - Analisar a descricao e o tipo da issue
   - Implementar as mudancas necessarias
   - Seguir os padroes do projeto (ver CLAUDE.md)

4. COMMIT e PUSH:
   - git add dos arquivos modificados (especificos, nao usar git add .)
   - git commit -m "tipo(modulo): descricao [ISSUE_KEY]"
   - git pull --rebase origin main
   - git push origin main
   - Se push falhar, retry ate 3x

5. TRANSICIONAR para Done:
   python3 scripts/jira_helper.py transition {ISSUE_KEY} 31
   python3 scripts/jira_helper.py comment {ISSUE_KEY} "✅ [BATCH-V2] Implementacao concluida

   Alteracoes: [resumo das mudancas]
   Commit: [hash do commit]
   Modelo: {modelo}"

6. Se ERRO em qualquer passo:
   - Comentar o erro na issue
   - NAO transicionar (deixar em In Progress para review manual)
   - Continuar com a proxima issue do grupo

Issues para executar:
{lista de issues do grupo com key, summary, description resumida}

REGRAS:
- NUNCA fazer git add . (apenas arquivos especificos)
- SEMPRE referenciar [ISSUE_KEY] no commit
- Se houver conflito no rebase, resolver automaticamente se possivel, senao reportar erro
- Seguir padroes de commit: tipo(modulo): descricao [TT-XXX]
- Tipos de commit: feat, fix, refactor, docs, test, chore
```

**Configuracao do Task agent:**
- `subagent_type`: "general-purpose"
- `model`: conforme classificacao do grupo
- `description`: "Jira {modulo} issues"

**5b. Aguardar todos os agents do batch terminarem** antes de lancar o proximo batch.

**5c. Coletar resultados** de cada agent (sucesso/erro por issue).

### Passo 6: Resumo Final

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BATCH V2 CONCLUIDO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Resultado:
  Concluidas: X issues
    haiku: Y | sonnet: Z | opus: W
  Com erro: E issues
  Commits: C

Issues finalizadas:
  ✅ TT-601 (haiku)  - Atualizar docs
  ✅ TT-602 (sonnet) - Fix login
  ❌ TT-603 (sonnet) - Nova pagina (erro: ...)
  ✅ TT-604 (opus)   - Refactor auth

Todas as issues do backlog foram processadas!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Tratamento de Erros

Se uma issue falhar durante a execucao pelo Task agent:

1. **Agent comenta o erro** na issue via jira_helper.py
2. **NAO transiciona** (fica em In Progress para review manual)
3. **Continua com proxima issue** dentro do mesmo grupo
4. **Inclui no resumo final** com indicacao de erro

Se um Task agent inteiro falhar (crash):
1. As issues nao-processadas daquele grupo sao listadas como erro no resumo
2. O orquestrador continua com os demais batches

## Regras

1. **NUNCA** executar Epics (apenas Tarefas e Subtasks)
2. **SEMPRE** classificar modelo antes de executar
3. **SEMPRE** agrupar por modulo para evitar conflitos git
4. **SEMPRE** limitar agents paralelos ao `max_parallel`
5. **SEMPRE** adicionar comentarios de inicio/fim em cada issue
6. **SEMPRE** continuar mesmo se uma issue falhar
7. **SEMPRE** exibir resumo final com status de todas as issues
8. Se houver subtasks de uma tarefa pai, executar subtasks primeiro
9. Respeitar dependencias (blockedBy) entre issues
10. Cada Task agent faz seu proprio commit + push (git pull --rebase antes)
11. O modelo do grupo e o MAIS FORTE entre as issues do grupo

## Exemplo de Uso

```bash
# Executar todas as issues pendentes
/jira-batch

# Limitar a 5 issues
/jira-batch --max 5

# Maximo 2 agents paralelos
/jira-batch --max-parallel 2

# Forcar tudo como sonnet
/jira-batch --model-override sonnet

# Apenas classificar (dry-run)
/jira-batch --dry-run

# Pular issues especificas
/jira-batch --skip TT-123,TT-456
```
