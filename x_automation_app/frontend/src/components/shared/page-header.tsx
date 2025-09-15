import { Zap } from "lucide-react"

export function PageHeader({ children }: { children: React.ReactNode }) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/10 backdrop-blur-sm">
      <div className="container mx-auto flex h-16 md:h-20 items-center justify-between px-4 md:px-6 lg:px-8 py-3 md:py-4">
        <div className="flex items-center gap-2 md:gap-3">
          <div className="flex h-8 w-8 md:h-10 md:w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Zap className="h-4 w-4 md:h-5 md:w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="font-heading text-base md:text-lg font-semibold truncate">
              AutoX Content Creator
            </h1>
            <p className="text-xs md:text-sm text-muted-foreground hidden sm:block">
              Automated content creation with real-time trends and news.
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2 md:space-x-4">{children}</div>
      </div>
    </header>
  )
}