"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { FileCheck2 } from "lucide-react"
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
        <CardTitle className="flex items-center gap-2">
          <FileCheck2 className="h-5 w-5 text-blue-500" />
          Deep Research Report
        </CardTitle>
        <CardDescription>
          The synthesized report from the web research phase.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <pre className="p-4 bg-muted rounded-md text-sm overflow-x-auto whitespace-pre-wrap break-words">
          {report}
        </pre>
      </CardContent>
    </Card>
  )
} 