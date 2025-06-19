"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"

export function TrendingTopicsDetails() {
  const { workflowState } = useWorkflowContext()
  const trendingTopics = workflowState?.trending_topics

  if (!trendingTopics || trendingTopics.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Trending Topics</CardTitle>
        <CardDescription>
          The following trending topics were identified and analyzed.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Topic</TableHead>
              <TableHead className="text-right">Tweet Volume</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trendingTopics.map((topic, index) => (
              <TableRow key={index}>
                <TableCell className="font-medium">{topic.name}</TableCell>
                <TableCell className="text-right">
                  {topic.tweet_count
                    ? topic.tweet_count.toLocaleString()
                    : "N/A"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
} 