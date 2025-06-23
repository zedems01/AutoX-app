"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { TweetSearched } from "@/types"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MessageCircle, Repeat2, Heart, BarChart2 } from "lucide-react"

function TweetCard({ tweet }: { tweet: TweetSearched }) {
  return (
    <Card className="mb-4">
      <CardHeader>
        <div className="flex items-center space-x-4">
          <Avatar>
            {/* Placeholder for author image */}
            <AvatarFallback>{tweet.author.name.charAt(0)}</AvatarFallback>
          </Avatar>
          <div>
            <p className="font-bold">{tweet.author.name}</p>
            <p className="text-sm text-muted-foreground">@{tweet.author.userName}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
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
      </CardContent>
    </Card>
  )
}

export function TweetSearchResultsDetails() {
  const { workflowState } = useWorkflowContext()
  const tweets = workflowState?.tweet_search_results

  if (!tweets || tweets.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          Fetched Tweets
        </CardTitle>
        <CardDescription>
          A selection of tweets gathered for analysis.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {tweets.map((tweet, index) => (
          <TweetCard key={index} tweet={tweet} />
        ))}
      </CardContent>
    </Card>
  )
} 