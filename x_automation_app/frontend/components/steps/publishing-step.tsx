"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useWorkflow } from "@/contexts/workflow-context"
import { useMutation } from "@tanstack/react-query"
import { mockApiService } from "@/services/mock-data"
import { useToast } from "@/hooks/use-toast"
import { Send, RefreshCw } from "lucide-react"
import Image from "next/image"

export function PublishingStep() {
  const { state, dispatch } = useWorkflow()
  const { toast } = useToast()

  const publishMutation = useMutation({
    mutationFn: () => mockApiService.publishTweet(state.selectedTweet?.id || "", state.generatedImage?.id),
    onSuccess: (result) => {
      dispatch({ type: "SET_STEP", payload: "completed" })
      toast({
        title: "Tweet Published Successfully!",
        description: `Your content is now live on X`,
      })
    },
    onError: () => {
      toast({
        title: "Publishing Failed",
        description: "There was an error publishing your tweet. Please try again.",
        variant: "destructive",
      })
    },
  })

  const handlePublish = () => {
    publishMutation.mutate()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Send className="h-5 w-5" />
          Ready to Publish
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg">
          <h4 className="font-medium mb-2 text-green-800 dark:text-green-200">Content Summary</h4>
          <div className="space-y-3 text-sm">
            <div>
              <span className="font-medium">Trend:</span> {state.trendingTopic?.topic}
            </div>
            <div>
              <span className="font-medium">Context:</span> {state.noteworthyFact?.fact.substring(0, 100)}...
            </div>
          </div>
        </div>

        {state.selectedTweet && (
          <div className="border rounded-lg p-4 bg-white dark:bg-gray-900">
            <h4 className="font-medium mb-3">Final Tweet Content:</h4>
            <p className="leading-relaxed mb-4">{state.selectedTweet.content}</p>

            {state.generatedImage && (
              <div className="mt-4">
                <Image
                  src={state.generatedImage.url || "/placeholder.svg"}
                  alt="Tweet image"
                  width={400}
                  height={267}
                  className="rounded-lg border"
                />
              </div>
            )}

            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <span className="text-sm text-muted-foreground">{state.selectedTweet.characterCount}/280 characters</span>
              <div className="flex gap-2">
                {state.selectedTweet.hashtags.map((tag, index) => (
                  <span key={index} className="text-sm text-blue-600 dark:text-blue-400">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="flex gap-4">
          <Button onClick={handlePublish} disabled={publishMutation.isPending} className="flex items-center gap-2">
            {publishMutation.isPending ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            {publishMutation.isPending ? "Publishing..." : "Publish to X"}
          </Button>
        </div>

        {publishMutation.isPending && (
          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
            <div className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
              <span className="text-sm">Publishing your content to X...</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
