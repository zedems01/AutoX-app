"use client"

import { useState, useEffect } from "react"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { useWorkflow } from "@/hooks/use-workflow"
import { ContentValidation } from "@/components/workflow/content-validation"
import { ImageValidation } from "@/components/workflow/image-validation"
import { TopicSelection } from "@/components/workflow/topic-selection"
import { WorkflowStatus } from "@/components/workflow/workflow-status"
import { FinalOutput } from "@/components/workflow/FinalOutput"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Loader2, RefreshCw } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { ActivityTimeline } from "@/components/workflow/ActivityTimeline"

export function WorkflowDashboard() {
  const { threadId, workflowState, showDetails } = useWorkflowContext()
  const { isConnected, error } = useWorkflow(threadId)
  const [isTopicModalOpen, setTopicModalOpen] = useState(false)
  const [isContentModalOpen, setContentModalOpen] = useState(false)
  const [isImageModalOpen, setImageModalOpen] = useState(false)

  useEffect(() => {
    const nextStep = workflowState?.next_human_input_step
    setTopicModalOpen(nextStep === "await_topic_selection")
    setContentModalOpen(nextStep === "await_content_validation")
    setImageModalOpen(nextStep === "await_image_validation")
  }, [workflowState?.next_human_input_step])

  const renderConnectionStatus = () => {
    if (error) return <Badge variant="destructive">{error}</Badge>
    if (!isConnected) return <Badge variant="secondary">Connecting...</Badge>
    if (workflowState?.next_human_input_step) return <Badge variant="yellow">Action Required</Badge>
    if (workflowState?.current_step === "END") return <Badge variant="green">Completed</Badge>
    if (workflowState) return <Badge variant="default">In Progress...</Badge>
    return <Badge variant="default">Initializing...</Badge>
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
        <CardTitle className="flex items-center justify-between">
          <span>Workflow Progress</span>
          <div className="flex items-center gap-4">
            {renderConnectionStatus()}
            {workflowState?.current_step === "END" && (
              <Button onClick={() => window.location.reload()} size="sm">
                <RefreshCw className="mr-2 h-4 w-4" />
                New Workflow
              </Button>
            )}
          </div>
        </CardTitle>
        <CardDescription>
          Tracking workflow: <code>{threadId}</code>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 pt-4">
        <ActivityTimeline />
        <WorkflowStatus />
        {!showDetails && <FinalOutput />}
      </CardContent>
      {workflowState?.current_step === "END" && (
        <CardFooter className="flex justify-end pt-6">
          <Button onClick={() => window.location.reload()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Start New Workflow
          </Button>
        </CardFooter>
      )}

      <Dialog open={isTopicModalOpen} onOpenChange={setTopicModalOpen}>
        <DialogContent>
          <TopicSelection onSubmitted={() => setTopicModalOpen(false)} />
        </DialogContent>
      </Dialog>

      <Dialog open={isContentModalOpen} onOpenChange={setContentModalOpen}>
        <DialogContent>
          <ContentValidation onSubmitted={() => setContentModalOpen(false)} />
        </DialogContent>
      </Dialog>

      <Dialog open={isImageModalOpen} onOpenChange={setImageModalOpen}>
        <DialogContent>
          <ImageValidation onSubmitted={() => setImageModalOpen(false)} />
        </DialogContent>
      </Dialog>
    </Card>
  )
} 