import * as React from "react"
import { Plus, Upload, Video, X } from "lucide-react"
import { cn } from "@/utils/cn"
import { useUIStore } from "@/stores/uiStore"
import { motion, AnimatePresence } from "framer-motion"

interface FabAction {
  icon: React.ElementType
  label: string
  onClick: () => void
}

const Fab = () => {
  const [isOpen, setIsOpen] = React.useState(false)
  const { setModal } = useUIStore()

  const actions: FabAction[] = [
    {
      icon: Upload,
      label: "Upload Video",
      onClick: () => {
        setModal('uploadVideo', true)
        setIsOpen(false)
      }
    },
    {
      icon: Video,
      label: "Nova Partida",
      onClick: () => {
        setModal('newMatch', true)
        setIsOpen(false)
      }
    }
  ]

  return (
    <div className="fixed bottom-20 md:bottom-8 right-4 md:right-8 z-40">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="flex flex-col gap-3 mb-3"
          >
            {actions.map((action, index) => {
              const Icon = action.icon
              return (
                <motion.button
                  key={action.label}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={action.onClick}
                  aria-label={action.label}
                  className="flex items-center gap-3 bg-slate-800 hover:bg-slate-700 text-slate-100 px-4 py-3 rounded-full shadow-lg border border-slate-700 hover:border-court-accent transition-all duration-300 group"
                >
                  <Icon className="w-5 h-5 text-court-accent" />
                  <span className="text-sm font-medium whitespace-nowrap">
                    {action.label}
                  </span>
                </motion.button>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main FAB Button */}
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? "Fechar menu" : "Abrir menu"}
        aria-expanded={isOpen}
        className={cn(
          "w-14 h-14 bg-court-accent hover:bg-court-accent-hover text-white rounded-full shadow-2xl shadow-court-accent/30 flex items-center justify-center transition-all duration-300",
          isOpen && "rotate-45"
        )}
      >
        {isOpen ? (
          <X className="w-6 h-6" />
        ) : (
          <Plus className="w-6 h-6" />
        )}
      </motion.button>
    </div>
  )
}

export { Fab }
