"use client"

import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { Code, Eye } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"

export function FinalOutput() {
  const { finalMarkdownContent } = useWorkflowContext()
  const [viewMode, setViewMode] = useState<"rendered" | "raw">("rendered")

  if (!finalMarkdownContent) {
    return null
  }

  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Final Output</CardTitle>
          <CardDescription>
            The generated content is ready for review.
          </CardDescription>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === "rendered" ? "secondary" : "ghost"}
            size="icon"
            onClick={() => setViewMode("rendered")}
            aria-label="Rendered view"
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === "raw" ? "secondary" : "ghost"}
            size="icon"
            onClick={() => setViewMode("raw")}
            aria-label="Raw markdown view"
          >
            <Code className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {viewMode === "rendered" ? (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {finalMarkdownContent}
            </ReactMarkdown>
          </div>
        ) : (
          <pre className="p-4 bg-muted rounded-md text-sm overflow-x-auto">
            <code>{finalMarkdownContent}</code>
          </pre>
        )}
      </CardContent>
    </Card>
  )
} 