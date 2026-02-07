# Design System Tennis Tracking

Guia de padroes visuais e componentes para manter consistencia no frontend React.

## Cores e Dark Mode

### Regras Fundamentais

1. **SEMPRE** incluir variantes `dark:` em todos os elementos visuais
2. Usar classes Tailwind padronizadas, nao cores hardcoded
3. Seguir a paleta definida

### Paleta de Cores

| Elemento | Light Mode | Dark Mode |
|----------|-----------|-----------|
| Background pagina | `bg-white` | `dark:bg-gray-900` |
| Background card | `bg-white` | `dark:bg-gray-800` |
| Background hover | `hover:bg-gray-50` | `dark:hover:bg-gray-800/50` |
| Background header tabela | `bg-gray-50` | `dark:bg-gray-800` |
| Texto principal | `text-gray-900` | `dark:text-gray-100` |
| Texto secundario | `text-gray-500` | `dark:text-gray-400` |
| Bordas | `border-gray-200` | `dark:border-gray-700` |
| Divisores | `divide-gray-100` | `dark:divide-gray-700/50` |

### Exemplo Correto

```tsx
// CORRETO - Com dark mode
<div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
  <h1 className="text-gray-900 dark:text-gray-100">Titulo</h1>
  <p className="text-gray-500 dark:text-gray-400">Descricao</p>
</div>

// INCORRETO - Sem dark mode
<div className="bg-white border border-gray-200">
  <h1 className="text-gray-900">Titulo</h1>
</div>
```

## Espacamentos

### Padding Padrao

| Elemento | Classes |
|----------|---------|
| Pagina | `p-4` ou `px-4 py-4` |
| Card body | `p-4` ou `p-6` |
| Celulas tabela | `px-4 py-3` |
| Botoes | `px-4 py-2` (md), `px-3 py-1.5` (sm) |
| Inputs | `px-3 py-2` |

### Spacing entre elementos

| Contexto | Classe |
|----------|--------|
| Secoes da pagina | `space-y-4` |
| Itens de formulario | `space-y-4` |
| Botoes em grupo | `gap-2` ou `gap-3` |

## Border Radius

**Padrao unico**: Use `rounded-lg` para todos os elementos

```tsx
// CORRETO
<input className="rounded-lg border ..." />
<button className="rounded-lg ..." />
<div className="rounded-lg bg-white ..." />

// INCORRETO - Mistura de valores
<input className="rounded-md border ..." />
<button className="rounded ..." />
```

**Excecoes**:
- `rounded-full` - Avatares, badges pill, botoes circulares
- `rounded` - Checkboxes

## Componentes Padronizados

### 1. Paginas de Listagem

Use `ListPageLayout` para todas as paginas de listagem:

```tsx
import { ListPageLayout, ListTable, Badge, Button } from '@/components/ui';

function ClientList() {
  return (
    <ListPageLayout
      title="Clientes"
      subtitle={`${total} clientes encontrados`}
      icon={<i className="bi bi-building" />}
      breadcrumbs={[
        { label: 'Home', href: '/' },
        { label: 'Clientes' },
      ]}
      actions={
        <Button variant="primary" onClick={handleCreate}>
          <i className="bi bi-plus mr-2" />
          Novo Cliente
        </Button>
      }
      filters={<ClientFilters />}
      viewMode={viewMode}
      viewModes={['table', 'grid']}
      onViewModeChange={setViewMode}
      loading={loading}
      error={error}
      isEmpty={clients.length === 0}
      pagination={{
        page,
        pageSize: 20,
        total,
        onPageChange: setPage,
      }}
    >
      <ListTable
        data={clients}
        columns={columns}
        onRowClick={handleRowClick}
      />
    </ListPageLayout>
  );
}
```

### 2. Tabelas

Use o componente `ListTable` ou os componentes `Table*`:

```tsx
// Opcao 1: ListTable (recomendado para listas simples)
<ListTable
  data={items}
  columns={[
    { key: 'name', header: 'Nome' },
    { key: 'status', header: 'Status', render: (item) => <Badge>{item.status}</Badge> },
    { key: 'actions', header: 'Acoes', align: 'right', render: (item) => <Actions item={item} /> },
  ]}
  onRowClick={handleClick}
/>

// Opcao 2: Componentes Table (para casos customizados)
import { Table, TableHead, TableBody, TableRow, TableHeaderCell, TableCell } from '@/components/ui';

<Table>
  <TableHead>
    <TableRow>
      <TableHeaderCell>Nome</TableHeaderCell>
      <TableHeaderCell>Status</TableHeaderCell>
    </TableRow>
  </TableHead>
  <TableBody>
    {items.map(item => (
      <TableRow key={item.id} hoverable>
        <TableCell>{item.name}</TableCell>
        <TableCell><Badge>{item.status}</Badge></TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### 3. Headers de Pagina

Use `PageHeader` para titulos de pagina:

```tsx
import { PageHeader } from '@/components/ui';

<PageHeader
  title="Clientes"
  subtitle="Gerencie seus clientes"
  icon={<i className="bi bi-building" />}
  breadcrumbs={[{ label: 'Home', href: '/' }, { label: 'Clientes' }]}
  actions={<Button>Novo</Button>}
/>
```

### 4. Badges de Status

Use `Badge` ou `StatusBadge`:

```tsx
import { Badge, StatusBadge } from '@/components/ui';

// Badge generico
<Badge variant="success">Ativo</Badge>
<Badge variant="danger">Inativo</Badge>
<Badge variant="warning">Pendente</Badge>
<Badge variant="info">Info</Badge>

// StatusBadge pre-definido
<StatusBadge status="active" />
<StatusBadge status="inactive" />
<StatusBadge status="pending" />
```

### 5. Botoes

Use o componente `Button`:

```tsx
import { Button } from '@/components/ui';

<Button variant="primary">Salvar</Button>
<Button variant="secondary">Cancelar</Button>
<Button variant="danger">Excluir</Button>
<Button variant="outline">Outline</Button>
<Button size="sm">Pequeno</Button>
<Button size="lg">Grande</Button>
<Button loading>Carregando...</Button>
```

### 6. Inputs de Busca

Use `SearchInput`:

```tsx
import { SearchInput } from '@/components/ui';

<SearchInput
  value={search}
  onChange={setSearch}
  onSearch={handleSearch}
  placeholder="Buscar clientes..."
  variant="light"
  debounce={300}
/>
```

### 7. Loading States

Use `Spinner`:

```tsx
import { Spinner } from '@/components/ui';

// Centralizado
<div className="flex items-center justify-center py-12">
  <Spinner size="lg" />
</div>

// Inline
<Button loading><Spinner size="sm" /> Salvando...</Button>
```

## Contraste de Cores (Acessibilidade)

### Regras de Contraste Minimo

| Elemento | Ratio Minimo | Exemplo Correto |
|----------|--------------|-----------------|
| Texto normal | 4.5:1 | `text-gray-700` em `bg-white` |
| Texto grande (18px+) | 3:1 | `text-gray-600` em `bg-white` |
| UI components | 3:1 | Bordas, icones, placeholders |

### Combinacoes Proibidas (baixo contraste)

```tsx
// PROIBIDO - Texto invisivel
<div className="bg-white text-white">  // Branco no branco
<div className="bg-gray-50 text-gray-100">  // Muito claro
<div className="bg-gray-100 text-gray-200">  // Sem contraste
<button className="bg-white border-white">  // Borda invisivel

// PROIBIDO - Texto muito claro para conteudo
<p className="text-gray-300">Texto principal</p>  // Ilegivel
<span className="text-gray-400">Informacao importante</span>  // Dificil ler
```

### Combinacoes Permitidas

```tsx
// CORRETO - Alto contraste
<div className="bg-white text-gray-900">  // Maximo contraste
<div className="bg-gray-50 text-gray-700">  // Bom contraste
<div className="bg-gray-100 text-gray-600">  // Aceitavel

// CORRETO - Texto branco em fundo escuro
<button className="bg-blue-600 text-white">  // OK
<div className="bg-gray-800 text-white">  // OK
<span className="bg-red-500 text-white">  // OK

// CORRETO - Textos secundarios
<p className="text-gray-500">Texto secundario</p>  // Minimo aceitavel
<span className="text-gray-600">Legenda</span>  // Bom
```

### Cores Minimas por Contexto

| Contexto | Cor Minima | Exemplo |
|----------|-----------|---------|
| Texto principal | `text-gray-700` | Paragrafos, labels |
| Texto secundario | `text-gray-500` | Descricoes, hints |
| Placeholders | `placeholder-gray-400` | Inputs |
| Icones | `text-gray-400` | Icones informativos |
| Bordas | `border-gray-200` | Divisores, cards |
| Disabled | `text-gray-400` | Estados desabilitados |

### Verificacao de Contraste

Antes de usar uma combinacao de cores, verifique:

1. **Texto branco (`text-white`)** so deve ser usado em:
   - Fundos coloridos escuros (`bg-blue-600`, `bg-red-500`, etc.)
   - Fundos cinza escuros (`bg-gray-600` ou mais escuro)
   - Nunca em `bg-white`, `bg-gray-50`, `bg-gray-100`

2. **Texto cinza claro (`text-gray-300`, `text-gray-400`)** so para:
   - Placeholders
   - Icones decorativos
   - Texto em dark mode sobre fundo escuro
   - Nunca para conteudo principal legivel

3. **Bordas e divisores**:
   - Minimo `border-gray-200` em fundos claros
   - `border-gray-700` em dark mode

## Checklist de Consistencia

Antes de finalizar uma pagina, verifique:

- [ ] Todas as cores tem variante `dark:`?
- [ ] Esta usando `rounded-lg` nos elementos?
- [ ] Headers usam `PageHeader`?
- [ ] Tabelas usam `ListTable` ou componentes `Table*`?
- [ ] Badges usam o componente `Badge`?
- [ ] Botoes usam o componente `Button`?
- [ ] Loading usa `Spinner`?
- [ ] Espacamento segue o padrao (`space-y-4`, `px-4 py-3`)?

## Anti-Patterns

### Evitar

```tsx
// Cores hardcoded
<div style={{ backgroundColor: '#f5f5f5' }}>

// Texto sem dark mode
<h1 className="text-gray-900">

// Tabela inline sem componentes
<table className="w-full">
  <thead className="bg-gray-50">

// Spinner inline
<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />

// Toggle view mode customizado
<button className={viewMode === 'table' ? 'bg-blue-50' : 'bg-white'}>
```

### Preferir

```tsx
// Usar componentes padronizados
<ListPageLayout title="..." loading={loading}>
  <ListTable data={data} columns={columns} />
</ListPageLayout>

// Usar Spinner
<Spinner size="lg" />

// Usar ViewToggle
<ViewToggle value={viewMode} options={['table', 'grid']} onChange={setViewMode} />
```

## Referencias

- Componentes: `frontend/src/components/`
- Paginas: `frontend/src/pages/`
- Contextos: `frontend/src/contexts/`
- Servicos API: `frontend/src/services/api.ts`
