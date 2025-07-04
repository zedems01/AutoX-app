import { Zap } from "lucide-react"

export function PageHeader({ children }: { children: React.ReactNode }) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/10 backdrop-blur-sm">
      <div className="container mx-auto flex h-20 items-center justify-between px-0 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-heading text-lg font-semibold">
              AutoX Content Creator
            </h1>
            <p className="text-sm text-muted-foreground">
              Automated content creation with real-time trends and news.
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-4">{children}</div>
      </div>
    </header>
  )
}