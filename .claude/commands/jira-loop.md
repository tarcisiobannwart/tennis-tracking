# Comando: Jira Loop V2 - Polling Otimizado com Modelo Inteligente

Faz polling continuo buscando issues no Jira. Classifica cada issue por complexidade para escolher o modelo adequado (haiku/sonnet/opus) e agrupa por modulo para execucao paralela via Task agents.

## Argumentos

`$ARGUMENTS`

- Vazio: polling padrao a cada 30 minutos
- `--interval N`: intervalo em segundos entre buscas (padrao: 1800)
- `--max-per-cycle N`: limite de issues por ciclo (padrao: 10)
- `--max-parallel N`: maximo de agents paralelos (padrao: 3)
- `--skip TT-123,TT-456`: pular issues especificas
- `--model-override MODEL`: forcar modelo para todas as issues (haiku/sonnet/opus)
- `--dry-run`: apenas classificar sem executar

## Arquitetura

```
ORQUESTRADOR (modelo principal)
├── 1. Busca issues (jira_helper.py)
├── 2. Classifica complexidade (tabela de decisao)
├── 3. Agrupa por modulo (evitar conflitos git)
├── 4. Lanca Task agents em paralelo (max 3)
│     ├── Task Agent 1 (haiku):  issues docs/config
│     ├── Task Agent 2 (sonnet): issues frontend
│     └── Task Agent 3 (sonnet): issues backend
├── 5. Aguarda conclusao
├── 6. Exibe resumo
└── 7. Sleep 30min → volta ao 1
```

## Fluxo de Execucao Detalhado

### Passo 0: Inicializacao

Parsear argumentos de `$ARGUMENTS`:
- `interval` = 1800 (ou valor de --interval)
- `max_per_cycle` = 10 (ou valor de --max-per-cycle)
- `max_parallel` = 3 (ou valor de --max-parallel)
- `skip_list` = [] (ou valores de --skip, separados por virgula)
- `model_override` = null (ou valor de --model-override)
- `dry_run` = false (ou true se --dry-run)
- `failed_skip_list` = [] (issues que falharam, evitar reprocessamento)

Exibir banner inicial:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JIRA LOOP V2 - Polling Otimizado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modo: Polling a cada {interval/60} minutos
Modelo: Inteligente (haiku/sonnet/opus por complexidade)
{Se model_override: "Override: {model_override} para todas"}
Paralelo: Max {max_parallel} agents simultaneos
Inicio: [data/hora atual]
Interromper: Ctrl+C ou ESC

Iniciando primeira busca...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Passo 1: Buscar Issues

```bash
python3 scripts/jira_helper.py search "project = TT AND status = 'To Do' AND issuetype NOT IN (Epic) ORDER BY priority DESC, created ASC" --max 50 --json
```

Parsear o JSON retornado. Filtrar issues que estejam em `skip_list` ou `failed_skip_list`.

Se subtasks de uma tarefa pai existirem, executar subtasks primeiro.

Limitar ao `max_per_cycle`.

**Se nenhuma issue encontrada**: exibir mensagem e ir para Passo 6 (sleep).

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

Se `model_override` estiver definido, ignorar tabela e usar o modelo especificado para todas.

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

### Passo 4: Agrupar por Modulo e Criar Batches

1. Agrupar issues pelo modulo detectado
2. Dentro de cada grupo, manter a ordem de prioridade original
3. Para o modelo do grupo, usar o modelo MAIS FORTE necessario (opus > sonnet > haiku). Ex: se um grupo tem 2 issues haiku e 1 opus, o agent roda como opus.
4. Criar batches de no maximo `max_parallel` grupos por vez

Exemplo:
```
Issues encontradas:
  TT-601 (docs, haiku)
  TT-602 (tmf_person, sonnet)
  TT-603 (tmf_product, sonnet)
  TT-604 (tmf_resource, opus)
  TT-605 (docs, haiku)

Agrupamento:
  Grupo "docs":        [TT-601, TT-605] → haiku
  Grupo "tmf_person":  [TT-602]           → sonnet
  Grupo "tmf_product": [TT-603]           → sonnet
  Grupo "tmf_resource":[TT-604]           → opus

Batch 1 (max 3 paralelos): docs, tmf_person, tmf_product
Batch 2 (restante):        tmf_resource
```

### Passo 4b: Dry-Run Mode

Se `dry_run` == true, exibir tabela de classificacao e parar:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DRY-RUN - Classificacao de Issues
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Issue | Summary | Labels | SP | Modelo | Modulo |
|-------|---------|--------|----|--------|--------|
| TT-601 | Atualizar docs | docs | 1 | haiku | docs |
| TT-602 | Fix login | auth | 2 | sonnet | tmf_person |
...

Batches planejados:
  Batch 1: [docs(2), tmf_person(1), tmf_product(1)]
  Batch 2: [tmf_resource(1)]

Proximo ciclo em {interval/60} minutos...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Depois ir para Passo 6 (sleep) e continuar o loop.

### Passo 5: Executar Batches

Para cada batch:

**5a. Lancar Task agents em paralelo** usando a ferramenta Task:

Para cada grupo no batch, lancar UM Task agent com o modelo classificado. O prompt do agent deve conter:

```
Voce e um agent de desenvolvimento. Execute as seguintes issues do Jira SEQUENCIALMENTE.

Para CADA issue abaixo:

1. TRANSICIONAR para In Progress:
   python3 scripts/jira_helper.py transition {ISSUE_KEY} 21
   python3 scripts/jira_helper.py comment {ISSUE_KEY} "🤖 [LOOP-V2] Desenvolvimento iniciado (modelo: {modelo})"

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
   python3 scripts/jira_helper.py comment {ISSUE_KEY} "✅ [LOOP-V2] Implementacao concluida

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

### Passo 6: Resumo do Ciclo e Sleep

Exibir resumo:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[HH:MM:SS] Ciclo #N - Resumo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Processadas neste ciclo: X issues
  haiku: Y | sonnet: Z | opus: W
Erros neste ciclo: E issues

Total acumulado: T issues (F erros)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Decisao de continuar:**
- Se processou issues neste ciclo → voltar ao Passo 1 IMEDIATAMENTE (sem sleep)
- Se nao encontrou issues → sleep pelo intervalo configurado, depois voltar ao Passo 1

```bash
# Sleep (apenas quando nao ha issues)
sleep {interval}
```

## Tratamento de Erros

Se uma issue falhar durante a execucao pelo Task agent:

1. **Agent comenta o erro** na issue via jira_helper.py
2. **NAO transiciona** (fica em In Progress para review manual)
3. **Continua com proxima issue** dentro do mesmo grupo
4. **Orquestrador adiciona a issue ao `failed_skip_list`** para nao reprocessar no proximo ciclo
5. **Incrementa contador de erros**

Se um Task agent inteiro falhar (crash):
1. Todas as issues nao-processadas daquele grupo voltam ao proximo ciclo
2. O orquestrador continua com os demais batches

## Regras

1. **NUNCA** executar Epics (apenas Tarefas e Subtasks)
2. **SEMPRE** classificar modelo antes de executar
3. **SEMPRE** agrupar por modulo para evitar conflitos git
4. **SEMPRE** limitar agents paralelos ao `max_parallel`
5. **SEMPRE** adicionar comentarios de inicio/fim em cada issue
6. **SEMPRE** continuar o loop mesmo se issues falharem
7. **SEMPRE** exibir timestamp em cada verificacao
8. **SEMPRE** manter contadores atualizados (processadas, erros, ciclos, por modelo)
9. **SEMPRE** voltar a buscar imediatamente apos executar issues (sem espera)
10. **SEMPRE** esperar intervalo configurado quando nao ha issues
11. Se houver subtasks de uma tarefa pai, executar subtasks primeiro
12. Issues que falharam sao adicionadas ao `failed_skip_list` e nao sao reprocessadas
13. Cada Task agent faz seu proprio commit + push (git pull --rebase antes)
14. O modelo do grupo e o MAIS FORTE entre as issues do grupo

## Exemplo de Uso

```bash
# Polling padrao (30 minutos, modelo inteligente)
/jira-loop

# Polling a cada 10 minutos
/jira-loop --interval 600

# Maximo 5 issues por ciclo, 2 agents paralelos
/jira-loop --max-per-cycle 5 --max-parallel 2

# Forcar tudo como sonnet
/jira-loop --model-override sonnet

# Apenas classificar sem executar
/jira-loop --dry-run

# Pular issues especificas
/jira-loop --skip TT-123,TT-456
```

## Exemplo de Saida

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JIRA LOOP V2 - Polling Otimizado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modo: Polling a cada 30 minutos
Modelo: Inteligente (haiku/sonnet/opus por complexidade)
Paralelo: Max 3 agents simultaneos
Inicio: 2026-02-06 14:30:00
Interromper: Ctrl+C ou ESC

Iniciando primeira busca...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[14:30:00] Ciclo #1 - Buscando issues...
           Encontradas: 4 issues

Classificacao:
  TT-601 | Atualizar README         | haiku  | docs
  TT-602 | Fix login redirect       | sonnet | tmf_person
  TT-603 | Nova pagina de produtos  | sonnet | tmf_product
  TT-604 | Refactor auth middleware | opus   | tmf_person

Batches:
  Batch 1 [3 agents]: docs(1), tmf_person(2→opus), tmf_product(1)

>> Lancando 3 Task agents em paralelo...
   Agent 1 (haiku):  docs [TT-601]
   Agent 2 (opus):   tmf_person [TT-602, TT-604]
   Agent 3 (sonnet): tmf_product [TT-603]

>> Aguardando conclusao...
   ✅ Agent 1 (haiku):  1/1 concluida
   ✅ Agent 2 (opus):   2/2 concluidas
   ✅ Agent 3 (sonnet): 1/1 concluida

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[14:35:00] Ciclo #1 - Resumo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Processadas neste ciclo: 4 issues
  haiku: 1 | sonnet: 1 | opus: 2
Erros neste ciclo: 0 issues

Total acumulado: 4 issues (0 erros)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[14:35:01] Ciclo #2 - Buscando issues...
           Encontradas: 0 issues
           Proxima verificacao em 30 minutos...

[15:05:01] Ciclo #3 - Buscando issues...
```
