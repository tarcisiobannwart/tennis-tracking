# Comando: Criar Pagina React

Cria uma nova pagina React para o Tennis Tracking seguindo os padroes do projeto.

## Argumentos

`$ARGUMENTS` - Nome da pagina e tipo (ex: `ClientsList list`, `ClientDetail detail`, `ClientForm form`)

Formato: `<NomePagina> <tipo>`
- `list` - Pagina de listagem com tabela, filtros, busca
- `detail` - Pagina de detalhe com abas e informacoes
- `form` - Pagina/modal de formulario para criar/editar

Se o tipo nao for informado, assumir `list`.

## Estrutura do Projeto

```
frontend/src/
├── pages/              # Paginas da aplicacao
│   ├── Clients.tsx
│   ├── ClientDetail.tsx
│   ├── Users.tsx
│   ├── HR.tsx
│   ├── FinanceCosts.tsx
│   ├── Observability.tsx
│   └── ...
├── components/         # Componentes reutilizaveis
│   ├── Layout.tsx
│   ├── ProtectedRoute.tsx
│   ├── ExportButtons.tsx
│   ├── clients/        # Componentes do modulo Clients
│   ├── finance/        # Componentes do modulo Finance
│   ├── crm/            # Componentes do modulo CRM
│   ├── dashboard/      # Componentes do Dashboard
│   └── ...
├── services/
│   └── api.ts          # Axios instance e API clients
├── contexts/
│   ├── AuthContext.tsx  # useAuth, hasPermission, hasRoleLevel
│   └── ThemeContext.tsx # useTheme, toggleTheme
├── types/              # TypeScript types
│   ├── auth.ts
│   ├── finance.ts
│   ├── crm.ts
│   └── ...
└── utils/
    ├── export.ts       # formatCurrency, exportacao
    └── format.ts       # formatadores
```

## Modulos do TMF

| Modulo | Paginas | Permissao | Jira Epic |
|--------|---------|-----------|-----------|
| Clientes | Clients, ClientDetail | clients:view | TT-11 |
| RH | HR | hr:view | TT-12 |
| Financeiro | FinanceConciliation, FinanceCosts, FinanceReports | finance:view | TT-13 |
| CRM | Opportunities, OpportunityDetail, Campaigns | opportunities:view | TT-14 |
| Infraestrutura | Functions, Logs, Observability, ServerOperations | functions:view | TT-15 |
| Configuracoes | Users, Security, Integrations, MenuAccess | users:view | TT-16 |
| Pessoas | Persons, Teams | persons:view | - |
| Projetos | ProjectManagement | finance:view | - |
| Comunicacao | CommunicationDashboard | communication:view | - |

## Stack Tecnologico

- **React 18** com functional components e hooks
- **TypeScript** com tipagem estrita
- **TailwindCSS** para estilizacao (utility-first)
- **React Query** (@tanstack/react-query) para data fetching
- **React Router DOM v6** para navegacao
- **Lucide React** para icones
- **Axios** para HTTP (via services/api.ts)
- **Recharts** para graficos
- **react-hot-toast** para notificacoes
- **date-fns** para manipulacao de datas

## Regras Obrigatorias

1. **Sem i18n/traducoes** - Todo texto diretamente em portugues (pt-BR)
2. **Sem clsx** - Usar template literals para classes condicionais
3. **Functional components** com `export default function NomePagina()`
4. **useQuery** para busca de dados (nunca useEffect + fetch manual para listagens)
5. **Tipagem completa** em TypeScript (interfaces para props, responses, etc.)
6. **Dark mode** suportado via classes `dark:` do Tailwind
7. **Responsividade** com classes Tailwind (sm:, md:, lg:)
8. **Lucide React** para icones (nunca HeroIcons ou FontAwesome)
9. **Docker only** - Porta 11001 para frontend, 11000 para backend API
10. **Consultar docs** - Verificar `docs/modules/{modulo}/interfaces/` antes de criar

## Template: Pagina de Listagem (list)

```tsx
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Search, Plus, Edit2, Trash2, Filter, X,
  Loader2, AlertCircle, ChevronDown, ChevronUp,
  // ... outros icones necessarios
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
// import { nomeApi } from '../services/api'  // Importar API client
// import ExportButtons from '../components/ExportButtons'

// Tipos
interface NomeItem {
  id: number
  name: string
  status: string
  created_at: string
  // ... outros campos
}

interface NomeListResponse {
  items: NomeItem[]
  total: number
}

export default function NomePagina() {
  const navigate = useNavigate()
  const { hasPermission } = useAuth()

  // Estados de filtro e busca
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  // Query de dados
  const { data, isLoading, error, refetch } = useQuery<NomeListResponse>({
    queryKey: ['nome-lista', filterStatus],
    queryFn: () => Promise.resolve({ items: [], total: 0 }), // TODO: trocar por API real
  })

  // Filtro local (busca por texto)
  const filteredItems = useMemo(() => {
    if (!data?.items) return []
    return data.items
      .filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .filter(item =>
        filterStatus === 'all' ? true : item.status === filterStatus
      )
      .sort((a, b) => {
        const modifier = sortOrder === 'asc' ? 1 : -1
        return a.name.localeCompare(b.name) * modifier
      })
  }, [data, searchTerm, filterStatus, sortBy, sortOrder])

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Carregando...</span>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <span className="ml-2 text-red-600 dark:text-red-400">
          Erro ao carregar dados. Tente novamente.
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Nome do Modulo
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Descricao breve do modulo
          </p>
        </div>
        {hasPermission('modulo:create') && (
          <button
            onClick={() => {/* abrir modal ou navegar */}}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Novo Item
          </button>
        )}
      </div>

      {/* Filtros e Busca */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por nome..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="w-4 h-4 text-gray-400 hover:text-gray-600" />
            </button>
          )}
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value="all">Todos os status</option>
          <option value="active">Ativo</option>
          <option value="inactive">Inativo</option>
        </select>
      </div>

      {/* Contador de resultados */}
      <div className="text-sm text-gray-500 dark:text-gray-400">
        {filteredItems.length} {filteredItems.length === 1 ? 'resultado' : 'resultados'}
      </div>

      {/* Tabela */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-gray-100"
                  onClick={() => {
                    if (sortBy === 'name') {
                      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
                    } else {
                      setSortBy('name')
                      setSortOrder('asc')
                    }
                  }}
                >
                  <div className="flex items-center gap-1">
                    Nome
                    {sortBy === 'name' && (
                      sortOrder === 'asc'
                        ? <ChevronUp className="w-3 h-3" />
                        : <ChevronDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Acoes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    Nenhum item encontrado
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                    onClick={() => navigate(`/modulo/${item.id}`)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {item.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        item.status === 'active'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {item.status === 'active' ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={(e) => { e.stopPropagation(); /* editar */ }}
                          className="p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                          title="Editar"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); /* deletar */ }}
                          className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                          title="Excluir"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
```

## Template: Pagina de Detalhe (detail)

```tsx
import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft, Edit2, Trash2, Loader2, AlertCircle,
  // ... outros icones
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
// import { nomeApi } from '../services/api'

interface NomeDetalhe {
  id: number
  name: string
  description: string
  status: string
  created_at: string
  // ... outros campos
}

type TabId = 'geral' | 'historico' | 'configuracoes'

export default function NomeDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { hasPermission } = useAuth()
  const [activeTab, setActiveTab] = useState<TabId>('geral')

  const { data, isLoading, error } = useQuery<NomeDetalhe>({
    queryKey: ['nome-detalhe', id],
    queryFn: () => Promise.resolve({} as NomeDetalhe), // TODO: trocar por API real
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Carregando...</span>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <span className="ml-2 text-red-600 dark:text-red-400">
          Erro ao carregar dados.
        </span>
      </div>
    )
  }

  const tabs: { id: TabId; label: string }[] = [
    { id: 'geral', label: 'Geral' },
    { id: 'historico', label: 'Historico' },
    { id: 'configuracoes', label: 'Configuracoes' },
  ]

  return (
    <div className="space-y-6">
      {/* Header com botao voltar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {data.name}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              ID: {data.id}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {hasPermission('modulo:edit') && (
            <button
              onClick={() => {/* editar */}}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <Edit2 className="w-4 h-4" />
              Editar
            </button>
          )}
          {hasPermission('modulo:delete') && (
            <button
              onClick={() => {/* confirmar exclusao */}}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              <Trash2 className="w-4 h-4" />
              Excluir
            </button>
          )}
        </div>
      </div>

      {/* Abas */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-4 -mb-px">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Conteudo da aba */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        {activeTab === 'geral' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400">
                Nome
              </label>
              <p className="mt-1 text-gray-900 dark:text-white">{data.name}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 dark:text-gray-400">
                Status
              </label>
              <span className={`inline-flex items-center mt-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                data.status === 'active'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
              }`}>
                {data.status === 'active' ? 'Ativo' : 'Inativo'}
              </span>
            </div>
            {/* Adicionar mais campos conforme necessario */}
          </div>
        )}

        {activeTab === 'historico' && (
          <p className="text-gray-500 dark:text-gray-400">
            Historico em desenvolvimento...
          </p>
        )}

        {activeTab === 'configuracoes' && (
          <p className="text-gray-500 dark:text-gray-400">
            Configuracoes em desenvolvimento...
          </p>
        )}
      </div>
    </div>
  )
}
```

## Template: Pagina de Formulario (form)

```tsx
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft, Save, Loader2, AlertCircle,
} from 'lucide-react'
import toast from 'react-hot-toast'
// import { nomeApi } from '../services/api'

interface NomeFormData {
  name: string
  description: string
  status: string
  // ... outros campos
}

const initialFormData: NomeFormData = {
  name: '',
  description: '',
  status: 'active',
}

export default function NomeForm() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isEditing = !!id

  const [formData, setFormData] = useState<NomeFormData>(initialFormData)
  const [errors, setErrors] = useState<Partial<Record<keyof NomeFormData, string>>>({})

  // Carregar dados para edicao
  const { isLoading: isLoadingData } = useQuery({
    queryKey: ['nome-detalhe', id],
    queryFn: () => Promise.resolve({} as NomeFormData), // TODO: trocar por API real
    enabled: isEditing,
    onSuccess: (data: NomeFormData) => {
      setFormData(data)
    },
  })

  // Mutation para salvar
  const mutation = useMutation({
    mutationFn: async (data: NomeFormData) => {
      // TODO: trocar por API real
      if (isEditing) {
        // return nomeApi.update(id!, data)
      } else {
        // return nomeApi.create(data)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nome-lista'] })
      toast.success(isEditing ? 'Atualizado com sucesso!' : 'Criado com sucesso!')
      navigate(-1)
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao salvar. Tente novamente.')
    },
  })

  // Validacao
  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof NomeFormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Nome e obrigatorio'
    }
    if (formData.name.length < 2) {
      newErrors.name = 'Nome deve ter pelo menos 2 caracteres'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validate()) {
      mutation.mutate(formData)
    }
  }

  const handleChange = (field: keyof NomeFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Limpar erro do campo ao digitar
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  if (isEditing && isLoadingData) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Carregando...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {isEditing ? 'Editar Item' : 'Novo Item'}
        </h1>
      </div>

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
        {/* Campo Nome */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Nome *
          </label>
          <input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.name
                ? 'border-red-500 dark:border-red-400'
                : 'border-gray-300 dark:border-gray-600'
            }`}
            placeholder="Digite o nome"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {errors.name}
            </p>
          )}
        </div>

        {/* Campo Descricao */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Descricao
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Digite a descricao"
          />
        </div>

        {/* Campo Status */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Status
          </label>
          <select
            id="status"
            value={formData.status}
            onChange={(e) => handleChange('status', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="active">Ativo</option>
            <option value="inactive">Inativo</option>
          </select>
        </div>

        {/* Botoes */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {mutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {isEditing ? 'Salvar Alteracoes' : 'Criar'}
          </button>
        </div>
      </form>
    </div>
  )
}
```

## Passos Apos Criar a Pagina

### 1. Registrar Rota no App.tsx

Abrir `frontend/src/App.tsx` e adicionar a rota:

```tsx
// No topo - import
import NomePagina from './pages/NomePagina'

// Dentro de <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
<Route
  path="nome-rota"
  element={
    <ProtectedRoute requiredPermission="modulo:view">
      <NomePagina />
    </ProtectedRoute>
  }
/>
```

### 2. Adicionar ao Sidebar (se necessario)

Editar `frontend/src/components/Layout.tsx` para adicionar o item de menu no sidebar.

### 3. Criar Hook Customizado (se necessario)

Para logica complexa, extrair para um hook em `frontend/src/hooks/`:

```tsx
// frontend/src/hooks/useNomeModulo.ts
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
// import { nomeApi } from '../services/api'

export function useNomeModulo() {
  const queryClient = useQueryClient()

  const listQuery = useQuery({
    queryKey: ['nome-lista'],
    queryFn: () => Promise.resolve([]), // TODO: API real
  })

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      // TODO: API real
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nome-lista'] })
      toast.success('Criado com sucesso!')
    },
    onError: () => {
      toast.error('Erro ao criar. Tente novamente.')
    },
  })

  return {
    items: listQuery.data || [],
    isLoading: listQuery.isLoading,
    error: listQuery.error,
    refetch: listQuery.refetch,
    create: createMutation.mutate,
    isCreating: createMutation.isPending,
  }
}
```

### 4. Adicionar API Client (se necessario)

Adicionar ao `frontend/src/services/api.ts`:

```tsx
// API client do modulo
export const nomeApi = {
  list: (params?: any) => api.get('/modulo', { params }),
  getById: (id: number) => api.get(`/modulo/${id}`),
  create: (data: any) => api.post('/modulo', data),
  update: (id: number, data: any) => api.put(`/modulo/${id}`, data),
  delete: (id: number) => api.delete(`/modulo/${id}`),
}
```

### 5. Criar Tipos (se necessario)

Adicionar em `frontend/src/types/nomeModulo.ts`:

```tsx
export interface NomeItem {
  id: number
  name: string
  status: string
  created_at: string
}

export interface NomeItemCreate {
  name: string
  status?: string
}

export interface NomeItemUpdate {
  name?: string
  status?: string
}
```

## Checklist de Validacao

- [ ] Pagina criada em `frontend/src/pages/`
- [ ] Rota registrada em `App.tsx`
- [ ] Permissao verificada via `<ProtectedRoute requiredPermission="...">`
- [ ] Textos em portugues (sem i18n)
- [ ] Dark mode suportado (classes `dark:`)
- [ ] Estados de loading, erro e vazio implementados
- [ ] Responsivo com classes Tailwind
- [ ] Icones do Lucide React
- [ ] TypeScript com tipos definidos
- [ ] API client adicionado em `services/api.ts`
- [ ] Documentacao de interface consultada (`docs/modules/{modulo}/interfaces/`)
- [ ] Typecheck passa: `cd web && npm run typecheck`
