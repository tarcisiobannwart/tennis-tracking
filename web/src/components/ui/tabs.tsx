import * as React from 'react'

interface TabsContextValue {
  value: string
  onValueChange: (value: string) => void
}

const TabsContext = React.createContext<TabsContextValue | undefined>(undefined)

export const Tabs = ({
  value,
  onValueChange,
  children,
  className
}: {
  value: string
  onValueChange: (value: string) => void
  children: React.ReactNode
  className?: string
}) => {
  return (
    <TabsContext.Provider value={{ value, onValueChange }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  )
}

export const TabsList = ({
  children,
  className
}: {
  children: React.ReactNode
  className?: string
}) => {
  return (
    <div className={`inline-flex items-center justify-center rounded-lg bg-muted p-1 ${className || ''}`}>
      {children}
    </div>
  )
}

export const TabsTrigger = ({
  value,
  children,
  className
}: {
  value: string
  children: React.ReactNode
  className?: string
}) => {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error('TabsTrigger must be used within Tabs')

  const isActive = context.value === value

  return (
    <button
      onClick={() => context.onValueChange(value)}
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
        isActive
          ? 'bg-background text-foreground shadow-sm'
          : 'text-muted-foreground hover:bg-background/50'
      } ${className || ''}`}
    >
      {children}
    </button>
  )
}

export const TabsContent = ({
  value,
  children,
  className
}: {
  value: string
  children: React.ReactNode
  className?: string
}) => {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error('TabsContent must be used within Tabs')

  if (context.value !== value) return null

  return <div className={className}>{children}</div>
}
