# Comando: Create Jira (Criar Issues)

Cria issues no Jira a partir de uma descricao de funcionalidade ou bug, quebrando em subtasks se necessario. Usa o script `scripts/jira_helper.py` para todas as operacoes.

## Agent Responsavel

- **Principal**: `jira-manager` (gestor de projeto)

## Argumentos

`$ARGUMENTS`

- Descricao em texto livre da funcionalidade ou bug
- `--epic=TT-XX`: vincula a um epico especifico
- `--priority=High|Medium|Low`: define prioridade (padrao: Medium)
- `--type=Story|Task|Bug`: define tipo de issue (padrao: Story)
- `--labels=label1,label2`: adiciona labels customizadas

## Configuracao

```
Projeto: TT (Tennis Tracking)
URL: https://trademarketingforce.atlassian.net
Email: tarcisio@trademarketingforce.com
Script: scripts/jira_helper.py
```

## Fluxo de Execucao

```
┌─────────────────────────────────────────────────────────────────┐
│  /create-jira [descricao da funcionalidade ou bug]             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Analisar descricao do usuario                              │
│     - Identificar tipo (feature, bug, task, improvement)       │
│     - Identificar modulo(s) envolvido(s)                       │
│     - Identificar palavras-chave para mapeamento de epic       │
│     - Estimar complexidade geral                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Mapear epic automaticamente (ou usar --epic)               │
│     - Analisar palavras-chave na descricao                     │
│     - Mapear para epics do projeto conforme contexto           │
│     - Se ambiguo, perguntar ao usuario                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Estimar Story Points                                       │
│     - 1 SP: Trivial (~1-2h) - ajuste simples, config          │
│     - 2 SP: Simples (~2-4h) - CRUD basico, componente         │
│     - 3 SP: Moderada (~4-8h) - feature completa               │
│     - >3 SP: OBRIGATORIO quebrar em subtasks                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┴──────────────┐
              │                            │
         <=3 SP                        >3 SP
              │                            │
              ▼                            ▼
┌─────────────────────────┐  ┌───────────────────────────────────┐
│  4a. Criar issue unica  │  │  4b. Quebrar em subtasks          │
│      com SP estimado    │  │      - Backend tasks (max 3 SP)   │
│                         │  │      - Frontend tasks (max 3 SP)  │
│                         │  │      - Testes (max 2 SP)           │
│                         │  │      - Docs (max 1 SP)             │
└────────────┬────────────┘  └────────────────┬──────────────────┘
             │                                │
             └────────────┬───────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Gerar descricao estruturada                                │
│     - Contexto/motivacao                                       │
│     - Descricao tecnica                                        │
│     - Criterios de aceite (checklist)                          │
│     - Notas tecnicas (se aplicavel)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Exibir preview completo para usuario                       │
│     - Titulo, tipo, prioridade, SP                             │
│     - Epic vinculado                                           │
│     - Descricao formatada                                      │
│     - Subtasks (se houver)                                     │
│     - Pedir confirmacao: (S)im / (N)ao / (E)ditar              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Criar no Jira via jira_helper.py                           │
│     - Criar issue principal                                    │
│     - Vincular ao epic                                         │
│     - Criar subtasks (se houver)                               │
│     - Adicionar labels                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. Retornar resumo das issues criadas com links               │
└─────────────────────────────────────────────────────────────────┘
```

## Mapeamento Automatico de Modulo/Epic

A descricao eh analisada em busca de palavras-chave para mapear ao epic correto:

| Palavras-chave na Descricao | Epic | Nome do Epic |
|------------------------------|------|--------------|
| video, processamento, analise, upload, streaming, minio, s3 | TT-10 | Processamento de Video |
| rastreamento, tracknet, bola, quadra, jogador, deteccao, yolo | TT-11 | Tracking CV |
| treino, exercicio, sessao, performance, estatistica, dashboard | TT-12 | Sistema de Treino |
| usuario, auth, permissao, login, perfil, cadastro, senha | TT-13 | Autenticacao |
| infra, deploy, docker, kubernetes, redis, celery, mongodb | TT-14 | Infraestrutura |
| mobile, app, android, ios, kotlin, swift | TT-15 | Mobile Apps |

Se nenhuma palavra-chave for encontrada ou for ambiguo, perguntar ao usuario.

## Comandos jira_helper.py Utilizados

### Criar issue principal

```bash
python scripts/jira_helper.py create \
  --type Story \
  --summary "Titulo da issue" \
  --description "Descricao completa com criterios de aceite" \
  --priority Medium \
  --labels "feature,frontend,backend" \
  --parent TT-13 \
  --sp 3 \
  --json
```

### Criar subtask

```bash
python scripts/jira_helper.py create \
  --type Sub-task \
  --summary "[Backend] Titulo da subtask" \
  --description "Descricao da subtask" \
  --priority Medium \
  --labels "backend" \
  --parent TT-156 \
  --sp 2 \
  --json
```

### Vincular issue a epic (se nao feito na criacao)

```bash
python scripts/jira_helper.py link-epic TT-156 TT-13
```

### Listar epics disponiveis

```bash
python scripts/jira_helper.py epics --json
```

## Templates de Descricao

### Template: Feature (Story)

```
## Contexto
[Por que essa funcionalidade eh necessaria]

## Descricao
[O que deve ser implementado]

## Criterios de Aceite
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Notas Tecnicas
- [Detalhes de implementacao relevantes]
- [APIs externas envolvidas]
- [Impacto em outros modulos]
```

### Template: Bug

```
## Descricao do Bug
[O que esta acontecendo de errado]

## Como Reproduzir
1. Passo 1
2. Passo 2
3. Passo 3

## Comportamento Esperado
[O que deveria acontecer]

## Comportamento Atual
[O que esta acontecendo]

## Ambiente
- Browser: Chrome/Firefox
- Ambiente: Producao/Desenvolvimento

## Criterios de Aceite
- [ ] Bug corrigido
- [ ] Nao ha regressao
- [ ] Teste cobre o cenario
```

### Template: Task

```
## Descricao
[O que deve ser feito]

## Passos
1. Passo 1
2. Passo 2

## Criterios de Aceite
- [ ] Criterio 1
- [ ] Criterio 2
```

## Exemplo de Preview

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PREVIEW: Nova Issue Jira
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tipo: Story
Titulo: Adicionar filtro por periodo no processamento de videos
Epic: TT-10 (Processamento de Video)
Prioridade: Medium
Story Points: 5 -> Sera quebrada em subtasks
Labels: feature, frontend, backend

Descricao:
  ## Contexto
  A listagem de videos atualmente mostra todos os dados
  sem opcao de filtrar por periodo. Usuarios precisam
  analisar videos processados em periodos especificos.

  ## Descricao
  Implementar filtro por periodo (data inicio/fim) na
  listagem de videos, tanto no backend (API) quanto
  no frontend (componente de filtro).

  ## Criterios de Aceite
  - [ ] Usuario pode selecionar data de inicio
  - [ ] Usuario pode selecionar data de fim
  - [ ] API aceita parametros date_from e date_to
  - [ ] Listagem eh filtrada ao aplicar datas
  - [ ] Filtro persiste ao navegar entre abas
  - [ ] Validacao: data inicio < data fim

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUBTASKS (5 SP -> 3 subtasks):

  1. [Backend] Adicionar parametros de data na API
     SP: 2 | Labels: backend
     - Adicionar query params date_from/date_to
     - Filtrar query SQLAlchemy por periodo
     - Validar formato de datas

  2. [Frontend] Criar componente de filtro por periodo
     SP: 2 | Labels: frontend
     - DatePicker com inicio/fim
     - Integrar com React Query
     - Dark mode e responsividade

  3. [Testes] Adicionar testes do filtro
     SP: 1 | Labels: test
     - Teste do endpoint com filtro
     - Teste de validacao de datas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Criar issues? (S)im / (N)ao / (E)ditar
```

## Exemplo de Saida Final

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ISSUES CRIADAS COM SUCESSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TT-156: Adicionar filtro por periodo no processamento de videos
  Epic: TT-10 (Processamento de Video)
  SP: 5 (quebrada em subtasks)
  Link: https://trademarketingforce.atlassian.net/browse/TT-156

  Subtasks criadas:
  |-- TT-157: [Backend] Adicionar parametros de data (2 SP)
  |   Link: https://trademarketingforce.atlassian.net/browse/TT-157
  |-- TT-158: [Frontend] Criar componente de filtro (2 SP)
  |   Link: https://trademarketingforce.atlassian.net/browse/TT-158
  |-- TT-159: [Testes] Adicionar testes do filtro (1 SP)
      Link: https://trademarketingforce.atlassian.net/browse/TT-159

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proximos passos:
  - Use /jira TT-157 para iniciar pelo backend
  - Use /jira TT-156 para trabalhar na issue principal
  - Use /jira --list para ver o backlog atualizado
```

## Exemplo Completo - Criacao de Bug

**Entrada:**
```
/create-jira O login retorna 500 quando o usuario digita email com espaco no final
```

**Saida - Preview:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PREVIEW: Nova Issue Jira
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tipo: Bug
Titulo: Login retorna 500 quando email tem espaco no final
Epic: TT-13 (Autenticacao)
Prioridade: High
Story Points: 1
Labels: bug, backend, auth

Descricao:
  ## Descricao do Bug
  O endpoint de login retorna erro 500 quando o usuario
  digita o email com um espaco no final (ex: "user@email.com ").

  ## Como Reproduzir
  1. Acessar /login
  2. Digitar email com espaco: "user@email.com "
  3. Digitar senha correta
  4. Clicar em "Entrar"

  ## Comportamento Esperado
  Login deveria funcionar normalmente, fazendo trim do email.

  ## Comportamento Atual
  Retorna erro HTTP 500 (Internal Server Error).

  ## Criterios de Aceite
  - [ ] Email eh trimmed antes da busca no banco
  - [ ] Login funciona com espacos no inicio/fim
  - [ ] Retorna 401 para credenciais invalidas (nao 500)
  - [ ] Nao ha regressao no fluxo de login normal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Criar issue? (S)im / (N)ao / (E)ditar
```

**Saida - Final:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ISSUE CRIADA COM SUCESSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TT-160: Login retorna 500 quando email tem espaco no final
  Tipo: Bug
  Epic: TT-13 (Autenticacao)
  Prioridade: High
  SP: 1
  Labels: bug, backend, auth
  Link: https://trademarketingforce.atlassian.net/browse/TT-160

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proximos passos:
  - Use /jira TT-160 para iniciar o desenvolvimento
  - Use /jira --list para ver o backlog atualizado
```

## Estimativa de Story Points - Guia

| Complexidade | SP | Tempo Estimado | Exemplos |
|--------------|-----|----------------|----------|
| Trivial | 1 | ~1-2h | Correcao de typo, ajuste de CSS, config |
| Simples | 2 | ~2-4h | CRUD simples, componente novo, endpoint |
| Moderada | 3 | ~4-8h | Feature completa (backend + frontend) |
| Complexa | 5 | Quebrar! | Feature com multiplas telas/APIs |
| Grande | 8+ | Quebrar! | Modulo inteiro, integracao complexa |

**Regra**: Qualquer estimativa >3 SP DEVE ser quebrada em subtasks de no maximo 3 SP cada.

## Regras

1. **SEMPRE** estimar Story Points antes de criar a issue
2. **SEMPRE** quebrar em subtasks se >3 SP (maximo 3 SP por subtask)
3. **SEMPRE** mostrar preview completo antes de criar no Jira
4. **SEMPRE** adicionar labels apropriadas (tipo + area: frontend/backend/test)
5. **SEMPRE** incluir criterios de aceite na descricao
6. **SEMPRE** mapear para o epic correto usando as palavras-chave
7. **SEMPRE** usar `scripts/jira_helper.py` para criar issues (nunca curl direto)
8. **NUNCA** criar subtasks com mais de 3 SP
9. **NUNCA** criar issues sem descricao estruturada
10. **NUNCA** criar issues sem criterios de aceite
11. Ordem das subtasks: Backend -> Frontend -> Testes -> Docs
12. Se descricao for ambigua, perguntar ao usuario antes de criar
13. Bugs devem incluir "Como Reproduzir" e "Comportamento Esperado"
14. Features devem incluir "Contexto" e "Descricao" detalhada
