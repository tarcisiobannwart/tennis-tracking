import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { adminService } from '@/services/adminService'

const AdminLogs = () => {
  const { t } = useTranslation()
  const [logs, setLogs] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [actionFilter, setActionFilter] = useState('')
  const limit = 50

  useEffect(() => {
    adminService.getLogs({
      skip: page * limit,
      limit,
      action: actionFilter || undefined,
    }).then(data => {
      setLogs(data.logs)
      setTotal(data.total)
    })
  }, [page, actionFilter])

  const totalPages = Math.ceil(total / limit)

  const actionColors: Record<string, string> = {
    login: 'bg-blue-500/10 text-blue-400',
    register: 'bg-green-500/10 text-green-400',
    logout: 'bg-slate-500/10 text-slate-400',
    upload: 'bg-purple-500/10 text-purple-400',
    subscribe: 'bg-amber-500/10 text-amber-400',
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100">{t('admin.logs')}</h1>
        <select
          value={actionFilter}
          onChange={(e) => { setActionFilter(e.target.value); setPage(0) }}
          className="bg-slate-800 border border-slate-700 text-slate-100 rounded-md px-3 py-2 text-sm"
        >
          <option value="">Todas as acoes</option>
          <option value="login">Login</option>
          <option value="register">Registro</option>
          <option value="logout">Logout</option>
          <option value="upload">Upload</option>
          <option value="subscribe">Assinatura</option>
        </select>
      </div>

      <Card className="bg-slate-800 border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-900">
              <tr>
                <th className="text-left p-3 text-slate-400 font-medium">Data</th>
                <th className="text-left p-3 text-slate-400 font-medium">Usuario</th>
                <th className="text-left p-3 text-slate-400 font-medium">Acao</th>
                <th className="text-left p-3 text-slate-400 font-medium">Recurso</th>
                <th className="text-left p-3 text-slate-400 font-medium">IP</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr key={log._id || i} className="border-t border-slate-700 hover:bg-slate-700/50">
                  <td className="p-3 text-slate-300 text-xs whitespace-nowrap">
                    {new Date(log.createdAt).toLocaleString('pt-BR')}
                  </td>
                  <td className="p-3 text-slate-300">{log.userId}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      actionColors[log.action] || 'bg-slate-500/10 text-slate-400'
                    }`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="p-3 text-slate-400">{log.resource}</td>
                  <td className="p-3 text-slate-500 text-xs">{log.ipAddress || '-'}</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-400">
                    Nenhum log encontrado
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between p-3 border-t border-slate-700">
          <p className="text-sm text-slate-400">{total} registros</p>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="ghost" disabled={page === 0} onClick={() => setPage(p => p - 1)}>
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-sm text-slate-300">{page + 1} / {Math.max(totalPages, 1)}</span>
            <Button size="sm" variant="ghost" disabled={page + 1 >= totalPages} onClick={() => setPage(p => p + 1)}>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AdminLogs
