"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { useWorkflow } from "@/contexts/workflow-context"
import { useQuery } from "@tanstack/react-query"
import { mockApiService } from "@/services/mock-data"
import { useToast } from "@/hooks/use-toast"
import type { TweetDraft } from "@/types/workflow"
import { MessageSquare, RefreshCw, CheckCircle, XCircle, Edit3, Hash } from "lucide-react"

export function TweetValidationStep() {
  const { state, dispatch } = useWorkflow()
  const { toast } = useToast()
  const [selectedDraft, setSelectedDraft] = useState<TweetDraft | null>(null)
  const [editedContent, setEditedContent] = useState("")
  const [isEditing, setIsEditing] = useState(false)

  const {
    data: tweetDrafts,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["tweet-drafts", state.trendingTopic?.id, state.noteworthyFact?.id],
    queryFn: () => mockApiService.generateTweetDrafts(state.trendingTopic?.id || "", state.noteworthyFact?.id || ""),
    enabled: !!state.trendingTopic && !!state.noteworthyFact,
  })

  const handleSelectDraft = (draft: TweetDraft) => {
    setSelectedDraft(draft)
    setEditedContent(draft.content)
    setIsEditing(false)
  }

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleSaveEdit = () => {
    if (selectedDraft && editedContent.trim()) {
      const updatedDraft: TweetDraft = {
        ...selectedDraft,
        content: editedContent,
        characterCount: editedContent.length,
      }
      setSelectedDraft(updatedDraft)
      setIsEditing(false)
      toast({
        title: "Tweet Updated",
        description: "Your edits have been saved",
      })
    }
  }

  const handleApprove = () => {
    if (selectedDraft) {
      const finalDraft = isEditing
        ? {
            ...selectedDraft,
            content: editedContent,
            characterCount: editedContent.length,
          }
        : selectedDraft

      dispatch({ type: "SET_SELECTED_TWEET", payload: finalDraft })
      dispatch({ type: "SET_STEP", payload: "image-validation" })
      toast({
        title: "Tweet Approved",
        description: "Moving to image generation",
      })
    }
  }

  const handleRejectAll = () => {
    setSelectedDraft(null)
    setEditedContent("")
    setIsEditing(false)
    refetch()
    toast({
      title: "All Drafts Rejected",
      description: "Generating new tweet options",
    })
  }

  const getCharacterCountColor = (count: number) => {
    if (count > 280) return "text-red-500"
    if (count > 250) return "text-amber-500"
    return "text-green-500"
  }

  const getToneColor = (tone: string) => {
    switch (tone) {
      case "informative":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "engaging":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "humorous":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
      case "professional":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Generating Tweet Drafts...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            <span className="ml-2 text-muted-foreground">AI is crafting engaging tweets...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Tweet Draft Validation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {tweetDrafts?.map((draft) => (
              <div
                key={draft.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedDraft?.id === draft.id
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
                    : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                }`}
                onClick={() => handleSelectDraft(draft)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Badge className={getToneColor(draft.tone)}>{draft.tone}</Badge>
                    <span className={`text-sm font-medium ${getCharacterCountColor(draft.characterCount)}`}>
                      {draft.characterCount}/280
                    </span>
                  </div>
                  {selectedDraft?.id === draft.id && <CheckCircle className="h-5 w-5 text-blue-500" />}
                </div>

                <p className="text-sm leading-relaxed mb-3">{draft.content}</p>

                <div className="flex items-center gap-2">
                  <Hash className="h-3 w-3 text-muted-foreground" />
                  <div className="flex gap-1">
                    {draft.hashtags.map((tag, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {selectedDraft && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Selected Tweet</span>
              <div className="flex gap-2">
                {!isEditing ? (
                  <Button variant="outline" size="sm" onClick={handleEdit} className="flex items-center gap-2">
                    <Edit3 className="h-4 w-4" />
                    Edit
                  </Button>
                ) : (
                  <Button size="sm" onClick={handleSaveEdit}>
                    Save Changes
                  </Button>
                )}
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isEditing ? (
              <div className="space-y-2">
                <Textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="min-h-[120px]"
                  placeholder="Edit your tweet..."
                />
                <div className="flex justify-between items-center">
                  <span className={`text-sm font-medium ${getCharacterCountColor(editedContent.length)}`}>
                    {editedContent.length}/280 characters
                  </span>
                  {editedContent.length > 280 && (
                    <span className="text-sm text-red-500">Tweet exceeds character limit</span>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <p className="leading-relaxed">{selectedDraft.content}</p>
              </div>
            )}

            <div className="flex gap-4">
              <Button
                onClick={handleApprove}
                className="flex items-center gap-2"
                disabled={isEditing && editedContent.length > 280}
              >
                <CheckCircle className="h-4 w-4" />
                Approve Tweet
              </Button>
              <Button variant="outline" onClick={handleRejectAll} className="flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                Reject All & Generate New
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
