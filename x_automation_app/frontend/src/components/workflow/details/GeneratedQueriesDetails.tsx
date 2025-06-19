"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"

export function GeneratedQueriesDetails() {
  const { workflowState } = useWorkflowContext()
  const searchQueries = workflowState?.search_query

  if (!searchQueries || searchQueries.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generated Search Queries</CardTitle>
        <CardDescription>
          These queries were used for the deep research phase.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="list-disc space-y-2 pl-5">
          {searchQueries.map((query, index) => (
            <li key={index} className="text-sm">
              <code>{query}</code>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
} 