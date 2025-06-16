"use client"

import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2 } from "lucide-react"

interface WorkflowStatusProps {
  isConnected: boolean
  error: string | null
}

export function WorkflowStatus({ isConnected, error }: WorkflowStatusProps) {
  const { workflowState } = useWorkflowContext()

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
    if (workflowState) return `In Progress: ${workflowState.current_step}`
    return "Initializing..."
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Workflow Status</span>
          <Badge variant={getStatusVariant()} className="ml-2 text-sm">
            {!isConnected && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {getStatusText()}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {workflowState ? (
          <pre className="p-4 bg-muted rounded-lg overflow-x-auto text-sm">
            {JSON.stringify(
              {
                current_step: workflowState.current_step,
                next_human_input_step: workflowState.next_human_input_step,
                error: workflowState.error_message,
              },
              null,
              2
            )}
          </pre>
        ) : (
          <p>Waiting for workflow to start and send its first state...</p>
        )}
      </CardContent>
    </Card>
  )
} 