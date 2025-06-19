"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"

export function OpinionAnalysisDetails() {
  const { workflowState } = useWorkflowContext()
  const { opinion_summary, overall_sentiment } = workflowState ?? {}

  if (!opinion_summary) {
    return null
  }

  const getSentimentVariant = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case "positive":
        return "green"
      case "negative":
        return "destructive"
      case "neutral":
        return "secondary"
      case "mixed":
        return "yellow"
      default:
        return "default"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Opinion Analysis</CardTitle>
        <CardDescription>
          Summary of public opinion and overall sentiment from social media.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {overall_sentiment && (
          <div className="flex items-center gap-2">
            <h4 className="font-semibold">Overall Sentiment:</h4>
            <Badge variant={getSentimentVariant(overall_sentiment)}>
              {overall_sentiment}
            </Badge>
          </div>
        )}
        <div>
          <h4 className="font-semibold mb-2">Analysis Summary:</h4>
          <p className="text-sm text-muted-foreground">{opinion_summary}</p>
        </div>
      </CardContent>
    </Card>
  )
} 