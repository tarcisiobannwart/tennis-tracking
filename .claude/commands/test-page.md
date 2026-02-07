# Comando: Gerar Testes para Pagina React

Gera testes unitarios para uma pagina React do Tennis Tracking usando React Testing Library e Vitest.

## Argumentos

`$ARGUMENTS` - Nome da pagina a testar (ex: `Users`, `Clients`, `HR`, `FinanceCosts`)

## Pre-requisitos

O projeto TMF atualmente **nao tem Vitest configurado**. Antes de rodar testes, verificar se as dependencias estao instaladas:

```bash
# Verificar se vitest esta instalado
cd frontend && npx vitest --version 2>/dev/null || echo "Vitest nao instalado"
```

Se nao estiver instalado, adicionar ao projeto:

```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

E criar/atualizar `frontend/vitest.config.ts`:

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

E criar `frontend/src/test/setup.ts`:

```typescript
import '@testing-library/jest-dom'
```

## Estrutura de Testes

```
frontend/src/
├── test/
│   ├── setup.ts              # Setup global (jest-dom)
│   ├── mocks/
│   │   ├── api.ts            # Mock do services/api
│   │   ├── auth.ts           # Mock do AuthContext
│   │   ├── theme.ts          # Mock do ThemeContext
│   │   ├── router.ts         # Mock do react-router-dom
│   │   └── query.ts          # Wrapper do QueryClientProvider
│   └── utils.ts              # Helpers de teste
├── pages/
│   ├── __tests__/
│   │   ├── Users.test.tsx
│   │   ├── Clients.test.tsx
│   │   ├── HR.test.tsx
│   │   └── ...
└── components/
    ├── __tests__/
    │   ├── ExportButtons.test.tsx
    │   └── ...
```

## Mocks Necessarios

### Mock do AuthContext

```typescript
// frontend/src/test/mocks/auth.ts
import { vi } from 'vitest'

export const mockAuthContext = {
  user: {
    id: 1,
    email: 'test@trademarketingforce.com',
    full_name: 'Usuario Teste',
    is_active: true,
    role: {
      id: 1,
      name: 'CEO',
      level: 100,
      permissions: [
        { id: 1, name: 'clients:view', description: '' },
        { id: 2, name: 'clients:create', description: '' },
        { id: 3, name: 'clients:edit', description: '' },
        { id: 4, name: 'clients:delete', description: '' },
        { id: 5, name: 'users:view', description: '' },
        { id: 6, name: 'users:create', description: '' },
        { id: 7, name: 'hr:view', description: '' },
        { id: 8, name: 'finance:view', description: '' },
        { id: 9, name: 'admin:access', description: '' },
      ],
    },
  },
  isAuthenticated: true,
  isLoading: false,
  accessToken: 'mock-token',
  refreshToken: 'mock-refresh',
  mfaRequired: false,
  mfaToken: null,
  login: vi.fn(),
  logout: vi.fn(),
  hasPermission: vi.fn((perm: string) => true),
  hasAnyPermission: vi.fn(() => true),
  hasRoleLevel: vi.fn((level: number) => true),
  setMFAToken: vi.fn(),
  clearMFAToken: vi.fn(),
}

// Mock do hook useAuth
export const mockUseAuth = vi.fn(() => mockAuthContext)
```

### Mock do ThemeContext

```typescript
// frontend/src/test/mocks/theme.ts
import { vi } from 'vitest'

export const mockThemeContext = {
  theme: 'light' as const,
  toggleTheme: vi.fn(),
  setTheme: vi.fn(),
}

export const mockUseTheme = vi.fn(() => mockThemeContext)
```

### Mock da API

```typescript
// frontend/src/test/mocks/api.ts
import { vi } from 'vitest'

// Mock generico para API responses
export function createMockApi<T>(data: T) {
  return vi.fn().mockResolvedValue({ data })
}

// Mocks especificos por modulo
export const mockUsersApi = {
  list: vi.fn().mockResolvedValue({ data: [] }),
  getById: vi.fn().mockResolvedValue({ data: null }),
  create: vi.fn().mockResolvedValue({ data: {} }),
  update: vi.fn().mockResolvedValue({ data: {} }),
  delete: vi.fn().mockResolvedValue({}),
  listRoles: vi.fn().mockResolvedValue({ data: [] }),
}

export const mockDashboardApi = {
  getStats: vi.fn().mockResolvedValue({ data: {} }),
  getClientHoursUsage: vi.fn().mockResolvedValue({
    period: { year: 2026, month: 1, month_name: 'Janeiro' },
    totals: { contracted_hours: 100, consumed_hours: 50, remaining_hours: 50, usage_percentage: 50, total_clients: 5 },
    clients: [],
  }),
}
```

### Wrapper de Teste

```typescript
// frontend/src/test/utils.ts
import { render, type RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '../contexts/ThemeContext'
import type { ReactElement } from 'react'

// QueryClient para testes (sem retries, sem cache)
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

// Wrapper com todos os providers
function AllProviders({ children }: { children: React.ReactNode }) {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

// Render customizado com providers
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllProviders, ...options })
}

// Re-exportar tudo do testing-library
export * from '@testing-library/react'
export { renderWithProviders as render }
```

## Template: Teste de Pagina de Listagem

```typescript
// frontend/src/pages/__tests__/NomePagina.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../test/utils'
import NomePagina from '../NomePagina'

// Mock do AuthContext
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

// Mock da API
vi.mock('../../services/api', () => ({
  nomeApi: {
    list: vi.fn().mockResolvedValue({
      data: [
        { id: 1, name: 'Item 1', status: 'active' },
        { id: 2, name: 'Item 2', status: 'inactive' },
        { id: 3, name: 'Item 3', status: 'active' },
      ],
    }),
  },
}))

// Mock do react-router-dom (manter navigate)
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({}),
  }
})

describe('NomePagina', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ============================================================
  // Renderizacao
  // ============================================================

  describe('Renderizacao', () => {
    it('deve renderizar o titulo da pagina', async () => {
      render(<NomePagina />)
      await waitFor(() => {
        expect(screen.getByText('Titulo do Modulo')).toBeInTheDocument()
      })
    })

    it('deve renderizar o campo de busca', async () => {
      render(<NomePagina />)
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/buscar/i)).toBeInTheDocument()
      })
    })

    it('deve renderizar o botao de criar quando tem permissao', async () => {
      render(<NomePagina />)
      await waitFor(() => {
        expect(screen.getByText(/novo/i)).toBeInTheDocument()
      })
    })
  })

  // ============================================================
  // Carregamento de Dados
  // ============================================================

  describe('Carregamento de Dados', () => {
    it('deve exibir loading enquanto carrega', () => {
      render(<NomePagina />)
      expect(screen.getByText(/carregando/i)).toBeInTheDocument()
    })

    it('deve exibir dados apos carregamento', async () => {
      render(<NomePagina />)
      await waitFor(() => {
        expect(screen.getByText('Item 1')).toBeInTheDocument()
        expect(screen.getByText('Item 2')).toBeInTheDocument()
      })
    })

    it('deve exibir mensagem quando nao ha dados', async () => {
      // Override mock para lista vazia
      const { nomeApi } = await import('../../services/api')
      vi.mocked(nomeApi.list).mockResolvedValueOnce({ data: [] })

      render(<NomePagina />)
      await waitFor(() => {
        expect(screen.getByText(/nenhum/i)).toBeInTheDocument()
      })
    })
  })

  // ============================================================
  // Busca e Filtros
  // ============================================================

  describe('Busca e Filtros', () => {
    it('deve filtrar itens ao digitar na busca', async () => {
      const user = userEvent.setup()
      render(<NomePagina />)

      await waitFor(() => {
        expect(screen.getByText('Item 1')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/buscar/i)
      await user.type(searchInput, 'Item 1')

      expect(screen.getByText('Item 1')).toBeInTheDocument()
      expect(screen.queryByText('Item 2')).not.toBeInTheDocument()
    })

    it('deve limpar busca ao clicar no X', async () => {
      const user = userEvent.setup()
      render(<NomePagina />)

      await waitFor(() => {
        expect(screen.getByText('Item 1')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/buscar/i)
      await user.type(searchInput, 'Item 1')

      // Clicar no botao de limpar
      const clearButton = screen.getByTitle(/limpar/i) || screen.getByRole('button', { name: /limpar|clear/i })
      await user.click(clearButton)

      // Todos os itens devem estar visiveis novamente
      expect(screen.getByText('Item 1')).toBeInTheDocument()
      expect(screen.getByText('Item 2')).toBeInTheDocument()
    })

    it('deve filtrar por status', async () => {
      const user = userEvent.setup()
      render(<NomePagina />)

      await waitFor(() => {
        expect(screen.getByText('Item 1')).toBeInTheDocument()
      })

      const statusFilter = screen.getByDisplayValue(/todos/i)
      await user.selectOptions(statusFilter, 'active')

      expect(screen.getByText('Item 1')).toBeInTheDocument()
      expect(screen.queryByText('Item 2')).not.toBeInTheDocument()
    })
  })

  // ============================================================
  // Interacoes
  // ============================================================

  describe('Interacoes', () => {
    it('deve navegar ao clicar em um item', async () => {
      const user = userEvent.setup()
      render(<NomePagina />)

      await waitFor(() => {
        expect(screen.getByText('Item 1')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Item 1'))
      expect(mockNavigate).toHaveBeenCalled()
    })
  })

  // ============================================================
  // Permissoes
  // ============================================================

  describe('Permissoes', () => {
    it('deve ocultar botao criar quando sem permissao', async () => {
      vi.mocked(
        (await import('../../contexts/AuthContext')).useAuth
      ).mockReturnValueOnce({
        ...vi.mocked((await import('../../contexts/AuthContext')).useAuth)(),
        hasPermission: vi.fn(() => false),
      })

      render(<NomePagina />)
      await waitFor(() => {
        expect(screen.queryByText(/novo/i)).not.toBeInTheDocument()
      })
    })
  })
})
```

## Template: Teste de Pagina de Detalhe

```typescript
// frontend/src/pages/__tests__/NomeDetail.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../test/utils'
import NomeDetail from '../NomeDetail'

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    hasPermission: vi.fn(() => true),
    hasRoleLevel: vi.fn(() => true),
  }),
}))

vi.mock('../../services/api', () => ({
  nomeApi: {
    getById: vi.fn().mockResolvedValue({
      data: {
        id: 1,
        name: 'Item Detalhe',
        description: 'Descricao do item',
        status: 'active',
        created_at: '2026-01-15T10:00:00Z',
      },
    }),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ id: '1' }),
  }
})

describe('NomeDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('deve renderizar dados do item', async () => {
    render(<NomeDetail />)
    await waitFor(() => {
      expect(screen.getByText('Item Detalhe')).toBeInTheDocument()
    })
  })

  it('deve exibir loading enquanto carrega', () => {
    render(<NomeDetail />)
    expect(screen.getByText(/carregando/i)).toBeInTheDocument()
  })

  it('deve navegar ao clicar em voltar', async () => {
    const user = userEvent.setup()
    render(<NomeDetail />)

    await waitFor(() => {
      expect(screen.getByText('Item Detalhe')).toBeInTheDocument()
    })

    // Clicar no botao voltar (ArrowLeft)
    const backButton = screen.getAllByRole('button')[0]
    await user.click(backButton)
    expect(mockNavigate).toHaveBeenCalledWith(-1)
  })

  it('deve alternar entre abas', async () => {
    const user = userEvent.setup()
    render(<NomeDetail />)

    await waitFor(() => {
      expect(screen.getByText('Item Detalhe')).toBeInTheDocument()
    })

    // Clicar na aba "Historico"
    const historyTab = screen.getByText(/historico/i)
    await user.click(historyTab)

    // Verificar conteudo da aba
    expect(screen.getByText(/historico/i)).toBeInTheDocument()
  })
})
```

## Executando Testes

```bash
# Rodar todos os testes
cd frontend && npx vitest --run

# Rodar teste especifico
cd frontend && npx vitest --run src/pages/__tests__/Users.test.tsx

# Rodar em modo watch
cd frontend && npx vitest

# Com cobertura
cd frontend && npx vitest --run --coverage

# Filtrar por nome
cd frontend && npx vitest --run -t "deve renderizar"
```

## Padroes de Teste

### Nomenclatura

- Describe: nome do componente (`describe('Users', () => {...})`)
- Sub-describe: categoria (`describe('Renderizacao', () => {...})`)
- It: `deve + verbo` (`it('deve renderizar o titulo', ...)`)
- Tudo em portugues

### Categorias de Teste

1. **Renderizacao** - Verifica se elementos estao na tela
2. **Carregamento de Dados** - Loading, dados, erro, vazio
3. **Busca e Filtros** - Filtragem, busca textual, ordenacao
4. **Interacoes** - Cliques, navegacao, formularios
5. **Permissoes** - Verificacao de acesso
6. **Estados** - Modais, abas, toggles

### Boas Praticas

- Usar `waitFor` para operacoes assincronas
- Usar `userEvent.setup()` (nao `fireEvent`)
- Preferir queries semanticas (`getByRole`, `getByText`, `getByPlaceholderText`)
- Mock de API no nivel do modulo (vi.mock)
- Limpar mocks no `beforeEach`
- Testar estados de loading, erro e vazio
- Testar permissoes (com e sem acesso)

## Checklist de Validacao

- [ ] Arquivo de teste criado em `pages/__tests__/` ou `components/__tests__/`
- [ ] Mocks de AuthContext, API e Router configurados
- [ ] Testes de renderizacao basica
- [ ] Testes de carregamento de dados (loading, sucesso, erro, vazio)
- [ ] Testes de busca e filtros
- [ ] Testes de interacao (cliques, navegacao)
- [ ] Testes de permissoes
- [ ] Nomes dos testes em portugues
- [ ] Sem mocks de i18n (TMF nao usa)
- [ ] `cd frontend && npx vitest --run` passa
