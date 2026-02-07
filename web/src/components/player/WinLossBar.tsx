interface WinLossBarProps {
  wins: number
  losses: number
  label: string
}

export const WinLossBar = ({ wins, losses, label }: WinLossBarProps) => {
  const total = wins + losses
  const winPercentage = total > 0 ? (wins / total) * 100 : 0

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-muted-foreground">
          {wins}V - {losses}D ({total > 0 ? winPercentage.toFixed(0) : 0}%)
        </span>
      </div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className="bg-green-500 transition-all"
          style={{ width: `${winPercentage}%` }}
        />
        <div
          className="bg-red-500 transition-all"
          style={{ width: `${100 - winPercentage}%` }}
        />
      </div>
    </div>
  )
}
