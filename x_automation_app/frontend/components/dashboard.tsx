"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useWorkflow } from "@/contexts/workflow-context"
import type { WorkflowStep } from "@/types/workflow"
import { CheckCircle, Circle, Clock, Zap } from "lucide-react"
import { ThemeToggle } from "./theme-toggle"

const workflowSteps: { step: WorkflowStep; label: string; description: string }[] = [
  { step: "trend-validation", label: "Trend Validation", description: "Review AI-recommended trending topic" },
  { step: "context-validation", label: "Context Validation", description: "Validate noteworthy historical context" },
  { step: "tweet-validation", label: "Tweet Validation", description: "Review and edit tweet drafts" },
  { step: "image-validation", label: "Image Validation", description: "Approve or modify generated image" },
  { step: "publishing", label: "Publishing", description: "Publish content to X" },
  { step: "completed", label: "Completed", description: "Content successfully published" },
]

export function Dashboard() {
  const { state, dispatch } = useWorkflow()

  const getStepStatus = (step: WorkflowStep) => {
    const currentIndex = workflowSteps.findIndex((s) => s.step === state.currentStep)
    const stepIndex = workflowSteps.findIndex((s) => s.step === step)

    if (stepIndex < currentIndex) return "completed"
    if (stepIndex === currentIndex) return "current"
    return "pending"
  }

  const getStepIcon = (step: WorkflowStep) => {
    const status = getStepStatus(step)
    if (status === "completed") return <CheckCircle className="h-5 w-5 text-green-500" />
    if (status === "current")
      return state.isProcessing ? (
        <Clock className="h-5 w-5 text-blue-500 animate-spin" />
      ) : (
        <Zap className="h-5 w-5 text-blue-500" />
      )
    return <Circle className="h-5 w-5 text-gray-400" />
  }

  const resetWorkflow = () => {
    dispatch({ type: "RESET_WORKFLOW" })
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">AI Agent Content System</h1>
            <p className="text-muted-foreground">Automated content creation for X with human oversight</p>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={resetWorkflow}>
              New Workflow
            </Button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Workflow Progress
              {state.isProcessing && <Badge variant="secondary">Processing...</Badge>}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {workflowSteps.map((step, index) => {
                const status = getStepStatus(step.step)
                return (
                  <div
                    key={step.step}
                    className={`flex items-center gap-4 p-4 rounded-lg border transition-colors ${
                      status === "current"
                        ? "bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800"
                        : status === "completed"
                          ? "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800"
                          : "bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800"
                    }`}
                  >
                    {getStepIcon(step.step)}
                    <div className="flex-1">
                      <h3 className="font-medium">{step.label}</h3>
                      <p className="text-sm text-muted-foreground">{step.description}</p>
                    </div>
                    <Badge
                      variant={status === "completed" ? "default" : status === "current" ? "secondary" : "outline"}
                    >
                      {status === "completed" ? "Done" : status === "current" ? "Active" : "Pending"}
                    </Badge>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Current Step Content */}
        <div className="space-y-6">
          {state.currentStep === "trend-validation" && <TrendValidationStep />}
          {state.currentStep === "context-validation" && <ContextValidationStep />}
          {state.currentStep === "tweet-validation" && <TweetValidationStep />}
          {state.currentStep === "image-validation" && <ImageValidationStep />}
          {state.currentStep === "publishing" && <PublishingStep />}
          {state.currentStep === "completed" && <CompletedStep />}
        </div>
      </main>
    </div>
  )
}

// Import the step components (we'll create these next)
import { TrendValidationStep } from "./steps/trend-validation-step"
import { ContextValidationStep } from "./steps/context-validation-step"
import { TweetValidationStep } from "./steps/tweet-validation-step"
import { ImageValidationStep } from "./steps/image-validation-step"
import { PublishingStep } from "./steps/publishing-step"
import { CompletedStep } from "./steps/completed-step"
