# Comando: Testar Modulo Completo

Executa testes de um modulo inteiro do Tennis Tracking, cobrindo paginas, componentes e hooks.

## Argumentos

`$ARGUMENTS` - Nome do modulo a testar (ex: `clients`, `hr`, `finance`, `users`, `crm`, `observability`)

## Mapeamento de Modulos

| Modulo (argumento) | Paginas | Componentes | Permissao |
|---------------------|---------|-------------|-----------|
| `clients` / `clientes` | Clients.tsx, ClientDetail.tsx | components/clients/* | clients:view |
| `hr` / `funcionarios` | HR.tsx | - | hr:view |
| `finance` / `financeiro` | FinanceConciliation.tsx, FinanceCosts.tsx, FinanceReports.tsx | components/finance/* | finance:view |
| `users` / `usuarios` | Users.tsx | - | users:view |
| `crm` | Opportunities.tsx, OpportunityDetail.tsx, Campaigns.tsx | components/crm/* | opportunities:view |
| `observability` | Observability.tsx, Logs.tsx | - | observability:view |
| `jira` | Jira.tsx | - | jira:view |
| `tenants` | (redirect para Clients) | - | clients:view |
| `expenses` / `despesas` | Expenses.tsx, ExpenseManagement.tsx | components/expenses/* | expenses:view |
| `projects` / `projetos` | ProjectManagement.tsx | - | finance:view |
| `dashboard` | Dashboard.tsx | components/dashboard/* | - |
| `integrations` / `integracoes` | Integrations.tsx | - | admin:access |
| `communication` / `comunicacao` | CommunicationDashboard.tsx | components/communication/* | communication:view |
| `persons` / `pessoas` | Persons.tsx | - | persons:view |
| `teams` / `equipes` | Teams.tsx | - | teams:view |
| `security` / `seguranca` | Security.tsx | - | - |
| `infra` | Functions.tsx, ServerOperations.tsx, Migrations.tsx, DataMigrations.tsx | components/functions/* | functions:view |

## Fluxo de Execucao

```
┌─────────────────────────────────────────────────────────┐
│  1. Identificar modulo pelo argumento                    │
│     (aceita portugues ou ingles)                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  2. Listar arquivos do modulo                            │
│     - Paginas em frontend/src/pages/                     │
│     - Componentes em frontend/src/components/{modulo}/   │
│     - Hooks em frontend/src/hooks/ (se existir)          │
│     - Tipos em frontend/src/types/                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  3. Verificar testes existentes                          │
│     - frontend/src/pages/__tests__/                      │
│     - frontend/src/components/{modulo}/__tests__/        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  4. Gerar testes faltantes                               │
│     - Usar /test-page para cada pagina                   │
│     - Criar testes de componentes                        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  5. Executar testes do modulo                            │
│     cd frontend && npx vitest --run src/**/{modulo}*     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  6. Reportar resultados                                  │
│     - Testes passando / falhando                         │
│     - Cobertura por arquivo                              │
│     - Sugestoes de melhoria                              │
└─────────────────────────────────────────────────────────┘
```

## Pre-requisitos

### Verificar Vitest

```bash
# Verificar se vitest esta disponivel
cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking/frontend
npx vitest --version 2>/dev/null || echo "VITEST NAO INSTALADO"
```

### Instalar Dependencias (se necessario)

```bash
cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking/frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitest/coverage-v8
```

### Verificar Configuracao

Arquivo `frontend/vitest.config.ts` deve existir:

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
```

## Categorias de Teste por Tipo de Arquivo

### Pagina de Listagem

| Categoria | O que testar |
|-----------|-------------|
| Renderizacao | Titulo, busca, botao criar, tabela |
| Dados | Loading, dados carregados, lista vazia, erro |
| Busca | Filtrar por texto, limpar busca |
| Filtros | Filtrar por status, resetar filtros |
| Ordenacao | Clicar header, alternar asc/desc |
| Navegacao | Clicar item navega para detalhe |
| Permissoes | Botoes visiveis/ocultos por permissao |

### Pagina de Detalhe

| Categoria | O que testar |
|-----------|-------------|
| Renderizacao | Dados do item, abas, botoes acao |
| Dados | Loading, dados carregados, item nao encontrado |
| Abas | Alternar entre abas, conteudo correto por aba |
| Acoes | Editar, excluir, voltar |
| Permissoes | Botoes visiveis/ocultos por permissao |

### Componente

| Categoria | O que testar |
|-----------|-------------|
| Renderizacao | Props renderizadas corretamente |
| Variantes | Diferentes estilos (variant, size) |
| Interacao | Clicks, hover, onChange |
| Estados | Disabled, loading, erro |
| Acessibilidade | aria-labels, roles |

## Comandos de Execucao

```bash
# Testar modulo completo (todas as paginas e componentes)
cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking/frontend

# Por nome do modulo
npx vitest --run src/pages/__tests__/Clients*
npx vitest --run src/pages/__tests__/HR*
npx vitest --run src/pages/__tests__/Users*
npx vitest --run src/pages/__tests__/Finance*

# Incluir componentes do modulo
npx vitest --run src/**/clients/**
npx vitest --run src/**/finance/**
npx vitest --run src/**/crm/**

# Todos os testes
npx vitest --run

# Com cobertura
npx vitest --run --coverage

# Modo watch (durante desenvolvimento)
npx vitest src/**/clients/**
```

## Estrutura de Mocks do TMF

### Mock do AuthContext (padrao para todos os testes)

```typescript
vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 1,
      email: 'test@trademarketingforce.com',
      full_name: 'Usuario Teste',
      role: { id: 1, name: 'CEO', level: 100, permissions: [] },
    },
    isAuthenticated: true,
    hasPermission: vi.fn(() => true),
    hasAnyPermission: vi.fn(() => true),
    hasRoleLevel: vi.fn(() => true),
  }),
}))
```

### Mock do React Router (padrao)

```typescript
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ id: '1' }),
  }
})
```

### Mock da API (por modulo)

```typescript
// Clients
vi.mock('../../services/api', () => ({
  dashboardApi: {
    getClientHoursUsage: vi.fn().mockResolvedValue({
      period: { year: 2026, month: 1, month_name: 'Janeiro' },
      totals: { contracted_hours: 100, consumed_hours: 50, remaining_hours: 50, usage_percentage: 50, total_clients: 3 },
      clients: [
        { client_id: '1', client_code: 'CLI001', client_name: 'Cliente Alpha', contracted_hours: 40, consumed_hours: 20, remaining_hours: 20, usage_percentage: 50, status: 'ok' },
        { client_id: '2', client_code: 'CLI002', client_name: 'Cliente Beta', contracted_hours: 60, consumed_hours: 55, remaining_hours: 5, usage_percentage: 91, status: 'exceeded' },
      ],
    }),
  },
}))

// Users
vi.mock('../../services/api', () => ({
  usersApi: {
    list: vi.fn().mockResolvedValue({
      data: [
        { id: 1, email: 'admin@tmf.com', full_name: 'Admin', is_active: true, role: { name: 'CEO' } },
        { id: 2, email: 'dev@tmf.com', full_name: 'Developer', is_active: true, role: { name: 'Dev Pleno' } },
      ],
    }),
    listRoles: vi.fn().mockResolvedValue({
      data: [
        { id: 1, name: 'CEO', level: 100 },
        { id: 2, name: 'Gerente', level: 80 },
      ],
    }),
  },
}))

// Finance
vi.mock('../../services/api', () => ({
  financeApi: {
    getCosts: vi.fn().mockResolvedValue({ data: [] }),
    getReports: vi.fn().mockResolvedValue({ data: [] }),
    getConciliation: vi.fn().mockResolvedValue({ data: [] }),
  },
}))
```

## Exemplo de Saida

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TESTES DO MODULO: clients
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivos do modulo:
  Paginas:
    - frontend/src/pages/Clients.tsx
    - frontend/src/pages/ClientDetail.tsx
  Componentes:
    - frontend/src/components/clients/ClientDetailPanel.tsx
    - frontend/src/components/clients/ClientDatabaseTab.tsx
    - frontend/src/components/clients/ClientsYearlyChart.tsx
    - (mais 6 arquivos)

Testes encontrados:
  - frontend/src/pages/__tests__/Clients.test.tsx
  - Nao encontrado: ClientDetail.test.tsx

Testes gerados:
  - frontend/src/pages/__tests__/ClientDetail.test.tsx (NOVO)

Resultados:
  Clients.test.tsx .............. 8/8 passando
  ClientDetail.test.tsx ........ 5/5 passando
  Total: 13 testes, 13 passando, 0 falhando

Cobertura:
  Clients.tsx ............ 78%
  ClientDetail.tsx ....... 65%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Regras

1. **SEMPRE** verificar se Vitest esta instalado antes de rodar
2. **NUNCA** criar mocks de i18n/traducao (TMF nao usa)
3. **SEMPRE** usar textos em portugues nos nomes dos testes
4. **SEMPRE** testar dark mode se o componente usa classes `dark:`
5. **SEMPRE** testar permissoes quando a pagina usa `hasPermission`
6. **SEMPRE** limpar mocks no `beforeEach`
7. Executar a partir de `frontend/`: `cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking/frontend`
8. Usar `npx vitest --run` (modo nao-interativo)
