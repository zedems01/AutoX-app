"use client"

import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { Badge } from "@/components/ui/badge"
import { Loader2 } from "lucide-react"
import { ActivityTimeline } from "@/components/workflow/ActivityTimeline"

export function WorkflowStatus() {
  const { isConnected, error, workflowState } = useWorkflowContext()

  const getStatusVariant = () => {
    if (error) return "destructive"
    if (!isConnected) return "secondary"
    if (workflowState?.current_step === "END") return "green"
    if (workflowState?.next_human_input_step) return "yellow"
    if (workflowState)
      return "outline"
    return "secondary"
  }

  const getStatusText = () => {
    if (error) return `Error: ${error}`
    if (!isConnected) return "Connecting..."
    if (workflowState?.current_step === "END") return "Completed"
    if (workflowState?.next_human_input_step) return "Action Required"
    if (workflowState) return "In Progress..."
    return "Initializing..."
  }

  const statusVariant = getStatusVariant();

  return (
        <Badge 
          variant={getStatusVariant()} 
          className={
            statusVariant === "outline"
            ? "border-blue-300 bg-blue-50 text-blue-700 dark:border-blue-700 dark:bg-blue-950 dark:text-blue-400"
            : "text-sm"
          }
        >
          {!isConnected && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {getStatusText()}
        </Badge>
  )
} 