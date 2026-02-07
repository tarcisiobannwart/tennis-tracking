# Comando: Testar Backend Python

Executa testes do backend Python e pipeline CV com pytest.

## Uso

```bash
/test-backend [modulo|--all] [opcoes]
```

### Exemplos

```bash
/test-backend --all
/test-backend api
/test-backend services
/test-backend --coverage
/test-backend -v
/test-backend --skip-jira
```

## Argumentos

| Argumento | Descricao |
|-----------|-----------|
| `[modulo]` | Nome do modulo (api, services, models, cv) |
| `--all` | Executa todos os testes |
| `--unit` | Apenas testes unitarios |
| `--integration` | Apenas testes de integracao |
| `--coverage` | Gera relatorio de cobertura |
| `-v` | Saida verbosa |
| `--list` | Lista modulos com testes |
| `-k "pattern"` | Filtra por nome |
| `--failed` | Re-executa apenas falhas |
| `--skip-jira` | Nao cria issues no Jira |

## Modulos Disponiveis

| Modulo | Descricao | Pasta |
|--------|-----------|-------|
| api | Endpoints FastAPI | `backend/app/api/` |
| services | Logica de negocio | `backend/app/services/` |
| models | Modelos MongoDB | `backend/app/models/` |
| cv | Visao computacional | `src/` |
| scoring | Sistema de placar | `src/scoring/` |
| analytics | Analise de performance | `src/analytics/` |
| tactics | Analise tatica | `src/tactics/` |
| training | Modulo de treino | `src/training/` |

## Processo

### 1. Identificar Escopo

```bash
# Se --list
ls -d backend/app/*/tests/ src/*/tests/ 2>/dev/null

# Se modulo especifico
MODULE_PATH="backend/app/$MODULE/tests/" ou "src/$MODULE/tests/"

# Se --all
pytest backend/ src/ -v --tb=short
```

### 2. Executar Testes

```bash
# Todos
pytest backend/ src/ -v --tb=short

# Backend especifico
pytest backend/app/services/tests/ -v --tb=short

# CV pipeline
pytest src/ -v --tb=short

# Com cobertura
pytest backend/ --cov=backend/app --cov-report=html --cov-report=term

# Filtrar
pytest backend/ -k "test_create" -v

# Re-executar falhas
pytest backend/ --lf -v
```

## Regras

1. **SEMPRE** usar --tb=short para traceback resumido
2. Mostrar tempo de execucao
3. Se --coverage, gerar relatorio HTML
4. Se modulo nao existir, mostrar lista

## Integracao com Jira

Quando ha falhas, criar issues automaticamente (exceto --skip-jira):

```bash
python3 scripts/jira_helper.py create \
  --type "Tarefa" \
  --summary "fix({modulo}): Corrigir {N} testes falhando" \
  --description "..." \
  --priority "{prioridade}" \
  --labels "bug,tests,{modulo}"
```

Prioridade: 1-10 falhas=Medium, 11-50=High, >50=Highest
