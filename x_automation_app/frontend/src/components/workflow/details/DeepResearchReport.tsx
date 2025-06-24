"use client"

import { useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { FileCheck2, ChevronDown, ChevronUp } from "lucide-react"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const TRUNCATE_LENGTH = 500

export function DeepResearchReport() {
  const { workflowState } = useWorkflowContext()
  const report = workflowState?.final_deep_research_report
  const [isExpanded, setIsExpanded] = useState(false)

  if (!report) {
    return null
  }

  const isLongReport = report.length > TRUNCATE_LENGTH

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
        <div className="relative">
          <pre
            className={cn(
              "p-4 bg-muted rounded-md text-sm whitespace-pre-wrap break-words transition-all duration-300 leading-relaxed",
              isLongReport && !isExpanded ? "max-h-48 overflow-hidden" : ""
            )}
          >
            {report}
          </pre>
          {isLongReport && !isExpanded && (
            <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-background to-transparent" />
          )}
        </div>
        {isLongReport && (
          <div className="flex justify-center -mt-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsExpanded(!isExpanded)}
              className="rounded-full bg-background/50 backdrop-blur-sm cursor-pointer"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 