/**
 * ComparisonTable - TT-134
 * Tabela comparativa de caracteristicas entre dois jogadores
 */

import { Card, CardContent } from '@/components/ui/card'
import { ComparisonItem } from '@/services/h2hService'

interface ComparisonTableProps {
  comparison: ComparisonItem[]
  playerName: string
  opponentName: string
}

const ComparisonTable = ({ comparison, playerName, opponentName }: ComparisonTableProps) => {
  if (comparison.length === 0) {
    return null
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <h3 className="text-base font-semibold text-slate-100 mb-4">Comparativo</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-2 px-3 text-xs font-medium text-green-400 w-1/3">
                  {playerName}
                </th>
                <th className="text-center py-2 px-3 text-xs font-medium text-slate-400">
                  Atributo
                </th>
                <th className="text-right py-2 px-3 text-xs font-medium text-red-400 w-1/3">
                  {opponentName}
                </th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((item, index) => (
                <tr
                  key={item.attribute}
                  className={`${
                    index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'
                  } border-b border-slate-700/50 last:border-0`}
                >
                  <td className="py-2.5 px-3 text-sm text-slate-200 font-medium">
                    {item.player_value || '-'}
                  </td>
                  <td className="py-2.5 px-3 text-xs text-slate-400 text-center font-medium uppercase tracking-wider">
                    {item.label}
                  </td>
                  <td className="py-2.5 px-3 text-sm text-slate-200 text-right font-medium">
                    {item.opponent_value || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

export default ComparisonTable
