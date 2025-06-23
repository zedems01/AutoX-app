"use client"

import { useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { TweetSearched } from "@/types"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  MessageCircle,
  Repeat2,
  Heart,
  BarChart2,
  ChevronDown,
  ChevronUp,
} from "lucide-react"
import { Button } from "@/components/ui/button"

function formatTweetDate(createdAt: string): string {
  const date = new Date(createdAt)
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

function TweetCard({ tweet }: { tweet: TweetSearched }) {
  return (
    <Card className="mb-1">
      <Accordion type="single" collapsible>
        <AccordionItem value="item-1" className="border-b-0">
          <AccordionTrigger className="p-4 pt-1 pb-1 hover:no-underline cursor-pointer">
            <div className="flex items-center space-x-4 text-left">
              <Avatar>
                <AvatarFallback>{tweet.author.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <div className="flex-grow">
                <div className="flex items-center gap-2">
                  <p className="font-bold">{tweet.author.name}</p>
                  <p className="text-sm text-muted-foreground truncate">
                    @{tweet.author.userName}
                  </p>
                </div>
                <p className="text-sm text-muted-foreground">
                  {formatTweetDate(tweet.createdAt)}
                </p>
              </div>
            </div>
          </AccordionTrigger>
          <AccordionContent className="p-4 pt-0">
            <p className="whitespace-pre-wrap">{tweet.text}</p>
            <div className="flex justify-between items-center mt-4 text-muted-foreground text-sm">
              <div className="flex items-center space-x-1">
                <MessageCircle className="h-4 w-4" />
                <span>{tweet.replyCount}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Repeat2 className="h-4 w-4" />
                <span>{tweet.retweetCount}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Heart className="h-4 w-4" />
                <span>{tweet.likeCount}</span>
              </div>
              <div className="flex items-center space-x-1">
                <BarChart2 className="h-4 w-4" />
                <span>{tweet.viewCount}</span>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </Card>
  )
}

const MAX_TWEETS = 20
const TWEETS_INCREMENT = 5

export function TweetSearchResultsDetails() {
  const { workflowState } = useWorkflowContext()
  const tweets = workflowState?.tweet_search_results || []
  const [visibleCount, setVisibleCount] = useState(TWEETS_INCREMENT)

  if (tweets.length === 0) {
    return null
  }

  const sortedTweets = [...tweets]
    .sort(
      (a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )
    .slice(0, MAX_TWEETS)

  const handleShowMore = () => {
    setVisibleCount((prevCount) =>
      Math.min(prevCount + TWEETS_INCREMENT, sortedTweets.length)
    )
  }

  const handleShowLess = () => {
    setVisibleCount(TWEETS_INCREMENT)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5 text-blue-500" />
          Fetched Tweets
        </CardTitle>
        <CardDescription>
          {/* The top {Math.min(MAX_TWEETS, tweets.length)} most recent tweets gathered for analysis. */}
          Some of the most recent tweets gathered for analysis.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {sortedTweets.slice(0, visibleCount).map((tweet, index) => (
          <TweetCard key={index} tweet={tweet} />
        ))}
        {sortedTweets.length > TWEETS_INCREMENT && (
          <div className="flex justify-center items-center gap-2 mt-2">
            {visibleCount < sortedTweets.length && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleShowMore}
                className="rounded-full bg-background/50 backdrop-blur-sm cursor-pointer"
              >
                <ChevronDown className="h-4 w-4" />
              </Button>
            )}
            {visibleCount > TWEETS_INCREMENT && (
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