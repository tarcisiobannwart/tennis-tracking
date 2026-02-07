# Comando: Testar Frontend React

Executa testes do frontend React com Vitest.

## Uso

```bash
/test-frontend [modulo|--all] [opcoes]
```

### Exemplos

```bash
/test-frontend --all
/test-frontend dashboard
/test-frontend analysis
/test-frontend --coverage
/test-frontend --watch
/test-frontend --components
/test-frontend --hooks
```

## Argumentos

| Argumento | Descricao |
|-----------|-----------|
| `[modulo]` | Nome do modulo (dashboard, analysis, etc.) |
| `--all` | Executa todos os testes |
| `--components` | Apenas componentes |
| `--hooks` | Apenas hooks |
| `--services` | Apenas services/API |
| `--pages` | Apenas paginas |
| `--coverage` | Relatorio de cobertura |
| `--watch` | Modo watch |
| `--list` | Lista modulos |
| `--skip-jira` | Nao cria issues no Jira |

## Mapeamento de Modulos

| Nome | Pasta | Descricao |
|------|-------|-----------|
| dashboard | `pages/dashboard/` | Dashboard principal |
| analysis | `pages/analysis/` | Analise de partidas |
| live | `pages/live/` | Visualizacao ao vivo |
| matches | `pages/matches/` | Historico de partidas |
| players | `pages/players/` | Perfis de jogadores |
| settings | `pages/settings/` | Configuracoes |
| components | `components/` | Componentes reutilizaveis |
| hooks | `hooks/` | Custom hooks |
| services | `services/` | API clients |
| stores | `stores/` | State management (Zustand) |

## Processo

### Executar Testes

```bash
cd web

# Todos
npm run test -- --run

# Modulo
npm run test -- --run src/pages/analysis/__tests__/

# Coverage
npm run test -- --run --coverage

# Watch
npm run test -- src/pages/dashboard/__tests__/

# Filtrar
npm run test -- --run -t "should render"
```

## Regras

1. **SEMPRE** executar a partir de `web/`
2. **SEMPRE** usar `--run` para execucao unica
3. Se modulo nao existir, mostrar lista
4. Mostrar progresso durante execucao

## Integracao com Jira

Quando ha falhas, criar issues automaticamente (exceto --skip-jira):

```bash
python3 scripts/jira_helper.py create \
  --type "Tarefa" \
  --summary "fix(frontend/{modulo}): Corrigir {N} testes falhando" \
  --description "..." \
  --priority "{prioridade}" \
  --labels "bug,tests,frontend,{modulo}"
```
