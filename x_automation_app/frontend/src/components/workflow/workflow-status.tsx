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
    if (workflowState?.next_human_input_step) return "yellow"
    if (workflowState?.current_step === "END") return "green"
    return "default"
  }

  const getStatusText = () => {
    if (error) return `Error: ${error}`
    if (!isConnected) return "Connecting..."
    if (workflowState?.next_human_input_step) return "Action Required"
    if (workflowState?.current_step === "END") return "Completed"
    if (workflowState) return "In Progress..."
    return "Initializing..."
  }

  return (
    <Badge variant={getStatusVariant()} className="text-sm">
      {!isConnected && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {getStatusText()}
    </Badge>
  )
} 