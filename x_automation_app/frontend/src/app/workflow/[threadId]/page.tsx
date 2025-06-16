"use client"

import { useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { useWorkflow } from "@/hooks/use-workflow"
import { WorkflowStatus } from "@/components/workflow/workflow-status"
import { TopicSelection } from "@/components/workflow/topic-selection"
import { ContentValidation } from "@/components/workflow/content-validation"
import { ImageValidation } from "@/components/workflow/image-validation"
import { toast } from "sonner"

export default function WorkflowDashboardPage() {
  const router = useRouter()
  const params = useParams()
  const { threadId: contextThreadId, setThreadId, workflowState } = useWorkflowContext()
  const threadId = typeof params.threadId === "string" ? params.threadId : null

  // Ensure context has the threadId, especially on page refresh
  useEffect(() => {
    if (threadId && !contextThreadId) {
      setThreadId(threadId)
    } else if (!threadId && !contextThreadId) {
      toast.error("No workflow session found. Redirecting to start.", { duration: 15000 })
      router.replace("/")
    }
  }, [threadId, contextThreadId, setThreadId, router])

  const { isConnected, error } = useWorkflow(contextThreadId)

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

  return (
    <div className="space-y-6">
      <WorkflowStatus isConnected={isConnected} error={error} />
      <div className="mt-6">{renderHumanInTheLoopStep()}</div>
    </div>
  )
} 