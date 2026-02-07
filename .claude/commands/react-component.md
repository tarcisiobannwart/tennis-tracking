# Comando: Criar Componente React

Cria um novo componente React reutilizavel para o Tennis Tracking seguindo os padroes do projeto.

## Argumentos

`$ARGUMENTS` - Nome do componente e pasta destino (ex: `StatusBadge ui`, `ClientCard clients`, `CostChart finance`)

Formato: `<NomeComponente> <pasta>`
- `ui` - Componente generico reutilizavel (Badge, Button, Spinner, Modal, etc.)
- `layout` - Componente de layout (Header, Footer, Sidebar, etc.)
- `clients` - Componente especifico do modulo Clientes
- `finance` - Componente especifico do modulo Financeiro
- `crm` - Componente especifico do modulo CRM
- `hr` - Componente especifico do modulo RH
- `dashboard` - Componente especifico do Dashboard
- `communication` - Componente especifico de Comunicacao
- `expenses` - Componente especifico de Despesas
- `functions` - Componente especifico de FaaS/Functions

Se a pasta nao for informada, assumir `ui`.

## Estrutura de Componentes

```
web/src/components/
├── ExportButtons.tsx         # Botoes de exportacao (PDF/Excel)
├── GrafanaDashboard.tsx      # Embed Grafana
├── IntegrationForm.tsx       # Form de integracoes
├── Layout.tsx                # Layout principal com sidebar
├── MFAVerify.tsx             # Verificacao MFA
├── ProtectedRoute.tsx        # Route guard
├── RichTextEditor.tsx        # Editor rich text
├── ToastProvider.tsx         # Provider de notificacoes
├── clients/                  # Componentes de Clientes
│   ├── ClientDetailPanel.tsx
│   ├── ClientDatabaseTab.tsx
│   ├── ClientFunctionsTab.tsx
│   ├── ClientInfrastructureTab.tsx
│   ├── ClientJiraTab.tsx
│   ├── ClientK8sTab.tsx
│   ├── ClientVersionsTab.tsx
│   ├── ClientsYearlyChart.tsx
│   └── CreateTagModal.tsx
├── finance/                  # Componentes Financeiros
│   ├── AmountDisplay.tsx
│   ├── Badge.tsx
│   ├── CompanyHourlyRateCard.tsx
│   ├── ExpenseForm.tsx
│   ├── ExpensesByClientChart.tsx
│   ├── FileUploader.tsx
│   ├── LaborCostCard.tsx
│   ├── MonthYearSelector.tsx
│   ├── ProjectHourlyRatesPanel.tsx
│   ├── RevenuesTab.tsx
│   ├── TotalCostCard.tsx
│   └── index.ts
├── crm/                      # Componentes CRM
│   ├── CompanyForm.tsx
│   ├── ContactForm.tsx
│   ├── ContentForm.tsx
│   ├── LostOpportunityForm.tsx
│   ├── OpportunityDetail.tsx
│   ├── OpportunityForm.tsx
│   ├── PerformanceCharts.tsx
│   └── PlanForm.tsx
├── dashboard/                # Componentes Dashboard
│   └── ClientHoursUsagePanel.tsx
├── communication/            # Componentes Comunicacao
├── expenses/                 # Componentes Despesas
└── functions/                # Componentes FaaS
```

## Stack Tecnologico

- **React 18** com functional components e hooks
- **TypeScript** com tipagem estrita
- **TailwindCSS** para estilizacao (utility-first, dark mode com `dark:`)
- **Lucide React** para icones
- **Sem i18n** - Textos diretamente em portugues
- **Sem clsx** - Template literals para classes condicionais

## Regras Obrigatorias

1. **Functional components** com `export default function NomeComponente()`
2. **Props tipadas** via interface TypeScript
3. **className prop** para permitir customizacao externa
4. **Dark mode** suportado com classes `dark:` do Tailwind
5. **Sem i18n/traducoes** - Todo texto em portugues direto
6. **Sem clsx** - Usar template literals para concatenacao de classes
7. **Responsivo** com breakpoints Tailwind (sm:, md:, lg:)
8. **Lucide React** para icones
9. **Acessibilidade** basica (aria-labels, roles, semantica HTML)
10. **Documentacao** de props via comentarios JSDoc

## Template: Componente UI Generico

```tsx
// web/src/components/ui/NomeComponente.tsx

interface NomeComponenteProps {
  /** Texto ou conteudo principal */
  children: React.ReactNode
  /** Variante visual do componente */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  /** Tamanho do componente */
  size?: 'sm' | 'md' | 'lg'
  /** Classes CSS adicionais */
  className?: string
  /** Callback ao clicar */
  onClick?: () => void
  /** Desabilitado */
  disabled?: boolean
}

const variantStyles: Record<string, string> = {
  default: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  primary: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  danger: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
}

const sizeStyles: Record<string, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
  lg: 'px-4 py-1.5 text-base',
}

export default function NomeComponente({
  children,
  variant = 'default',
  size = 'md',
  className = '',
  onClick,
  disabled = false,
}: NomeComponenteProps) {
  return (
    <span
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={!disabled ? onClick : undefined}
      className={`inline-flex items-center font-medium rounded-full ${variantStyles[variant]} ${sizeStyles[size]} ${
        onClick && !disabled ? 'cursor-pointer hover:opacity-80' : ''
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </span>
  )
}
```

## Template: Componente de Card

```tsx
// web/src/components/ui/Card.tsx

interface CardProps {
  /** Titulo do card */
  title?: string
  /** Subtitulo ou descricao */
  subtitle?: string
  /** Conteudo do card */
  children: React.ReactNode
  /** Icone no header (componente Lucide) */
  icon?: React.ReactNode
  /** Acoes no canto superior direito */
  actions?: React.ReactNode
  /** Classes CSS adicionais */
  className?: string
  /** Padding interno */
  noPadding?: boolean
}

export default function Card({
  title,
  subtitle,
  children,
  icon,
  actions,
  className = '',
  noPadding = false,
}: CardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      {(title || actions) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="text-gray-400 dark:text-gray-500">
                {icon}
              </div>
            )}
            <div>
              {title && (
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {actions && (
            <div className="flex items-center gap-2">
              {actions}
            </div>
          )}
        </div>
      )}
      <div className={noPadding ? '' : 'p-6'}>
        {children}
      </div>
    </div>
  )
}
```

## Template: Componente Modal

```tsx
// web/src/components/ui/Modal.tsx

import { useEffect, useRef } from 'react'
import { X } from 'lucide-react'

interface ModalProps {
  /** Se o modal esta aberto */
  isOpen: boolean
  /** Callback ao fechar */
  onClose: () => void
  /** Titulo do modal */
  title: string
  /** Conteudo do modal */
  children: React.ReactNode
  /** Tamanho do modal */
  size?: 'sm' | 'md' | 'lg' | 'xl'
  /** Botoes do footer */
  footer?: React.ReactNode
}

const sizeStyles: Record<string, string> = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  footer,
}: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null)

  // Fechar com ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      document.addEventListener('keydown', handleEsc)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = ''
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose()
      }}
    >
      <div className={`w-full ${sizeStyles[size]} bg-white dark:bg-gray-800 rounded-lg shadow-xl`}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
```

## Template: Componente de Tabela

```tsx
// web/src/components/ui/DataTable.tsx

import { ChevronUp, ChevronDown } from 'lucide-react'

interface Column<T> {
  /** Chave do campo no objeto */
  key: string
  /** Titulo da coluna */
  label: string
  /** Renderizador customizado */
  render?: (item: T) => React.ReactNode
  /** Se a coluna e ordenavel */
  sortable?: boolean
  /** Alinhamento */
  align?: 'left' | 'center' | 'right'
  /** Largura fixa */
  width?: string
}

interface DataTableProps<T> {
  /** Colunas da tabela */
  columns: Column<T>[]
  /** Dados */
  data: T[]
  /** Chave unica de cada item */
  keyExtractor: (item: T) => string | number
  /** Callback ao clicar numa linha */
  onRowClick?: (item: T) => void
  /** Campo de ordenacao atual */
  sortBy?: string
  /** Direcao da ordenacao */
  sortOrder?: 'asc' | 'desc'
  /** Callback ao ordenar */
  onSort?: (field: string) => void
  /** Mensagem quando vazio */
  emptyMessage?: string
  /** Classes CSS adicionais */
  className?: string
}

export default function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  sortBy,
  sortOrder,
  onSort,
  emptyMessage = 'Nenhum item encontrado',
  className = '',
}: DataTableProps<T>) {
  const alignStyles = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden ${className}`}>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider ${
                    alignStyles[col.align || 'left']
                  } ${col.sortable ? 'cursor-pointer hover:text-gray-700 dark:hover:text-gray-100' : ''}`}
                  style={col.width ? { width: col.width } : undefined}
                  onClick={() => col.sortable && onSort?.(col.key)}
                >
                  <div className={`flex items-center gap-1 ${
                    col.align === 'right' ? 'justify-end' : col.align === 'center' ? 'justify-center' : ''
                  }`}>
                    {col.label}
                    {col.sortable && sortBy === col.key && (
                      sortOrder === 'asc'
                        ? <ChevronUp className="w-3 h-3" />
                        : <ChevronDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-6 py-12 text-center text-gray-500 dark:text-gray-400"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((item) => (
                <tr
                  key={keyExtractor(item)}
                  className={`${
                    onRowClick
                      ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700'
                      : ''
                  }`}
                  onClick={() => onRowClick?.(item)}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white ${
                        alignStyles[col.align || 'left']
                      }`}
                    >
                      {col.render
                        ? col.render(item)
                        : (item as any)[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

## Template: Componente Especifico de Modulo

```tsx
// web/src/components/clients/ClientStatusCard.tsx

import { Building2 } from 'lucide-react'

interface ClientStatusCardProps {
  /** Nome do cliente */
  clientName: string
  /** Status atual */
  status: 'active' | 'inactive' | 'suspended'
  /** Horas contratadas */
  contractedHours: number
  /** Horas consumidas */
  consumedHours: number
  /** Callback ao clicar */
  onClick?: () => void
  /** Classes CSS adicionais */
  className?: string
}

const statusConfig: Record<string, { label: string; color: string }> = {
  active: {
    label: 'Ativo',
    color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  },
  inactive: {
    label: 'Inativo',
    color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  },
  suspended: {
    label: 'Suspenso',
    color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  },
}

export default function ClientStatusCard({
  clientName,
  status,
  contractedHours,
  consumedHours,
  onClick,
  className = '',
}: ClientStatusCardProps) {
  const usagePercent = contractedHours > 0
    ? Math.round((consumedHours / contractedHours) * 100)
    : 0

  const statusInfo = statusConfig[status] || statusConfig.inactive

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-gray-800 rounded-lg shadow p-4 ${
        onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      } ${className}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Building2 className="w-5 h-5 text-gray-400" />
          <h4 className="font-medium text-gray-900 dark:text-white">
            {clientName}
          </h4>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}>
          {statusInfo.label}
        </span>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Horas utilizadas</span>
          <span className="text-gray-900 dark:text-white">
            {consumedHours}h / {contractedHours}h
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              usagePercent > 100
                ? 'bg-red-500'
                : usagePercent > 80
                  ? 'bg-yellow-500'
                  : 'bg-blue-500'
            }`}
            style={{ width: `${Math.min(usagePercent, 100)}%` }}
          />
        </div>
        <p className="text-xs text-right text-gray-500 dark:text-gray-400">
          {usagePercent}% utilizado
        </p>
      </div>
    </div>
  )
}
```

## Padroes de Classes Condicionais (sem clsx)

```tsx
// Template literals para classes condicionais
className={`base-classes ${condicao ? 'classe-true' : 'classe-false'} ${className}`}

// Multiplas condicoes
className={`
  base-classes
  ${isActive ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'}
  ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'}
  ${size === 'lg' ? 'px-6 py-3 text-lg' : 'px-4 py-2 text-sm'}
  ${className}
`}

// Usando objetos de mapeamento (preferido para muitas variantes)
const styles: Record<string, string> = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
  danger: 'bg-red-600 text-white hover:bg-red-700',
}
className={`${styles[variant]} ${className}`}
```

## Checklist de Validacao

- [ ] Componente criado na pasta correta (`components/{pasta}/`)
- [ ] Props tipadas com interface TypeScript
- [ ] Prop `className` para customizacao externa
- [ ] Dark mode suportado (classes `dark:`)
- [ ] Textos em portugues (sem i18n)
- [ ] Sem clsx (template literals)
- [ ] Icones do Lucide React
- [ ] Responsivo com Tailwind
- [ ] Acessibilidade basica (aria, roles)
- [ ] Export default function
- [ ] Typecheck passa: `cd web && npm run type-check`
