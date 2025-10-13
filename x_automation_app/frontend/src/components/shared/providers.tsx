"use client"

import React from "react"
import { ThemeProvider } from "@/components/shared/theme-provider"
import { QueryProvider } from "@/components/shared/query-provider"
import { AuthProvider } from "@/contexts/AuthContext"
import { WorkflowProvider } from "@/contexts/WorkflowProvider"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <QueryProvider>
        <AuthProvider>
          <WorkflowProvider>{children}</WorkflowProvider>
        </AuthProvider>
      </QueryProvider>
    </ThemeProvider>
  )
} 