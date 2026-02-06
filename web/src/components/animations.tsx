import { motion, AnimatePresence, Variants } from 'framer-motion'
import { ReactNode, useEffect, useState } from 'react'
import { cn } from '@/utils/cn'

// Page Transition Wrapper
interface PageTransitionProps {
  children: ReactNode
  className?: string
}

export const PageTransition = ({ children, className }: PageTransitionProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Card with Stagger Animation
interface StaggerContainerProps {
  children: ReactNode
  className?: string
  staggerDelay?: number
}

export const StaggerContainer = ({ children, className, staggerDelay = 0.1 }: StaggerContainerProps) => {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: staggerDelay
      }
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {children}
    </motion.div>
  )
}

export const StaggerItem = ({ children, className }: { children: ReactNode; className?: string }) => {
  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        ease: 'easeOut'
      }
    }
  }

  return (
    <motion.div variants={itemVariants} className={className}>
      {children}
    </motion.div>
  )
}

// Card Hover Animation
interface AnimatedCardProps {
  children: ReactNode
  className?: string
  hoverScale?: number
}

export const AnimatedCard = ({ children, className, hoverScale = 1.02 }: AnimatedCardProps) => {
  return (
    <motion.div
      whileHover={{ scale: hoverScale }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Modal/Sheet Animation
interface AnimatedModalProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
  className?: string
}

export const AnimatedModal = ({ isOpen, onClose, children, className }: AnimatedModalProps) => {
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

          {/* Modal Content */}
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className={cn('fixed inset-x-4 bottom-4 md:inset-auto md:left-1/2 md:top-1/2 md:-translate-x-1/2 md:-translate-y-1/2 z-50', className)}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Bottom Sheet Animation
interface AnimatedSheetProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
  className?: string
}

export const AnimatedSheet = ({ isOpen, onClose, children, className }: AnimatedSheetProps) => {
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

          {/* Sheet Content */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className={cn('fixed inset-x-0 bottom-0 z-50 rounded-t-2xl', className)}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Skeleton Loading Component
interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
}

export const Skeleton = ({ className, variant = 'rectangular' }: SkeletonProps) => {
  const baseClasses = 'bg-muted animate-pulse'
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg'
  }

  return <div className={cn(baseClasses, variantClasses[variant], className)} />
}

// Number Counter Animation
interface CounterProps {
  value: number
  duration?: number
  className?: string
  suffix?: string
  prefix?: string
}

export const AnimatedCounter = ({
  value,
  duration = 2,
  className,
  suffix = '',
  prefix = ''
}: CounterProps) => {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let rafId: number
    let startTime: number | null = null
    const startValue = 0
    const endValue = value

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1)

      // Easing function (easeOutExpo)
      const easedProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)

      const currentCount = Math.floor(startValue + (endValue - startValue) * easedProgress)
      setCount(currentCount)

      if (progress < 1) {
        rafId = requestAnimationFrame(animate)
      }
    }

    rafId = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(rafId)
  }, [value, duration])

  return (
    <span className={className}>
      {prefix}
      {count.toLocaleString()}
      {suffix}
    </span>
  )
}

// Fade In Animation
interface FadeInProps {
  children: ReactNode
  delay?: number
  duration?: number
  className?: string
}

export const FadeIn = ({ children, delay = 0, duration = 0.5, className }: FadeInProps) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration, delay }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Slide In Animation
interface SlideInProps {
  children: ReactNode
  direction?: 'left' | 'right' | 'up' | 'down'
  delay?: number
  duration?: number
  className?: string
}

export const SlideIn = ({
  children,
  direction = 'up',
  delay = 0,
  duration = 0.5,
  className
}: SlideInProps) => {
  const directionOffset = {
    left: { x: -50, y: 0 },
    right: { x: 50, y: 0 },
    up: { x: 0, y: 50 },
    down: { x: 0, y: -50 }
  }

  return (
    <motion.div
      initial={{ opacity: 0, ...directionOffset[direction] }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{ duration, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Get Ready Screen Animation
interface GetReadyScreenProps {
  isVisible: boolean
  text?: string
  onComplete?: () => void
}

export const GetReadyScreen = ({ isVisible, text = 'Get Ready', onComplete }: GetReadyScreenProps) => {
  useEffect(() => {
    if (isVisible && onComplete) {
      const timer = setTimeout(onComplete, 2500)
      return () => clearTimeout(timer)
    }
  }, [isVisible, onComplete])

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-background"
        >
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 1.5, opacity: 0 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="text-center"
          >
            <h1 className="text-6xl md:text-8xl font-bold text-court-accent mb-4">
              {text}
            </h1>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 2, ease: 'easeInOut' }}
              className="h-2 bg-court-accent rounded-full mx-auto max-w-xs"
            />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Animated Button
interface AnimatedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
}

export const AnimatedButton = ({ children, className, ...props }: AnimatedButtonProps) => {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={className}
      {...props}
    >
      {children}
    </motion.button>
  )
}

// Animated Input Wrapper
interface AnimatedInputProps {
  children: ReactNode
  className?: string
}

export const AnimatedInput = ({ children, className }: AnimatedInputProps) => {
  return (
    <motion.div
      whileFocus={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// List Item with Stagger
export const ListStaggerContainer = ({ children, className }: { children: ReactNode; className?: string }) => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: 0.05
          }
        }
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export const ListStaggerItem = ({ children, className }: { children: ReactNode; className?: string }) => {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, x: -20 },
        visible: { opacity: 1, x: 0 }
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}
