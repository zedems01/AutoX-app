"use client"

import React from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { Users } from "lucide-react"

export function OpinionAnalysisDetails() {
  const { workflowState } = useWorkflowContext()
  const { opinion_summary, overall_sentiment } = workflowState ?? {}

  if (!opinion_summary) {
    return null
  }

  const getSentimentClassName = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case "positive":
        return "border-green-300 bg-green-50 text-green-700 dark:border-green-700 dark:bg-green-950 dark:text-green-400"
      case "negative":
        return "border-red-300 bg-red-50 text-red-700 dark:border-red-700 dark:bg-red-950 dark:text-red-400"
      case "neutral":
        return "border-gray-300 bg-gray-50 text-gray-700 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-400"
      case "mixed":
        return "border-yellow-300 bg-yellow-50 text-yellow-700 dark:border-yellow-700 dark:bg-yellow-950 dark:text-yellow-400"
      default:
        return "border-gray-300 bg-gray-50 text-gray-700 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-400"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5 text-purple-500" />
          Opinion Analysis
        </CardTitle>
        <CardDescription>
          Summary of public opinion and overall sentiment from social media.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {overall_sentiment && (
          <div className="flex items-center gap-2">
            <h4 className="font-semibold">Overall Sentiment:</h4>
            <Badge variant="outline" className={getSentimentClassName(overall_sentiment)}>
              {overall_sentiment}
            </Badge>
          </div>
        )}
        <div>
          <h4 className="font-semibold mb-2">Analysis Summary:</h4>
          <p className="text-sm text-muted-foreground leading-relaxed">{opinion_summary}</p>
        </div>
      </CardContent>
    </Card>
  )
} 