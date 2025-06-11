"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useWorkflow } from "@/contexts/workflow-context"
import { CheckCircle, ExternalLink, RotateCcw } from "lucide-react"

export function CompletedStep() {
  const { dispatch } = useWorkflow()

  const handleNewWorkflow = () => {
    dispatch({ type: "RESET_WORKFLOW" })
  }

  const mockTweetUrl = `https://x.com/user/status/${Date.now()}`

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-green-600 dark:text-green-400">
          <CheckCircle className="h-6 w-6" />
          Content Published Successfully!
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="bg-green-50 dark:bg-green-950 p-6 rounded-lg text-center">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">🎉 Great Job!</h3>
          <p className="text-muted-foreground mb-4">
            Your AI-generated content has been successfully published to X. The human-in-the-loop process ensured
            quality and relevance.
          </p>

          <div className="flex gap-4 justify-center">
            <Button asChild className="flex items-center gap-2">
              <a href={mockTweetUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4" />
                View on X
              </a>
            </Button>
            <Button variant="outline" onClick={handleNewWorkflow} className="flex items-center gap-2">
              <RotateCcw className="h-4 w-4" />
              Start New Workflow
            </Button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Workflow Stats</h4>
            <ul className="space-y-1 text-muted-foreground">
              <li>• 4 human validation points completed</li>
              <li>• Content quality ensured</li>
              <li>• Trend relevance verified</li>
              <li>• Historical context validated</li>
            </ul>
          </div>

          <div className="bg-purple-50 dark:bg-purple-950 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Next Steps</h4>
            <ul className="space-y-1 text-muted-foreground">
              <li>• Monitor engagement metrics</li>
              <li>• Analyze audience response</li>
              <li>• Plan follow-up content</li>
              <li>• Start new content workflow</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
