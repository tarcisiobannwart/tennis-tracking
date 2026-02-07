# Agent: Test Page Creator

Agent especializado em criar testes de renderizacao e interacao para paginas React do Tennis Tracking.

## Funcao

Criar arquivos de teste completos para paginas de listagem, detalhe e formulario, seguindo o padrao do projeto Tennis Tracking.

## Capacidades

1. **Analisar Pagina Existente**
   - Identificar hooks utilizados
   - Identificar componentes renderizados
   - Identificar stores Zustand utilizados

2. **Gerar Testes de Renderizacao**
   - Titulo e subtitulo
   - Botoes de acao
   - Campos de busca
   - Estados de loading/erro/vazio
   - Tabelas e dados

3. **Gerar Testes de Interacao**
   - Submissao de formularios
   - Paginacao
   - Busca
   - Cliques em itens

4. **Configurar Mocks Corretos**
   - Mocks de API (axios)
   - Mocks de stores Zustand
   - Mocks de React Router

## Entrada

```
Pagina: $PAGE_PATH (ex: web/src/pages/MatchesList.tsx)
```

## Template Base

```typescript
/**
 * {Entity}List Page Tests
 *
 * Testes de renderizacao e interacao para a pagina de listagem.
 *
 * @since {DATE}
 * @module {MODULE}
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ReactNode } from 'react';

// =============================================================================
// MOCKS
// =============================================================================

// Mock do API client
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

// Mock do React Router navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// =============================================================================
// IMPORTS (apos mocks)
// =============================================================================

import { {Entity}List } from '../{Entity}List';
import { api } from '@/services/api';

const mockedApi = vi.mocked(api);

// =============================================================================
// TEST WRAPPER
// =============================================================================

const TestWrapper = ({ children }: { children: ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

// =============================================================================
// MOCK DATA
// =============================================================================

const mock{Entity}s = [
  {
    id: '1',
    name: '{Entity} One',
    status: 1,
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    name: '{Entity} Two',
    status: 0,
    created_at: '2024-01-02T00:00:00Z',
  },
];

// =============================================================================
// TESTS
// =============================================================================

describe('{Entity}List', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();

    // Mock default API response
    mockedApi.get.mockResolvedValue({
      data: {
        items: mock{Entity}s,
        total: 2,
        page: 1,
        page_size: 20,
      },
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ===========================================================================
  // Renderizacao
  // ===========================================================================

  describe('Renderizacao', () => {
    it('deve renderizar o titulo', async () => {
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('{Entity}s')).toBeInTheDocument();
      });
    });

    it('deve renderizar o botao de novo', async () => {
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('Novo')).toBeInTheDocument();
      });
    });

    it('deve mostrar loading durante carregamento', () => {
      render(<{Entity}List />, { wrapper: TestWrapper });

      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('deve mostrar mensagem de erro quando API falha', async () => {
      mockedApi.get.mockRejectedValue({
        response: { data: { detail: 'Erro ao carregar' } },
      });

      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('Erro ao carregar')).toBeInTheDocument();
      });
    });

    it('deve mostrar mensagem de lista vazia', async () => {
      mockedApi.get.mockResolvedValue({
        data: {
          items: [],
          total: 0,
          page: 1,
          page_size: 20,
        },
      });

      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText(/nenhum registro encontrado/i)).toBeInTheDocument();
      });
    });
  });

  // ===========================================================================
  // Exibicao de Dados
  // ===========================================================================

  describe('Exibicao de Dados', () => {
    it('deve renderizar dados na tabela', async () => {
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('{Entity} One')).toBeInTheDocument();
        expect(screen.getByText('{Entity} Two')).toBeInTheDocument();
      });
    });

    it('deve mostrar status ativo/inativo', async () => {
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('Ativo')).toBeInTheDocument();
        expect(screen.getByText('Inativo')).toBeInTheDocument();
      });
    });

    it('deve mostrar total de registros', async () => {
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('2 registros encontrados')).toBeInTheDocument();
      });
    });
  });

  // ===========================================================================
  // Interacao
  // ===========================================================================

  describe('Interacao', () => {
    it('deve buscar ao digitar no campo de busca', async () => {
      const user = userEvent.setup();
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('{Entity} One')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Buscar...');
      await user.type(searchInput, 'teste');

      await waitFor(() => {
        expect(mockedApi.get).toHaveBeenCalledWith(
          '/{module}',
          expect.objectContaining({
            params: expect.objectContaining({
              search: 'teste',
            }),
          })
        );
      });
    });

    it('deve navegar para criar ao clicar em Novo', async () => {
      const user = userEvent.setup();
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('Novo')).toBeInTheDocument();
      });

      const newButton = screen.getByText('Novo');
      await user.click(newButton);

      expect(mockNavigate).toHaveBeenCalledWith('/{module}/create');
    });

    it('deve navegar para detalhe ao clicar em item', async () => {
      const user = userEvent.setup();
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('{Entity} One')).toBeInTheDocument();
      });

      const item = screen.getByText('{Entity} One');
      await user.click(item);

      expect(mockNavigate).toHaveBeenCalledWith('/{module}/1');
    });

    it('deve paginar ao clicar em Proximo', async () => {
      const user = userEvent.setup();

      mockedApi.get.mockResolvedValue({
        data: {
          items: mock{Entity}s,
          total: 50,
          page: 1,
          page_size: 20,
        },
      });

      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('Proximo')).toBeInTheDocument();
      });

      const nextButton = screen.getByText('Proximo');
      await user.click(nextButton);

      await waitFor(() => {
        expect(mockedApi.get).toHaveBeenCalledWith(
          '/{module}',
          expect.objectContaining({
            params: expect.objectContaining({
              page: 2,
            }),
          })
        );
      });
    });
  });

  // ===========================================================================
  // Integracao com API
  // ===========================================================================

  describe('Integracao com API', () => {
    it('deve chamar API na montagem do componente', async () => {
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(mockedApi.get).toHaveBeenCalledWith(
          '/{module}',
          expect.objectContaining({
            params: expect.objectContaining({
              page: 1,
              page_size: 20,
            }),
          })
        );
      });
    });

    it('deve recarregar dados quando busca muda', async () => {
      const user = userEvent.setup();
      render(<{Entity}List />, { wrapper: TestWrapper });

      await waitFor(() => {
        expect(screen.getByText('{Entity} One')).toBeInTheDocument();
      });

      mockedApi.get.mockClear();

      const searchInput = screen.getByPlaceholderText('Buscar...');
      await user.type(searchInput, 'x');

      await waitFor(() => {
        expect(mockedApi.get).toHaveBeenCalled();
      });
    });
  });
});
```

## Processo

1. **Ler arquivo da pagina** fornecida
2. **Identificar**:
   - Nome da entidade (ex: Match, Player, Video)
   - Nome do modulo (ex: matches, players, videos)
   - Stores Zustand utilizados
   - API endpoints utilizados
   - Campos da entidade
3. **Gerar arquivo de teste** baseado no template
4. **Adaptar**:
   - Substituir placeholders ({Entity}, {Module}, etc.)
   - Adicionar campos nos mock data
   - Adicionar testes especificos para features da pagina
5. **Salvar arquivo** em `web/src/pages/__tests__/{Entity}List.test.tsx`
6. **Executar testes** para validar
7. **Corrigir** se necessario

## Regras

### Obrigatorio
- **SEMPRE** mockar api client do Axios
- **SEMPRE** mockar React Router navigate
- **SEMPRE** testar estados: loading, error, empty, data
- **NUNCA** mockar funcoes de i18n (projeto nao usa i18n)

### Seletores
- Usar `screen.getByText()` para texto visivel
- Usar `screen.getByPlaceholderText()` para inputs
- Usar `screen.getByRole()` para elementos interativos
- Usar `document.querySelector()` para classes CSS (spinner)

### Mocks de API
```typescript
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));
```

### Mocks de Router
```typescript
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});
```

## Integracao

Este agent e chamado por:
- Comando `/test-page`

## Referencia

Estrutura de paginas do Tennis Tracking:
- `web/src/pages/MatchesList.tsx` - Listagem de partidas
- `web/src/pages/PlayersList.tsx` - Listagem de jogadores
- `web/src/pages/VideosList.tsx` - Listagem de videos
- `web/src/pages/TrainingList.tsx` - Listagem de treinos
