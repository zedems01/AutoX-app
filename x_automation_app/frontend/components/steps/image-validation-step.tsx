"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useWorkflow } from "@/contexts/workflow-context"
import { useQuery, useMutation } from "@tanstack/react-query"
import { mockApiService } from "@/services/mock-data"
import { useToast } from "@/hooks/use-toast"
import { ImageIcon, RefreshCw, CheckCircle, XCircle, Edit3, SkipForward } from "lucide-react"
import Image from "next/image"

export function ImageValidationStep() {
  const { state, dispatch } = useWorkflow()
  const { toast } = useToast()
  const [customPrompt, setCustomPrompt] = useState("")
  const [isEditingPrompt, setIsEditingPrompt] = useState(false)

  const { data: generatedImage, isLoading } = useQuery({
    queryKey: ["generated-image", state.selectedTweet?.id],
    queryFn: () => mockApiService.generateImage("default-prompt"),
    enabled: !!state.selectedTweet && !state.generatedImage,
  })

  const regenerateImageMutation = useMutation({
    mutationFn: (prompt: string) => mockApiService.generateImage(prompt),
    onSuccess: (newImage) => {
      toast({
        title: "New Image Generated",
        description: "Image has been regenerated with your custom prompt",
      })
    },
  })

  const handleApproveImage = () => {
    if (generatedImage) {
      dispatch({ type: "SET_GENERATED_IMAGE", payload: generatedImage })
      dispatch({ type: "SET_STEP", payload: "publishing" })
      toast({
        title: "Image Approved",
        description: "Moving to publishing step",
      })
    }
  }

  const handleRejectImage = () => {
    regenerateImageMutation.mutate(generatedImage?.prompt || "default-prompt")
  }

  const handleCustomPrompt = () => {
    if (customPrompt.trim()) {
      regenerateImageMutation.mutate(customPrompt)
      setIsEditingPrompt(false)
    }
  }

  const handleSkipImage = () => {
    dispatch({ type: "SET_STEP", payload: "publishing" })
    toast({
      title: "Image Skipped",
      description: "Proceeding without image",
    })
  }

  const currentImage = regenerateImageMutation.data || generatedImage

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ImageIcon className="h-5 w-5" />
            Generating Image...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            <span className="ml-2 text-muted-foreground">AI is creating visual content...</span>
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
            <ImageIcon className="h-5 w-5" />
            Image Validation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {state.selectedTweet && (
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Selected Tweet:</h4>
              <p className="text-sm leading-relaxed">{state.selectedTweet.content}</p>
            </div>
          )}

          {currentImage && (
            <>
              <div className="space-y-4">
                <div className="relative">
                  <Image
                    src={currentImage.url || "/placeholder.svg"}
                    alt="Generated image"
                    width={600}
                    height={400}
                    className="w-full max-w-2xl mx-auto rounded-lg border"
                  />
                  {regenerateImageMutation.isPending && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                      <RefreshCw className="h-8 w-8 animate-spin text-white" />
                    </div>
                  )}
                </div>

                <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Image Prompt:</h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsEditingPrompt(!isEditingPrompt)}
                      className="flex items-center gap-2"
                    >
                      <Edit3 className="h-4 w-4" />
                      Edit
                    </Button>
                  </div>
                  <p className="text-sm mb-3">{currentImage.prompt}</p>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>Style: {currentImage.style}</span>
                    <span>Dimensions: {currentImage.dimensions}</span>
                  </div>
                </div>

                {isEditingPrompt && (
                  <div className="space-y-3">
                    <Label htmlFor="custom-prompt">Custom Image Prompt</Label>
                    <Input
                      id="custom-prompt"
                      value={customPrompt}
                      onChange={(e) => setCustomPrompt(e.target.value)}
                      placeholder="Describe the image you want to generate..."
                    />
                    <Button
                      onClick={handleCustomPrompt}
                      disabled={!customPrompt.trim() || regenerateImageMutation.isPending}
                      className="flex items-center gap-2"
                    >
                      {regenerateImageMutation.isPending ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <ImageIcon className="h-4 w-4" />
                      )}
                      Generate New Image
                    </Button>
                  </div>
                )}
              </div>

              <div className="flex gap-4">
                <Button
                  onClick={handleApproveImage}
                  className="flex items-center gap-2"
                  disabled={regenerateImageMutation.isPending}
                >
                  <CheckCircle className="h-4 w-4" />
                  Approve Image
                </Button>
                <Button
                  variant="outline"
                  onClick={handleRejectImage}
                  className="flex items-center gap-2"
                  disabled={regenerateImageMutation.isPending}
                >
                  <XCircle className="h-4 w-4" />
                  Reject & Regenerate
                </Button>
                <Button variant="ghost" onClick={handleSkipImage} className="flex items-center gap-2">
                  <SkipForward className="h-4 w-4" />
                  Skip Image
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
