import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, X, AlertCircle, Info, Trophy, Award, Sparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { cn } from '@/utils/cn'
import { Button } from '@/components/ui/button'

// Congratulation Screen Component
interface CongratulationScreenProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  message?: string
  score?: string
  icon?: 'check' | 'trophy' | 'award'
}

export const CongratulationScreen = ({
  isOpen,
  onClose,
  title = 'Congratulations!',
  message = 'You have successfully completed the match',
  score,
  icon = 'check'
}: CongratulationScreenProps) => {
  const iconMap = {
    check: CheckCircle,
    trophy: Trophy,
    award: Award
  }
  const Icon = iconMap[icon]

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-black/90 via-black/80 to-black/90 backdrop-blur-md"
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="text-center max-w-md px-6"
          >
            {/* Animated Icon */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1, rotate: 360 }}
              transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
              className="mb-8 flex justify-center"
            >
              <div className="relative">
                <Icon className="w-24 h-24 text-court-accent" />
                {/* Pulsing ring effect */}
                <motion.div
                  initial={{ scale: 1, opacity: 0.6 }}
                  animate={{ scale: 1.5, opacity: 0 }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="absolute inset-0 rounded-full border-4 border-court-accent"
                />
              </div>
            </motion.div>

            {/* Title */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-4xl font-bold mb-4 text-white"
            >
              {title}
            </motion.h1>

            {/* Score (if provided) */}
            {score && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="text-3xl font-bold text-court-accent mb-4"
              >
                {score}
              </motion.div>
            )}

            {/* Message */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="text-lg text-white/80 mb-8"
            >
              {message}
            </motion.p>

            {/* Close Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <Button
                onClick={onClose}
                className="bg-court-accent hover:bg-court-accent-hover text-white px-8 py-6 text-lg"
              >
                Close
              </Button>
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Countdown Screen Component
interface CountdownScreenProps {
  isVisible: boolean
  onComplete?: () => void
  duration?: number
}

export const CountdownScreen = ({ isVisible, onComplete, duration = 3 }: CountdownScreenProps) => {
  const [count, setCount] = useState(duration)

  useEffect(() => {
    if (!isVisible) {
      setCount(duration)
      return
    }

    if (count === 0) {
      setTimeout(() => onComplete?.(), 500)
      return
    }

    const timer = setTimeout(() => setCount(count - 1), 1000)
    return () => clearTimeout(timer)
  }, [count, isVisible, onComplete, duration])

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-court-accent"
        >
          <motion.div
            key={count}
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 2, opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <h1 className="text-9xl font-bold text-white">
              {count === 0 ? 'GO!' : count}
            </h1>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Toast Notification Component
type ToastType = 'success' | 'error' | 'info' | 'warning'

interface ToastProps {
  type: ToastType
  message: string
  isVisible: boolean
  duration?: number
  onClose?: () => void
}

export const Toast = ({ type, message, isVisible, duration = 3000, onClose }: ToastProps) => {
  useEffect(() => {
    if (isVisible && duration) {
      const timer = setTimeout(() => onClose?.(), duration)
      return () => clearTimeout(timer)
    }
  }, [isVisible, duration, onClose])

  const config = {
    success: {
      icon: CheckCircle,
      className: 'bg-green-500/10 border-green-500/30 text-green-500'
    },
    error: {
      icon: AlertCircle,
      className: 'bg-red-500/10 border-red-500/30 text-red-500'
    },
    info: {
      icon: Info,
      className: 'bg-blue-500/10 border-blue-500/30 text-blue-500'
    },
    warning: {
      icon: AlertCircle,
      className: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500'
    }
  }

  const { icon: Icon, className } = config[type]

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, x: '-50%' }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className="fixed top-4 left-1/2 z-50 min-w-[300px]"
        >
          <div
            className={cn(
              'flex items-center gap-3 p-4 rounded-lg border backdrop-blur-sm',
              className
            )}
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm font-medium flex-1">{message}</p>
            {onClose && (
              <button onClick={onClose} className="flex-shrink-0 hover:opacity-70">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Badge Earned Popup
interface BadgeEarnedProps {
  isOpen: boolean
  onClose: () => void
  badgeTitle: string
  badgeDescription?: string
  badgeIcon?: React.ReactNode
}

export const BadgeEarned = ({
  isOpen,
  onClose,
  badgeTitle,
  badgeDescription,
  badgeIcon
}: BadgeEarnedProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* Badge Popup */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 180 }}
            transition={{ type: 'spring', duration: 0.6 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50"
          >
            <div className="bg-card border border-border rounded-2xl p-8 text-center max-w-sm shadow-2xl">
              {/* Sparkles decoration */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="absolute -top-4 -right-4"
              >
                <Sparkles className="w-8 h-8 text-yellow-500" />
              </motion.div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="absolute -bottom-4 -left-4"
              >
                <Sparkles className="w-6 h-6 text-yellow-500" />
              </motion.div>

              {/* Badge Icon */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring' }}
                className="mb-6 flex justify-center"
              >
                <div className="w-24 h-24 rounded-full bg-court-accent/10 flex items-center justify-center">
                  {badgeIcon || <Trophy className="w-12 h-12 text-court-accent" />}
                </div>
              </motion.div>

              {/* Text */}
              <motion.h3
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-2xl font-bold mb-2"
              >
                Badge Earned!
              </motion.h3>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-lg font-semibold text-court-accent mb-2"
              >
                {badgeTitle}
              </motion.p>
              {badgeDescription && (
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="text-sm text-muted-foreground mb-6"
                >
                  {badgeDescription}
                </motion.p>
              )}

              {/* Button */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Button onClick={onClose} className="w-full">
                  Continue
                </Button>
              </motion.div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Form Success/Error State
interface FormStateProps {
  type: 'success' | 'error'
  message: string
  className?: string
}

export const FormState = ({ type, message, className }: FormStateProps) => {
  const Icon = type === 'success' ? CheckCircle : AlertCircle
  const colorClass = type === 'success' ? 'text-green-500' : 'text-red-500'

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn('flex items-center gap-3 p-4 rounded-lg border', className)}
    >
      <Icon className={cn('w-5 h-5', colorClass)} />
      <p className="text-sm font-medium">{message}</p>
    </motion.div>
  )
}

// Confetti Effect (simple particles)
export const ConfettiEffect = ({ isActive }: { isActive: boolean }) => {
  const [particles, setParticles] = useState<Array<{ id: number; x: number; delay: number }>>([])

  useEffect(() => {
    if (isActive) {
      const newParticles = Array.from({ length: 30 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        delay: Math.random() * 0.5
      }))
      setParticles(newParticles)

      const timer = setTimeout(() => setParticles([]), 3000)
      return () => clearTimeout(timer)
    }
  }, [isActive])

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          initial={{ y: -20, x: `${particle.x}%`, opacity: 1 }}
          animate={{ y: '100vh', opacity: 0 }}
          transition={{ duration: 2, delay: particle.delay }}
          className="absolute w-2 h-2 rounded-full bg-court-accent"
        />
      ))}
    </div>
  )
}
