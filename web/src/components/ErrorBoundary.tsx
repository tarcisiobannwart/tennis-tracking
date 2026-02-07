import { Component, type ErrorInfo, type ReactNode } from 'react'
import { captureComponentError } from '@/services/errorReporter'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    captureComponentError(error, errorInfo.componentStack ?? undefined)
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null })
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex min-h-[400px] items-center justify-center p-8">
          <div className="w-full max-w-md rounded-lg border border-border bg-card p-6 text-center shadow-sm">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
              <svg
                className="h-6 w-6 text-destructive"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                />
              </svg>
            </div>
            <h2 className="mb-2 text-lg font-semibold text-card-foreground">
              Algo deu errado
            </h2>
            <p className="mb-4 text-sm text-muted-foreground">
              Ocorreu um erro inesperado. A equipe foi notificada automaticamente.
            </p>
            {this.state.error && (
              <p className="mb-4 rounded bg-muted p-2 text-xs text-muted-foreground font-mono">
                {this.state.error.message.substring(0, 150)}
              </p>
            )}
            <button
              onClick={this.handleRetry}
              className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
