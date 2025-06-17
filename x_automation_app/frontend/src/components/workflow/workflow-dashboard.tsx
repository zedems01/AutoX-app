"use client"

import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { useWorkflow } from "@/hooks/use-workflow"
import { ContentValidation } from "@/components/workflow/content-validation"
import { ImageValidation } from "@/components/workflow/image-validation"
import { TopicSelection } from "@/components/workflow/topic-selection"
import { WorkflowStatus } from "@/components/workflow/workflow-status"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Loader2 } from "lucide-react"

export function WorkflowDashboard() {
  const { threadId, workflowState } = useWorkflowContext()
  const { isConnected, error } = useWorkflow(threadId)

  const renderHumanInTheLoopStep = () => {
    if (!workflowState || !workflowState.next_human_input_step) {
      return null
    }

    switch (workflowState.next_human_input_step) {
      case "await_topic_selection":
        return <TopicSelection />
      case "await_content_validation":
        return <ContentValidation />
      case "await_image_validation":
        return <ImageValidation />
      default:
        return null
    }
  }

  if (!threadId) {
    return (
      <Card className="flex h-full w-full items-center justify-center">
        <CardContent className="text-center">
          <p className="text-muted-foreground">
            Configure and launch a workflow to see its status here.
          </p>
        </CardContent>
      </Card>
    )
  }

  if (!workflowState) {
    return (
      <Card className="flex h-full w-full items-center justify-center">
        <CardContent className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin" />
          <p className="mt-2 text-muted-foreground">
            Waiting for workflow to start...
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Workflow Status</CardTitle>
        <CardDescription>
          Tracking workflow: <code>{threadId}</code>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <WorkflowStatus isConnected={isConnected} error={error} />
        <div className="mt-6">{renderHumanInTheLoopStep()}</div>
      </CardContent>
    </Card>
  )
} 