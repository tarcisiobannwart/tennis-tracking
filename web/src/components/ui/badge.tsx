import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils/cn"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-all duration-300",
  {
    variants: {
      variant: {
        default: "bg-court-accent text-white",
        success: "bg-green-500/20 text-green-400 border border-green-500/30",
        error: "bg-red-500/20 text-red-400 border border-red-500/30",
        warning: "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30",
        info: "bg-blue-500/20 text-blue-400 border border-blue-500/30",
        neutral: "bg-slate-700 text-slate-300 border border-slate-600",
        outline: "border border-court-accent text-court-accent bg-transparent",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
