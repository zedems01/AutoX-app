"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"

export function DeepResearchReport() {
  const { workflowState } = useWorkflowContext()
  const report = workflowState?.final_deep_research_report

  if (!report) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Deep Research Report</CardTitle>
        <CardDescription>
          The synthesized report from the web research phase.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <p>{report}</p>
        </div>
      </CardContent>
    </Card>
  )
} 