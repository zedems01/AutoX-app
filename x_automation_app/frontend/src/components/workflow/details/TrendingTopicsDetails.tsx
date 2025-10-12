"use client"

import React, { useState } from "react"
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
import { TrendingUp, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"

const MAX_TOPICS = 20
const TOPICS_INCREMENT = 5

export function TrendingTopicsDetails() {
  const { workflowState } = useWorkflowContext()
  const trendingTopics = workflowState?.trending_topics || []
  const [visibleCount, setVisibleCount] = useState(TOPICS_INCREMENT)

  if (trendingTopics.length === 0) {
    return null
  }

  const sortedTopics = [...trendingTopics]
    .sort((a, b) => (b.tweet_count || 0) - (a.tweet_count || 0))
    .slice(0, MAX_TOPICS)

  const handleShowMore = () => {
    setVisibleCount((prevCount) =>
      Math.min(prevCount + TOPICS_INCREMENT, sortedTopics.length)
    )
  }

  const handleShowLess = () => {
    setVisibleCount(TOPICS_INCREMENT)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-green-500" />
          Trending Topics
        </CardTitle>
        <CardDescription>
          The top {Math.min(MAX_TOPICS, trendingTopics.length)} most popular
          topics that were identified and analyzed.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="font-bold">Topic</TableHead>
              <TableHead className="text-right font-bold">Tweet Count</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedTopics.slice(0, visibleCount).map((topic, index) => (
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
        {sortedTopics.length > TOPICS_INCREMENT && (
          <div className="flex justify-center items-center gap-2 mt-2">
            {visibleCount < sortedTopics.length && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleShowMore}
                className="rounded-full bg-background/50 backdrop-blur-sm cursor-pointer"
              >
                <ChevronDown className="h-4 w-4" />
              </Button>
            )}
            {visibleCount > TOPICS_INCREMENT && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleShowLess}
                className="rounded-full bg-background/50 backdrop-blur-sm cursor-pointer"
              >
                <ChevronUp className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
} 