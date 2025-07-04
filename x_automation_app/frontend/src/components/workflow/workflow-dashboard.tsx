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
import { Loader2, RefreshCw, BarChart } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { ActivityTimeline } from "@/components/workflow/ActivityTimeline"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"

export function WorkflowDashboard() {
  const {
    threadId,
    workflowState,
    showDetails,
    isConnected,
    error,
    progress,
    events,
  } = useWorkflowContext()
  useWorkflow(threadId)
  const [isTopicModalOpen, setTopicModalOpen] = useState(false)
  const [isContentModalOpen, setContentModalOpen] = useState(false)
  const [isImageModalOpen, setImageModalOpen] = useState(false)

  const isPublicatorCompleted = events.some(
    (event) => event.name === "publicator" && event.event !== "on_chain_start"
  )

  useEffect(() => {
    const nextStep = workflowState?.next_human_input_step
    setTopicModalOpen(nextStep === "await_topic_selection")
    setContentModalOpen(nextStep === "await_content_validation")
    setImageModalOpen(nextStep === "await_image_validation")
  }, [workflowState?.next_human_input_step])

  if (!threadId) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart className="h-6 w-6 text-green-500" />
            <CardTitle>Workflow Timeline</CardTitle>
          </div>
          <div className="flex items-center gap-4">
            <WorkflowStatus />
            {(workflowState?.current_step === "END" || isPublicatorCompleted) && (
              <Button onClick={() => window.location.reload()} size="sm" className="cursor-pointer">
                Start New Workflow
              </Button>
            )}
          </div>
        </div>
        <Progress value={progress} className="mt-4" />
      </CardHeader>
      <CardContent className="space-y-6 pt-4">
        <ScrollArea className="h-[60vh] p-1">
          <ActivityTimeline />
        </ScrollArea>
        {!showDetails && <FinalOutput />}
      </CardContent>

      {/* Modals for validation */}
      <Dialog open={isTopicModalOpen} onOpenChange={setTopicModalOpen}>
        <DialogContent
          className="max-w-4xl"
          onPointerDownOutside={(e) => {
            e.preventDefault()
          }}
        >
          <TopicSelection onSubmitted={() => setTopicModalOpen(false)} />
        </DialogContent>
      </Dialog>

      <Dialog open={isContentModalOpen} onOpenChange={setContentModalOpen}>
        <DialogContent
          className="max-w-4xl"
          onPointerDownOutside={(e) => {
            e.preventDefault()
          }}
        >
          <ContentValidation onSubmitted={() => setContentModalOpen(false)} />
        </DialogContent>
      </Dialog>

      <Dialog open={isImageModalOpen} onOpenChange={setImageModalOpen}>
        <DialogContent
          className="max-w-4xl"
          onPointerDownOutside={(e) => {
            e.preventDefault()
          }}
        >
          <ImageValidation onSubmitted={() => setImageModalOpen(false)} />
        </DialogContent>
      </Dialog>
    </Card>
  )
} 