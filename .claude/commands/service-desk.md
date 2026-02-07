# Comando: Service Desk - Loop de Suporte Inteligente com RAG

> **REGRA CRITICA DE SEGURANCA**: TODAS as respostas geradas sao APENAS sugestoes internas para agentes de suporte. NUNCA, sob NENHUMA circunstancia, enviar resposta diretamente ao cliente. SOMENTE comentarios PRIVADOS/INTERNOS. Qualquer postagem DEVE usar a API backend (que forca `internal=True`) ou `comment-internal` do jira_helper.py. O uso do comando `comment` (publico) e PROIBIDO neste fluxo.

Faz polling continuo no board CS (Service Desk), classifica tickets por complexidade, gera respostas via RAG e posta como **comentario interno/privado** no Jira (invisivel ao cliente). Usa modelo inteligente (haiku/sonnet/opus) por complexidade do ticket.

## Argumentos

`$ARGUMENTS`

- Vazio: polling padrao a cada 5 minutos
- `--interval N`: intervalo em segundos entre ciclos (padrao: 300)
- `--max-per-cycle N`: limite de tickets por ciclo (padrao: 5)
- `--max-parallel N`: maximo de agents paralelos (padrao: 3)
- `--skip CS-123,CS-456`: pular tickets especificos
- `--model-override MODEL`: forcar modelo para todos os tickets (haiku/sonnet/opus)
- `--client-id UUID`: client ID para contexto RAG (obrigatorio na primeira vez, depois reusar)
- `--dry-run`: apenas classificar sem gerar respostas
- `--once`: executar apenas 1 ciclo (sem loop)

## Arquitetura

```
ORQUESTRADOR (modelo principal)
├── 0. Autenticar na API backend (obter Bearer token)
├── 1. Busca tickets abertos no CS (jira_helper.py)
├── 2. Filtra tickets ja respondidos (tag [RAG-CLI])
├── 3. Classifica complexidade (tabela de decisao)
├── 4. Lanca Task agents em paralelo (max 3)
│     ├── Task Agent 1 (haiku):  ticket FAQ/simples
│     ├── Task Agent 2 (sonnet): ticket tecnico
│     └── Task Agent 3 (opus):   ticket critico
│     Cada agent usa a API backend para:
│       → POST /api/rag/service-desk/generate/{key} (gera resposta + feedback_token)
│       → POST /api/rag/service-desk/post-comment/{id} (posta com links feedback)
├── 5. Aguarda conclusao
├── 6. Exibe resumo
└── 7. Sleep → volta ao 1
```

## Ferramentas

### Jira (via jira_helper.py) - Leitura e busca

```bash
# Buscar tickets do Service Desk
python3 scripts/jira_helper.py search "project = CS AND ..." --max 20 --json

# Buscar ticket especifico com descricao
python3 scripts/jira_helper.py get CS-123 --json --full

# Listar comentarios de um ticket (para verificar duplicatas)
python3 scripts/jira_helper.py get-comments CS-123 --json

# Transicionar status
python3 scripts/jira_helper.py transition CS-123 21  # In Progress
```

### API Backend (via curl) - Geracao e postagem com feedback

```bash
# Autenticar
curl -s -X POST http://localhost:11000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "tarcisio@trademarketingforce.com", "password": "admin123"}'

# Gerar resposta RAG (cria RAGResponse + feedback_token)
curl -s -X POST "http://localhost:11000/api/rag/service-desk/generate/CS-123?client_id={UUID}&trigger_type=new_ticket" \
  -H "Authorization: Bearer {TOKEN}"

# Postar como comentario interno com links de feedback
curl -s -X POST "http://localhost:11000/api/rag/service-desk/post-comment/{response_id}" \
  -H "Authorization: Bearer {TOKEN}"

# Ver status do polling
curl -s "http://localhost:11000/api/rag/service-desk/polling-status" \
  -H "Authorization: Bearer {TOKEN}"
```

## Fluxo de Execucao Detalhado

### Passo 0: Inicializacao

Parsear argumentos de `$ARGUMENTS`:
- `interval` = 300 (ou valor de --interval)
- `max_per_cycle` = 5 (ou valor de --max-per-cycle)
- `max_parallel` = 3 (ou valor de --max-parallel)
- `skip_list` = [] (ou valores de --skip, separados por virgula)
- `model_override` = null (ou valor de --model-override)
- `dry_run` = false (ou true se --dry-run)
- `once` = false (ou true se --once)
- `client_id` = valor de --client-id (obrigatorio se nao for dry-run)
- `responded_list` = [] (tickets ja respondidos nesta sessao)

**Autenticacao na API backend:**

```bash
# Obter token de acesso
curl -s -X POST http://localhost:11000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "tarcisio@trademarketingforce.com", "password": "admin123"}'
```

Parsear o JSON e extrair `access_token`. Armazenar como `API_TOKEN` para usar nos agents.

Se o login falhar, exibir erro e encerrar.

Se `client_id` nao foi fornecido e nao e `dry_run`, perguntar ao usuario qual client_id usar (pode listar via API se disponivel).

Exibir banner inicial:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SERVICE DESK RAG - Suporte Inteligente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modo: Polling a cada {interval/60} minutos
Modelo: Inteligente (haiku/sonnet/opus por complexidade)
{Se model_override: "Override: {model_override} para todos"}
Paralelo: Max {max_parallel} agents simultaneos
{Se once: "Modo: Ciclo unico (sem loop)"}
{Se dry_run: "Modo: DRY-RUN (apenas classificar)"}
Inicio: [data/hora atual]
Interromper: Ctrl+C ou ESC

Iniciando primeira busca...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Passo 1: Buscar Tickets Abertos

```bash
python3 scripts/jira_helper.py search "project = CS AND status NOT IN (Resolvido, Fechado, Recusado, Cancelado, Done, Closed, Resolved, Declined) AND issuetype NOT IN (Epic) ORDER BY created DESC" --max 20 --json
```

Parsear o JSON retornado. Filtrar tickets que estejam em `skip_list` ou `responded_list`.

Limitar ao `max_per_cycle`.

**Se nenhum ticket encontrado**: exibir mensagem e ir para Passo 6 (sleep).

### Passo 2: Filtrar Tickets Ja Respondidos

Para cada ticket encontrado, verificar se ja tem comentario do Suporte Inteligente:

```bash
python3 scripts/jira_helper.py get-comments {TICKET_KEY} --json
```

Analisar o JSON dos comentarios. Se QUALQUER comentario contem o texto `Suporte Inteligente` ou `[RAG-CLI]`, **remover o ticket da lista** (ja foi respondido).

Adicionar tickets removidos ao `responded_list` para nao verificar novamente.

**IMPORTANTE**: Fazer essa verificacao para TODOS os tickets antes de continuar. Usar Bash em paralelo se possivel para acelerar.

### Passo 3: Classificar Modelo de Cada Ticket

Para cada ticket, analisar o `summary` e `description` (se disponivel). Aplicar regras **em ordem** (primeira match ganha):

| # | Condicao (keywords no summary/description, case-insensitive) | Modelo |
|---|--------------------------------------------------------------|--------|
| 1 | `urgente`, `critico`, `producao`, `prod`, `seguranca`, `security`, `incidente`, `indisponivel`, `fora do ar`, `dados perdidos`, `vazamento`, `perda` | **opus** |
| 2 | `multiplos sistemas`, `integracao`, `migrac`, `arquitetura`, `infraestrutura` | **opus** |
| 3 | Prioridade = Highest ou Blocker | **opus** |
| 4 | `senha`, `acesso`, `login`, `como fazer`, `como faco`, `duvida`, `cadastro`, `email`, `permissao`, `reset`, `desbloqu`, `ativar`, `desativar` | **haiku** |
| 5 | `configurar`, `configuracao`, `trocar`, `alterar cadastro`, `atualizar dados` | **haiku** |
| 6 | Prioridade = Low ou Lowest | **haiku** |
| 7 | Default (nenhuma regra acima) | **sonnet** |

Se `model_override` estiver definido, ignorar tabela e usar o modelo especificado para todos.

### Passo 3b: Dry-Run Mode

Se `dry_run` == true, exibir tabela de classificacao e parar (ou ir pro sleep se em loop):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DRY-RUN - Classificacao de Tickets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Ticket | Summary | Prioridade | Modelo | Motivo |
|--------|---------|------------|--------|--------|
| CS-601 | Como resetar senha | Medium | haiku | keyword: senha |
| CS-602 | Erro na integracao X | High | sonnet | default |
| CS-603 | Producao fora do ar | Highest | opus | keyword: producao |

Proximo ciclo em {interval/60} minutos...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Se `once` == true, encerrar. Senao ir para Passo 6 (sleep).

### Passo 4: Lancar Task Agents

Para cada ticket (respeitando `max_parallel` simultaneos), lancar UM Task agent com o modelo classificado.

**Configuracao do Task agent:**
- `subagent_type`: "general-purpose"
- `model`: conforme classificacao do ticket
- `description`: "SD {TICKET_KEY} RAG"

**Prompt do agent:**

```
Voce e um agent de suporte inteligente para o Service Desk TT.
Sua tarefa e processar um ticket do Jira Service Desk usando a API RAG do backend para gerar uma sugestao de resposta e posta-la como COMENTARIO PRIVADO/INTERNO com links de feedback.

## REGRA CRITICA
NUNCA enviar resposta ao cliente. SOMENTE comentarios PRIVADOS/INTERNOS (invisiveis ao cliente).
A API backend ja garante isso (internal=True), mas voce NUNCA deve usar `jira_helper.py comment` (publico).
Use APENAS a API backend para postar (POST /api/rag/service-desk/post-comment/).

## Ticket
- Key: {TICKET_KEY}
- Summary: {summary}
- Prioridade: {priority}

## Credenciais API
- Token: {API_TOKEN}
- Client ID: {client_id}
- Base URL: http://localhost:11000

## Passos

1. BUSCAR descricao completa do ticket (para contexto):
   python3 scripts/jira_helper.py get {TICKET_KEY} --json --full

2. BUSCAR comentarios existentes (para contexto):
   python3 scripts/jira_helper.py get-comments {TICKET_KEY} --json

3. GERAR resposta via API RAG do backend:
   Este endpoint busca tickets similares, gera resposta via GPT-4o, calcula confianca e cria um feedback_token automaticamente.

   curl -s -X POST "http://localhost:11000/api/rag/service-desk/generate/{TICKET_KEY}?client_id={client_id}&trigger_type=new_ticket" \
     -H "Authorization: Bearer {API_TOKEN}" \
     -H "Content-Type: application/json"

   Parsear o JSON retornado. Extrair:
   - `id`: response_id (UUID da resposta gerada)
   - `confidence_score`: score de confianca (0.0 a 1.0)
   - `similar_tickets`: lista de tickets similares encontrados
   - `response_text`: texto da resposta gerada
   - `feedback_token`: token para links de feedback

   Se a API retornar erro 500 ou falhar, reportar o erro e encerrar.

4. AVALIAR a resposta gerada:
   - Ler o `response_text` retornado pela API
   - Verificar se faz sentido no contexto do ticket (passos 1 e 2)
   - Se a resposta for generica demais ou nao fizer sentido, reportar como ERRO
   - Anotar o `confidence_score` para o resumo

5. POSTAR como comentario interno via API:
   Este endpoint formata o comentario com header, links de feedback (aprovar/rejeitar) e posta como comentario interno no Jira (invisivel ao cliente).

   curl -s -X POST "http://localhost:11000/api/rag/service-desk/post-comment/{response_id}" \
     -H "Authorization: Bearer {API_TOKEN}" \
     -H "Content-Type: application/json"

   O backend formata automaticamente o comentario com:
   - Header "Sugestao automatica do Suporte Inteligente"
   - Confianca em porcentagem
   - Quantidade de tickets similares
   - Link de aprovar (feedback URL com token)
   - Link de rejeitar (feedback URL com token)

   Se ja foi postado (erro "ja postado"), considerar como sucesso.

6. RETORNAR resultado:
   Ao final, imprima um resumo no formato:
   RESULTADO: {TICKET_KEY} | confianca: {confidence_score} | similares: {N} | response_id: {id} | status: OK

   Se houve erro em qualquer passo:
   RESULTADO: {TICKET_KEY} | status: ERRO | motivo: {descricao do erro}

REGRAS:
- CRITICO: NUNCA enviar resposta ao cliente. SOMENTE comentarios PRIVADOS/INTERNOS
- PROIBIDO usar `jira_helper.py comment` (publico). SOMENTE API backend para postar
- SEMPRE usar a API backend para gerar e postar (POST /generate + POST /post-comment)
- A API backend cuida do formato do comentario, feedback_token, links e forca internal=True
- Se a API de geracao falhar, NAO tente postar manualmente via jira_helper.py
- Se a API de postagem falhar, reporte o erro com o response_id para retry manual
- Em caso de QUALQUER duvida sobre visibilidade, NAO postar
```

**Lancar ate `max_parallel` agents simultaneamente.** Se houver mais tickets que `max_parallel`, aguardar o batch atual terminar antes de lancar o proximo.

### Passo 5: Coletar Resultados

Apos todos os agents terminarem, coletar os resultados. Cada agent deve retornar uma linha `RESULTADO:` com o status.

Parsear os resultados:
- Contar sucessos e erros
- Adicionar tickets processados ao `responded_list`

### Passo 6: Resumo do Ciclo e Sleep

Exibir resumo:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[HH:MM:SS] Ciclo #N - Resumo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Processados neste ciclo: X tickets
  haiku: Y | sonnet: Z | opus: W
  Confianca: A alta | B media | C baixa
Erros neste ciclo: E tickets

Total acumulado: T tickets (F erros)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Decisao de continuar:**
- Se `once` == true: encerrar
- Se processou tickets neste ciclo → voltar ao Passo 1 IMEDIATAMENTE (sem sleep)
- Se nao encontrou tickets → sleep pelo intervalo configurado, depois voltar ao Passo 1

```bash
# Sleep (apenas quando nao ha tickets)
sleep {interval}
```

## Tratamento de Erros

Se um ticket falhar durante a execucao pelo Task agent:

1. **Agent reporta o erro** no resultado
2. **NAO posta comentario** (evita poluir o ticket)
3. **Orquestrador adiciona ao `responded_list`** para nao reprocessar neste ciclo
4. **Incrementa contador de erros**
5. **Continua com proximos tickets**

Se um Task agent inteiro falhar (crash):
1. Os tickets nao-processados voltam ao proximo ciclo
2. O orquestrador continua com os demais agents

## Regras

### REGRA #0 - SEGURANCA (INVIOLAVEL)
**NUNCA enviar resposta ao cliente. SOMENTE comentarios PRIVADOS/INTERNOS.**
- PROIBIDO usar `jira_helper.py comment` (publico) neste fluxo
- SOMENTE a API backend para postar (`POST /post-comment/` que forca `internal=True`)
- Em caso de falha na API, NAO tentar postar por outro meio
- Na duvida, NAO postar

### Regras Operacionais
1. **SEMPRE** usar `scripts/jira_helper.py` para buscar tickets e verificar comentarios
2. **SEMPRE** usar a API backend para gerar respostas e postar comentarios (com feedback integrado)
3. **SEMPRE** classificar modelo antes de executar
4. **SEMPRE** verificar comentario do Suporte Inteligente antes de processar (evitar duplicatas)
5. **SEMPRE** autenticar na API backend antes de lancar agents
6. **SEMPRE** limitar agents paralelos ao `max_parallel`
7. **SEMPRE** continuar o loop mesmo se tickets falharem
8. **SEMPRE** exibir timestamp em cada verificacao
9. **SEMPRE** manter contadores atualizados (processados, erros, ciclos, por modelo)
10. **SEMPRE** voltar a buscar imediatamente apos processar tickets (sem espera)
11. **SEMPRE** esperar intervalo configurado quando nao ha tickets
12. **NUNCA** reprocessar tickets ja respondidos
13. Se `--once` estiver ativo, executar apenas 1 ciclo e encerrar

## Exemplo de Uso

```bash
# Polling padrao (5 minutos, modelo inteligente)
/service-desk

# Polling a cada 10 minutos
/service-desk --interval 600

# Maximo 3 tickets por ciclo, 2 agents paralelos
/service-desk --max-per-cycle 3 --max-parallel 2

# Forcar tudo como sonnet
/service-desk --model-override sonnet

# Apenas classificar sem gerar respostas
/service-desk --dry-run

# Executar 1 ciclo e parar
/service-desk --once

# Pular tickets especificos
/service-desk --skip CS-123,CS-456

# Ciclo unico em dry-run
/service-desk --once --dry-run
```

## Exemplo de Saida

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SERVICE DESK RAG - Suporte Inteligente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modo: Polling a cada 5 minutos
Modelo: Inteligente (haiku/sonnet/opus por complexidade)
Paralelo: Max 3 agents simultaneos
Inicio: 2026-02-06 14:30:00
Interromper: Ctrl+C ou ESC

Iniciando primeira busca...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[14:30:00] Ciclo #1 - Buscando tickets...
           Encontrados: 6 tickets no CS
           Filtrando ja respondidos...
           Apos filtro: 3 tickets pendentes

Classificacao:
  CS-601 | Como resetar senha       | Medium  | haiku  | keyword: senha
  CS-602 | Erro na integracao SAP   | High    | sonnet | default
  CS-603 | Producao indisponivel    | Highest | opus   | keyword: producao

>> Lancando 3 Task agents em paralelo...
   Agent 1 (haiku):  CS-601 - Como resetar senha
   Agent 2 (sonnet): CS-602 - Erro na integracao SAP
   Agent 3 (opus):   CS-603 - Producao indisponivel

>> Aguardando conclusao...
   CS-601 | confianca: alta  | similares: 3 | OK
   CS-602 | confianca: media | similares: 1 | OK
   CS-603 | confianca: baixa | similares: 0 | OK

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[14:31:30] Ciclo #1 - Resumo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Processados neste ciclo: 3 tickets
  haiku: 1 | sonnet: 1 | opus: 1
  Confianca: 1 alta | 1 media | 1 baixa
Erros neste ciclo: 0 tickets

Total acumulado: 3 tickets (0 erros)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[14:31:31] Ciclo #2 - Buscando tickets...
           Encontrados: 6 tickets no CS
           Filtrando ja respondidos...
           Apos filtro: 0 tickets pendentes
           Proxima verificacao em 5 minutos...

[14:36:31] Ciclo #3 - Buscando tickets...
```

## Formato do Comentario Interno

O comentario e postado pela API backend (`POST /api/rag/service-desk/post-comment/{response_id}`), que formata automaticamente:

```
🤖 Sugestao automatica do Suporte Inteligente
Confianca: 85% | Base: 3 ticket(s) similar(es)
---

{resposta gerada pela API RAG baseada em tickets similares}

---
Avalie esta sugestao:
✅ Aprovar: https://hub.trademarketingforce.com/rag/feedback/{token}?rating=approved
❌ Rejeitar: https://hub.trademarketingforce.com/rag/feedback/{token}?rating=rejected

Seu feedback melhora as proximas sugestoes automaticamente.
```

**Feedback integrado:**
- Links de aprovar/rejeitar com token unico por resposta
- Ao aprovar: relevancia dos chunks similares e aumentada (+5%), resposta vira `verified_answer`
- Ao rejeitar: relevancia e penalizada (-3%), registra feedback para analise
- Tudo gerenciado automaticamente pelo backend

Este comentario e visivel apenas para agentes de suporte (interno), NUNCA para o cliente.
