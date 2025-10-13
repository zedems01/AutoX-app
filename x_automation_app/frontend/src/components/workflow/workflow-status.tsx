"use client"

import React from "react"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { Badge } from "@/components/ui/badge"
import { Loader2 } from "lucide-react"
// import { ActivityTimeline } from "@/components/workflow/ActivityTimeline"

export function WorkflowStatus() {
  const { isConnected, error, workflowState, events } = useWorkflowContext()

  const isPublicatorCompleted = events.some(
    (event) => event.name === "publicator" && event.event !== "on_chain_start"
  )

  const getStatusVariant = () => {
    if (error) return "destructive"
    if (!isConnected) return "secondary"
    if (workflowState?.current_step === "END" || isPublicatorCompleted)
      return "green"
    if (workflowState?.next_human_input_step) return "yellow"
    if (workflowState) return "blue"
    return "secondary"
  }

  const getStatusText = () => {
    if (error) return `Error: ${error}`
    if (!isConnected) return "Connecting..."
    if (workflowState?.current_step === "END" || isPublicatorCompleted)
      return "Completed"
    if (workflowState?.next_human_input_step) return "Action Required"
    if (workflowState) return "In Progress..."
    return "Initializing..."
  }

  const statusVariant = getStatusVariant()

  const getStatusClassName = (variant: string) => {
    switch (variant) {
      case "destructive":
        return "border-red-300 bg-red-50 text-red-700 dark:border-red-700 dark:bg-red-950 dark:text-red-400"
      case "green":
        return "border-green-300 bg-green-50 text-green-700 dark:border-green-700 dark:bg-green-950 dark:text-green-400"
      case "yellow":
        return "border-yellow-300 bg-yellow-50 text-yellow-700 dark:border-yellow-700 dark:bg-yellow-950 dark:text-yellow-400"
      case "blue":
        return "border-blue-300 bg-blue-50 text-blue-700 dark:border-blue-700 dark:bg-blue-950 dark:text-blue-400"
      case "secondary":
      default:
        return "border-gray-300 bg-gray-50 text-gray-700 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-400"
    }
  }

  return (
    <Badge variant="outline" className={getStatusClassName(statusVariant)}>
      {!isConnected && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {getStatusText()}
    </Badge>
  )
} 