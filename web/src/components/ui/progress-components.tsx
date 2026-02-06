import { cn } from '@/utils/cn'
import { Trophy, Flame, Target, Award } from 'lucide-react'

// Circular Progress Component
interface CircularProgressProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  label?: string
  showValue?: boolean
  className?: string
}

export const CircularProgress = ({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  label,
  showValue = true,
  className
}: CircularProgressProps) => {
  const percentage = Math.min((value / max) * 100, 100)
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (percentage / 100) * circumference

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          className="transform -rotate-90"
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            className="text-muted/20"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgb(var(--court-accent))"
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
          />
        </svg>
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-2xl font-bold">{Math.round(percentage)}%</div>
              {label && <div className="text-xs text-muted-foreground">{label}</div>}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Linear Progress Bar with Label
interface LinearProgressProps {
  value: number
  max?: number
  label?: string
  showPercentage?: boolean
  className?: string
  barClassName?: string
}

export const LinearProgress = ({
  value,
  max = 100,
  label,
  showPercentage = true,
  className,
  barClassName
}: LinearProgressProps) => {
  const percentage = Math.min((value / max) * 100, 100)

  return (
    <div className={cn('space-y-2', className)}>
      {(label || showPercentage) && (
        <div className="flex items-center justify-between text-sm">
          {label && <span className="font-medium">{label}</span>}
          {showPercentage && (
            <span className="text-muted-foreground">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={cn('h-full bg-court-accent transition-all duration-500 ease-out', barClassName)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

// Level Badge Component
interface LevelBadgeProps {
  level: 'beginner' | 'intermediate' | 'advanced' | 'pro'
  className?: string
}

export const LevelBadge = ({ level, className }: LevelBadgeProps) => {
  const config = {
    beginner: {
      label: 'Beginner',
      color: 'bg-green-500/10 text-green-500 border-green-500/30',
      icon: Target
    },
    intermediate: {
      label: 'Intermediate',
      color: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30',
      icon: Trophy
    },
    advanced: {
      label: 'Advanced',
      color: 'bg-orange-500/10 text-orange-500 border-orange-500/30',
      icon: Award
    },
    pro: {
      label: 'Pro',
      color: 'bg-red-500/10 text-red-500 border-red-500/30',
      icon: Flame
    }
  }

  const { label, color, icon: Icon } = config[level]

  return (
    <div
      className={cn(
        'inline-flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium border',
        color,
        className
      )}
    >
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </div>
  )
}

// Difficulty Tag Component
interface DifficultyTagProps {
  difficulty: 'easy' | 'medium' | 'hard' | 'aaa'
  className?: string
}

export const DifficultyTag = ({ difficulty, className }: DifficultyTagProps) => {
  const config = {
    easy: {
      label: 'Easy',
      color: 'bg-green-500/10 text-green-500'
    },
    medium: {
      label: 'Medium',
      color: 'bg-yellow-500/10 text-yellow-500'
    },
    hard: {
      label: 'Hard',
      color: 'bg-orange-500/10 text-orange-500'
    },
    aaa: {
      label: 'AAA',
      color: 'bg-red-500/10 text-red-500'
    }
  }

  const { label, color } = config[difficulty]

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        color,
        className
      )}
    >
      {label}
    </span>
  )
}

// Streak Counter Component
interface StreakCounterProps {
  days: number
  className?: string
}

export const StreakCounter = ({ days, className }: StreakCounterProps) => {
  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <div className="p-2 rounded-lg bg-orange-500/10">
        <Flame className="w-5 h-5 text-orange-500" />
      </div>
      <div>
        <div className="text-2xl font-bold">{days}</div>
        <div className="text-xs text-muted-foreground">Day Streak</div>
      </div>
    </div>
  )
}

// Animated Counter Component
interface AnimatedStatCounterProps {
  value: number
  label: string
  icon?: React.ReactNode
  suffix?: string
  className?: string
}

export const AnimatedStatCounter = ({
  value,
  label,
  icon,
  suffix = '',
  className
}: AnimatedStatCounterProps) => {
  return (
    <div className={cn('flex items-center space-x-3', className)}>
      {icon && <div className="p-2 rounded-lg bg-court-accent/10">{icon}</div>}
      <div>
        <div className="text-2xl font-bold">
          {value.toLocaleString()}
          {suffix}
        </div>
        <div className="text-sm text-muted-foreground">{label}</div>
      </div>
    </div>
  )
}

// Radar Chart Component (simple implementation)
interface RadarChartProps {
  data: {
    label: string
    value: number
    max?: number
  }[]
  size?: number
  className?: string
}

export const RadarChart = ({ data, size = 200, className }: RadarChartProps) => {
  const center = size / 2
  const radius = size / 2 - 20
  const angleStep = (2 * Math.PI) / data.length

  // Calculate points for the data polygon
  const dataPoints = data.map((item, index) => {
    const angle = index * angleStep - Math.PI / 2
    const max = item.max || 100
    const normalizedValue = (item.value / max) * radius
    const x = center + normalizedValue * Math.cos(angle)
    const y = center + normalizedValue * Math.sin(angle)
    return { x, y }
  })

  // Calculate points for the outer polygon
  const outerPoints = data.map((_, index) => {
    const angle = index * angleStep - Math.PI / 2
    const x = center + radius * Math.cos(angle)
    const y = center + radius * Math.sin(angle)
    return { x, y }
  })

  // Calculate label positions
  const labelPositions = data.map((item, index) => {
    const angle = index * angleStep - Math.PI / 2
    const labelRadius = radius + 15
    const x = center + labelRadius * Math.cos(angle)
    const y = center + labelRadius * Math.sin(angle)
    return { x, y, label: item.label }
  })

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Grid circles */}
        {[0.25, 0.5, 0.75, 1].map((scale) => (
          <circle
            key={scale}
            cx={center}
            cy={center}
            r={radius * scale}
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            className="text-muted/20"
          />
        ))}

        {/* Grid lines */}
        {outerPoints.map((point, index) => (
          <line
            key={index}
            x1={center}
            y1={center}
            x2={point.x}
            y2={point.y}
            stroke="currentColor"
            strokeWidth="1"
            className="text-muted/20"
          />
        ))}

        {/* Data polygon */}
        <polygon
          points={dataPoints.map((p) => `${p.x},${p.y}`).join(' ')}
          fill="rgb(var(--court-accent))"
          fillOpacity="0.3"
          stroke="rgb(var(--court-accent))"
          strokeWidth="2"
        />

        {/* Data points */}
        {dataPoints.map((point, index) => (
          <circle
            key={index}
            cx={point.x}
            cy={point.y}
            r="4"
            fill="rgb(var(--court-accent))"
          />
        ))}

        {/* Labels */}
        {labelPositions.map((pos, index) => (
          <text
            key={index}
            x={pos.x}
            y={pos.y}
            textAnchor="middle"
            dominantBaseline="middle"
            className="text-xs font-medium fill-current"
          >
            {pos.label}
          </text>
        ))}
      </svg>
    </div>
  )
}

// Stats Card with Progress
interface StatsCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  progress?: number
  progressMax?: number
  trend?: 'up' | 'down' | 'neutral'
  className?: string
}

export const StatsCard = ({
  icon,
  label,
  value,
  progress,
  progressMax = 100,
  trend,
  className
}: StatsCardProps) => {
  return (
    <div className={cn('p-4 rounded-lg border border-border bg-card', className)}>
      <div className="flex items-start justify-between mb-3">
        <div className="p-2 rounded-lg bg-court-accent/10">{icon}</div>
        {trend && (
          <span
            className={cn('text-xs font-medium', {
              'text-green-500': trend === 'up',
              'text-red-500': trend === 'down',
              'text-muted-foreground': trend === 'neutral'
            })}
          >
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
          </span>
        )}
      </div>
      <div className="space-y-2">
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-sm text-muted-foreground">{label}</div>
        {progress !== undefined && (
          <LinearProgress value={progress} max={progressMax} showPercentage={false} />
        )}
      </div>
    </div>
  )
}
