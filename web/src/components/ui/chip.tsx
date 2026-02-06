import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils/cn"
import { X } from "lucide-react"

const chipVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition-all duration-300",
  {
    variants: {
      variant: {
        default: "bg-slate-800 text-slate-300 border border-slate-700 hover:border-court-accent hover:text-court-accent",
        active: "bg-court-accent-bg border border-court-accent text-court-accent",
        filled: "bg-court-accent text-white hover:bg-court-accent-hover",
        outline: "border-2 border-court-accent text-court-accent bg-transparent hover:bg-court-accent-bg",
      },
      clickable: {
        true: "cursor-pointer hover:shadow-lg hover:shadow-court-accent/20",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      clickable: false,
    },
  }
)

export interface ChipProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof chipVariants> {
  onRemove?: () => void
}

function Chip({
  className,
  variant,
  clickable,
  onRemove,
  children,
  ...props
}: ChipProps) {
  return (
    <div
      className={cn(chipVariants({ variant, clickable }), className)}
      {...props}
    >
      {children}
      {onRemove && (
        <button
          onClick={onRemove}
          className="ml-1 rounded-full hover:bg-white/20 p-0.5 transition-colors"
          aria-label="Remove"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </div>
  )
}

export { Chip, chipVariants }
