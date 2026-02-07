# Comando: Refatorar Pagina de Listagem

Refatora uma pagina de listagem existente no Tennis Tracking para seguir os padroes atuais do projeto.

## Argumentos

`$ARGUMENTS` - Nome da pagina a refatorar (ex: `Users`, `HR`, `Clients`)

## Objetivo

Garantir que paginas de listagem sigam os padroes consistentes do TMF:
- React Query para data fetching
- Filtros e busca padronizados
- Tabela com ordenacao
- Estados de loading/erro/vazio
- Dark mode
- Responsividade
- Sem i18n (textos em portugues)
- Sem clsx

## Checklist Completo de Refatoracao

### 1. Imports

- [ ] Usar `useQuery` / `useMutation` do `@tanstack/react-query`
- [ ] Importar icones do `lucide-react`
- [ ] Importar `useAuth` de `../contexts/AuthContext`
- [ ] Importar API client de `../services/api`
- [ ] Remover imports de `useEffect` para data fetching (substituir por useQuery)
- [ ] Remover imports de i18n/traducao (nao usado no TMF)
- [ ] Remover imports de clsx

**Antes:**
```tsx
import { useState, useEffect } from 'react'
import clsx from 'clsx'
import { useTranslation } from 'react-i18next'
```

**Depois:**
```tsx
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Plus, Edit2, Trash2, Loader2, AlertCircle, ChevronUp, ChevronDown, X } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
```

### 2. Data Fetching

- [ ] Substituir `useEffect + fetch` por `useQuery`
- [ ] Definir `queryKey` descritiva
- [ ] Usar `queryFn` com API client
- [ ] Tratar `isLoading`, `error`, `data`

**Antes:**
```tsx
const [data, setData] = useState([])
const [isLoading, setIsLoading] = useState(true)
const [error, setError] = useState('')

useEffect(() => {
  const fetchData = async () => {
    setIsLoading(true)
    try {
      const response = await nomeApi.list()
      setData(response.data)
    } catch (err) {
      setError('Erro ao carregar')
    } finally {
      setIsLoading(false)
    }
  }
  fetchData()
}, [])
```

**Depois:**
```tsx
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['nome-lista'],
  queryFn: () => nomeApi.list().then(r => r.data),
})
```

### 3. Filtragem e Busca

- [ ] Estado `searchTerm` para busca textual
- [ ] Estado `filterStatus` para filtros
- [ ] `useMemo` para filtro local
- [ ] Input de busca com icone Search e botao limpar (X)
- [ ] Select ou botoes para filtros

**Padrao:**
```tsx
const [searchTerm, setSearchTerm] = useState('')
const [filterStatus, setFilterStatus] = useState<string>('all')
const [sortBy, setSortBy] = useState<string>('name')
const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

const filteredItems = useMemo(() => {
  if (!data) return []
  return data
    .filter(item =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.email?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter(item =>
      filterStatus === 'all' ? true : item.status === filterStatus
    )
    .sort((a, b) => {
      const modifier = sortOrder === 'asc' ? 1 : -1
      const aVal = (a as any)[sortBy] || ''
      const bVal = (b as any)[sortBy] || ''
      return String(aVal).localeCompare(String(bVal)) * modifier
    })
}, [data, searchTerm, filterStatus, sortBy, sortOrder])
```

### 4. Ordenacao

- [ ] Headers de tabela clicaveis para ordenacao
- [ ] Icones ChevronUp/ChevronDown no header ativo
- [ ] Alternar asc/desc ao clicar no mesmo campo

**Padrao:**
```tsx
const handleSort = (field: string) => {
  if (sortBy === field) {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
  } else {
    setSortBy(field)
    setSortOrder('asc')
  }
}

// No header da tabela:
<th
  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-gray-100"
  onClick={() => handleSort('name')}
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
```

### 5. Estados Visuais

- [ ] Loading com Spinner centralizado
- [ ] Erro com icone e mensagem
- [ ] Tabela vazia com mensagem
- [ ] Contador de resultados

**Loading:**
```tsx
if (isLoading) {
  return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      <span className="ml-2 text-gray-600 dark:text-gray-400">Carregando...</span>
    </div>
  )
}
```

**Erro:**
```tsx
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
```

**Vazio:**
```tsx
{filteredItems.length === 0 && (
  <tr>
    <td colSpan={columns} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
      Nenhum item encontrado
    </td>
  </tr>
)}
```

### 6. Estilizacao

- [ ] Todas as classes com dark mode (`dark:bg-gray-800`, etc.)
- [ ] Sem clsx - usar template literals
- [ ] Badge de status com cores semanticas
- [ ] Hover na linha da tabela
- [ ] Responsivo (overflow-x-auto na tabela)

**Substituicoes de clsx:**

Antes:
```tsx
className={clsx(
  'px-2 py-1 rounded',
  isActive && 'bg-blue-500 text-white',
  !isActive && 'bg-gray-200 text-gray-700'
)}
```

Depois:
```tsx
className={`px-2 py-1 rounded ${
  isActive
    ? 'bg-blue-500 text-white'
    : 'bg-gray-200 text-gray-700'
}`}
```

### 7. Header da Pagina

- [ ] Titulo h1 com descricao
- [ ] Botao de acao principal (Novo, Criar, etc.) com verificacao de permissao
- [ ] Alinhamento flex between

**Padrao:**
```tsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
      Titulo do Modulo
    </h1>
    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
      Descricao breve
    </p>
  </div>
  {hasPermission('modulo:create') && (
    <button
      onClick={() => setShowCreateModal(true)}
      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
    >
      <Plus className="w-4 h-4" />
      Novo Item
    </button>
  )}
</div>
```

### 8. Barra de Busca e Filtros

**Padrao:**
```tsx
<div className="flex flex-col sm:flex-row gap-4">
  <div className="relative flex-1">
    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
    <input
      type="text"
      placeholder="Buscar..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      className="w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
    <option value="all">Todos</option>
    <option value="active">Ativos</option>
    <option value="inactive">Inativos</option>
  </select>
</div>
```

### 9. Tabela

**Padrao completo:**
```tsx
<div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
  <div className="overflow-x-auto">
    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
      <thead className="bg-gray-50 dark:bg-gray-700">
        <tr>
          {/* Headers com ordenacao */}
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
        {filteredItems.map((item) => (
          <tr
            key={item.id}
            className="hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            {/* Celulas */}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
</div>
```

### 10. Acoes na Tabela

- [ ] Botoes de acao com icones
- [ ] `e.stopPropagation()` quando a linha e clicavel
- [ ] Verificacao de permissao para cada acao

**Padrao:**
```tsx
<td className="px-6 py-4 whitespace-nowrap text-right text-sm">
  <div className="flex items-center justify-end gap-2">
    {hasPermission('modulo:edit') && (
      <button
        onClick={(e) => {
          e.stopPropagation()
          handleEdit(item)
        }}
        className="p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
        title="Editar"
      >
        <Edit2 className="w-4 h-4" />
      </button>
    )}
    {hasPermission('modulo:delete') && (
      <button
        onClick={(e) => {
          e.stopPropagation()
          handleDelete(item)
        }}
        className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
        title="Excluir"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    )}
  </div>
</td>
```

## Mapeamento de Substituicoes

| Antes | Depois |
|-------|--------|
| `clsx(...)` | Template literal `${...}` |
| `useTranslation()` | Texto direto em portugues |
| `t('key')` | `"Texto em portugues"` |
| `useEffect + fetch` | `useQuery({...})` |
| `useState` para dados remotos | `useQuery` retorna `data, isLoading, error` |
| `className="..."` sem dark | Adicionar `dark:` classes |
| Icons SVG inline | `import { Icon } from 'lucide-react'` |
| `<Spinner />` customizado | `<Loader2 className="animate-spin" />` |

## Ordem de Execucao

1. Ler a pagina atual completa
2. Identificar problemas conforme checklist
3. Verificar documentacao de interface em `docs/modules/{modulo}/interfaces/`
4. Refatorar imports
5. Refatorar data fetching (useQuery)
6. Refatorar filtros e busca
7. Refatorar tabela e ordenacao
8. Adicionar dark mode
9. Remover clsx e i18n
10. Validar typecheck: `cd frontend && npm run typecheck`

## Validacao Final

- [ ] `cd frontend && npm run typecheck` passa sem erros
- [ ] Todos os textos em portugues (sem `t('...')`)
- [ ] Sem imports de clsx
- [ ] Sem imports de i18n
- [ ] useQuery para data fetching
- [ ] useMemo para filtragem local
- [ ] Dark mode em todos os elementos
- [ ] Loading/erro/vazio implementados
- [ ] Tabela com ordenacao
- [ ] Busca com icone e botao limpar
- [ ] Permissoes verificadas (hasPermission/hasRoleLevel)
- [ ] Responsivo (overflow-x-auto, flex-col sm:flex-row)
