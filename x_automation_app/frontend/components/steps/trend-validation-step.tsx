"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useWorkflow } from "@/contexts/workflow-context"
import { useQuery } from "@tanstack/react-query"
import { mockApiService } from "@/services/mock-data"
import { useToast } from "@/hooks/use-toast"
import { TrendingUp, RefreshCw, CheckCircle, XCircle } from "lucide-react"

export function TrendValidationStep() {
  const { state, dispatch } = useWorkflow()
  const { toast } = useToast()

  const {
    data: trendingTopic,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["trending-topic"],
    queryFn: mockApiService.getTrendingTopic,
    enabled: !state.trendingTopic,
  })

  const handleApprove = () => {
    if (trendingTopic) {
      dispatch({ type: "SET_TRENDING_TOPIC", payload: trendingTopic })
      dispatch({ type: "SET_STEP", payload: "context-validation" })
      toast({
        title: "Trend Approved",
        description: "Moving to context validation step",
      })
    }
  }

  const handleReject = () => {
    refetch()
    toast({
      title: "Trend Rejected",
      description: "Fetching new trending topic recommendation",
    })
  }

  const currentTopic = state.trendingTopic || trendingTopic

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Analyzing Trending Topics...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            <span className="ml-2 text-muted-foreground">AI is analyzing current trends...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Trend Recommendation Validation
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {currentTopic && (
          <>
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-semibold mb-2">{currentTopic.topic}</h3>
                <p className="text-muted-foreground mb-4">{currentTopic.description}</p>
                <div className="flex items-center gap-4 mb-4">
                  <Badge variant="secondary">{currentTopic.category}</Badge>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">Relevance Score:</span>
                    <Badge variant={currentTopic.relevanceScore >= 90 ? "default" : "secondary"}>
                      {currentTopic.relevanceScore}%
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                <h4 className="font-medium mb-2">AI Justification:</h4>
                <p className="text-sm">{currentTopic.justification}</p>
              </div>
            </div>

            <div className="flex gap-4">
              <Button onClick={handleApprove} className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                Approve Topic
              </Button>
              <Button variant="outline" onClick={handleReject} className="flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                Reject & Get New Topic
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
