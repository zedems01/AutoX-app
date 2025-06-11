"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useWorkflow } from "@/contexts/workflow-context"
import { useQuery } from "@tanstack/react-query"
import { mockApiService } from "@/services/mock-data"
import { useToast } from "@/hooks/use-toast"
import { BookOpen, RefreshCw, CheckCircle, XCircle, ExternalLink } from "lucide-react"

export function ContextValidationStep() {
  const { state, dispatch } = useWorkflow()
  const { toast } = useToast()

  const {
    data: noteworthyFact,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["noteworthy-fact", state.trendingTopic?.id],
    queryFn: () => mockApiService.getNoteworthyFact(state.trendingTopic?.id || ""),
    enabled: !!state.trendingTopic && !state.noteworthyFact,
  })

  const handleApprove = () => {
    if (noteworthyFact) {
      dispatch({ type: "SET_NOTEWORTHY_FACT", payload: noteworthyFact })
      dispatch({ type: "SET_STEP", payload: "tweet-validation" })
      toast({
        title: "Context Approved",
        description: "Moving to tweet draft generation",
      })
    }
  }

  const handleReject = () => {
    refetch()
    toast({
      title: "Context Rejected",
      description: "Searching for alternative noteworthy facts",
    })
  }

  const currentFact = state.noteworthyFact || noteworthyFact

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Researching Noteworthy Context...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            <span className="ml-2 text-muted-foreground">AI is researching historical context...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BookOpen className="h-5 w-5" />
          Noteworthy Context Validation
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {state.trendingTopic && (
          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Selected Trend:</h4>
            <p className="text-sm">{state.trendingTopic.topic}</p>
          </div>
        )}

        {currentFact && (
          <>
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-3">Discovered Fact</h3>
                <p className="text-base leading-relaxed mb-4">{currentFact.fact}</p>

                <div className="flex items-center gap-2 mb-4">
                  <Badge variant="outline" className="flex items-center gap-1">
                    <ExternalLink className="h-3 w-3" />
                    {currentFact.source}
                  </Badge>
                </div>
              </div>

              <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Relevance to Current Trend:</h4>
                <p className="text-sm">{currentFact.relevanceToTrend}</p>
              </div>

              <div className="bg-amber-50 dark:bg-amber-950 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Historical Context:</h4>
                <p className="text-sm mb-3">{currentFact.historicalContext}</p>

                <h5 className="font-medium text-sm mb-2">Supporting Data:</h5>
                <ul className="text-sm space-y-1">
                  {currentFact.supportingData.map((data, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-amber-600 dark:text-amber-400">•</span>
                      {data}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="flex gap-4">
              <Button onClick={handleApprove} className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                Approve Context
              </Button>
              <Button variant="outline" onClick={handleReject} className="flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                Find Alternative Facts
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
