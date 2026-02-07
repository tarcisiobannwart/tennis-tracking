/**
 * Error Reporter - Captura automatica de erros e envio para backend.
 *
 * Usa fetch nativo (NAO Axios) para evitar loop infinito no interceptor.
 * Dedup client-side por sessao usando Set de fingerprints.
 */

const REPORT_ENDPOINT = '/api/error-reports'
const MAX_STACK_LENGTH = 5000

/** Fingerprints ja enviados nesta sessao (dedup client-side) */
const reportedFingerprints = new Set<string>()

/** Flag para evitar re-init */
let initialized = false

/**
 * Gera fingerprint simples (hash) para dedup client-side.
 * Nao precisa ser SHA256 - apenas evita envios repetidos na mesma sessao.
 */
function generateFingerprint(errorType: string, message: string): string {
  const normalized = message
    .replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, '<UUID>')
    .replace(/\b[0-9a-f]{8,}\b/gi, '<HEX>')
    .replace(/\b\d{4,}\b/g, '<NUM>')
  const raw = `${errorType}|${normalized}`
  // Simple hash baseado em charCode
  let hash = 0
  for (let i = 0; i < raw.length; i++) {
    const char = raw.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash |= 0
  }
  return hash.toString(36)
}

/**
 * Envia error report para o backend usando fetch nativo.
 * Silencioso - nunca propaga erros.
 */
async function sendReport(payload: {
  source: string
  error_type: string
  message: string
  stack_trace?: string
  context?: Record<string, string>
}): Promise<void> {
  try {
    // Dedup client-side
    const fp = generateFingerprint(payload.error_type, payload.message)
    if (reportedFingerprints.has(fp)) return
    reportedFingerprints.add(fp)

    // Usa fetch nativo para evitar loop no interceptor Axios
    await fetch(REPORT_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch {
    // Silencioso - nunca propaga erros do reporter
  }
}

/**
 * Captura erro de window.onerror.
 */
function handleWindowError(event: ErrorEvent): void {
  sendReport({
    source: 'frontend',
    error_type: event.error?.name || 'Error',
    message: event.message || 'Unknown error',
    stack_trace: event.error?.stack?.substring(0, MAX_STACK_LENGTH),
    context: {
      url: window.location.href,
      filename: event.filename || '',
      line: String(event.lineno || ''),
      col: String(event.colno || ''),
      user_agent: navigator.userAgent,
    },
  })
}

/**
 * Captura unhandled promise rejections.
 */
function handleUnhandledRejection(event: PromiseRejectionEvent): void {
  const error = event.reason
  const isError = error instanceof Error

  sendReport({
    source: 'frontend',
    error_type: isError ? error.name : 'UnhandledRejection',
    message: isError ? error.message : String(error),
    stack_trace: isError ? error.stack?.substring(0, MAX_STACK_LENGTH) : undefined,
    context: {
      url: window.location.href,
      user_agent: navigator.userAgent,
    },
  })
}

/**
 * Captura erros de API (5xx e network errors).
 * Chamado pelo interceptor do Axios.
 */
export function captureApiError(
  status: number | undefined,
  url: string,
  method: string,
  message: string,
): void {
  // Apenas 5xx e network errors
  if (status !== undefined && status < 500) return

  sendReport({
    source: 'frontend',
    error_type: status ? `HTTP_${status}` : 'NetworkError',
    message: message,
    context: {
      url: window.location.href,
      api_url: url,
      api_method: method.toUpperCase(),
      status_code: String(status || 'N/A'),
      user_agent: navigator.userAgent,
    },
  })
}

/**
 * Captura erro de React Error Boundary.
 */
export function captureComponentError(
  error: Error,
  componentStack?: string,
): void {
  sendReport({
    source: 'frontend',
    error_type: error.name || 'ComponentError',
    message: error.message,
    stack_trace: (error.stack || '').substring(0, MAX_STACK_LENGTH),
    context: {
      url: window.location.href,
      component_stack: componentStack?.substring(0, 2000) || '',
      user_agent: navigator.userAgent,
    },
  })
}

/**
 * Inicializa os listeners globais de erro.
 * Deve ser chamado uma vez no main.tsx.
 */
export function init(): void {
  if (initialized) return
  initialized = true

  window.addEventListener('error', handleWindowError)
  window.addEventListener('unhandledrejection', handleUnhandledRejection)
}

export default {
  init,
  captureApiError,
  captureComponentError,
}
