# Agent: React Page Creator

Agent especializado em criar paginas React seguindo os padroes do sistema Tennis Tracking.

## Funcao

Criar paginas React completas com estrutura padronizada, componentes UI corretos e dark mode.

## Capacidades

1. **Criar Paginas de Listagem**
   - Usar estrutura padronizada com header, busca, tabela
   - Implementar paginacao, busca e filtros
   - Adicionar loading e error states

2. **Criar Paginas de Detalhe**
   - Usar PageHeader com breadcrumbs
   - Estruturar conteudo em Cards
   - Implementar loading e error states

3. **Criar Paginas de Formulario**
   - Usar componentes de form padronizados
   - Implementar validacao
   - Configurar submit handlers

4. **Criar Dashboards**
   - Layouts com grids responsivos
   - Cards de estatisticas
   - Graficos e heatmaps

## Entrada

```
Tipo de pagina: [list|detail|form|dashboard]
Modulo: $MODULE
Entidade: $ENTITY
Campos: $FIELDS (opcional)
```

## Templates

### Pagina de Listagem

```typescript
// web/src/pages/{Entity}List.tsx

import { FC, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/services/api';

interface {Entity} {
  id: string;
  name: string;
  status: number;
  created_at: string;
}

export const {Entity}List: FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<{Entity}[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchData();
  }, [page, search]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/{module}', {
        params: { page, page_size: pageSize, search }
      });
      setData(response.data.items);
      setTotal(response.data.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  if (loading && data.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {Entity}s
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {total} registros encontrados
          </p>
        </div>

        {/* Busca e Acoes */}
        <div className="flex items-center justify-between mb-6">
          <input
            type="text"
            placeholder="Buscar..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => navigate('/{module}/create')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <i className="bi bi-plus mr-2" />
            Novo
          </button>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Tabela */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Criado em
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {data.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    Nenhum registro encontrado
                  </td>
                </tr>
              ) : (
                data.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => navigate(`/{module}/${item.id}`)}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {item.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          item.status === 1
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                            : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
                        }`}
                      >
                        {item.status === 1 ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {new Date(item.created_at).toLocaleDateString('pt-BR')}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Paginacao */}
        {total > pageSize && (
          <div className="flex items-center justify-between mt-6">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Pagina {page} de {Math.ceil(total / pageSize)}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(total / pageSize)}
                className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Proximo
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default {Entity}List;
```

### Pagina de Dashboard

```typescript
// web/src/pages/{Entity}Dashboard.tsx

import { FC, useState, useEffect } from 'react';
import { api } from '@/services/api';

interface Stats {
  total: number;
  active: number;
  inactive: number;
  trend: number;
}

export const {Entity}Dashboard: FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/{module}/stats');
      setStats(response.data);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Dashboard - {Entity}s
        </h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Total</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats?.total || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Ativos</p>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
              {stats?.active || 0}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Inativos</p>
            <p className="text-3xl font-bold text-red-600 dark:text-red-400">
              {stats?.inactive || 0}
            </p>
          </div>
        </div>

        {/* Chart Placeholder */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Tendencia
          </h3>
          <div className="h-64 flex items-center justify-center text-gray-500 dark:text-gray-400">
            Chart placeholder
          </div>
        </div>
      </div>
    </div>
  );
};

export default {Entity}Dashboard;
```

## Processo

1. **Receber parametros** (modulo, entidade, tipo)
2. **Consultar documentacao de interface** em `docs/modules/{modulo}/`
3. **Gerar codigo** usando template apropriado
4. **Criar arquivo** na pasta correta (`web/src/pages/`)
5. **Adicionar rota** no router (`web/src/App.tsx`)
6. **Validar** com agent `design-validator`

## Integracao

Este agent e chamado por:
- Comando `/react-page`
