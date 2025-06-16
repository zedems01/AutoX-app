import { ModeToggle } from "./theme-toggle"

interface PageHeaderProps {
  title: string
  description?: string
  children?: React.ReactNode
}

export function PageHeader({ title, description, children }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-4 shadow-sm">
      <div className="grid gap-1">
        <h1 className="font-heading text-lg font-semibold md:text-2xl">
          {title}
        </h1>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      <div className="flex items-center space-x-4">{children}</div>
    </div>
  )
} 