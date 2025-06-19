"use client"

import Image from "next/image"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"

export function FinalOutput() {
  const { workflowState } = useWorkflowContext()
  const finalContent = workflowState?.final_content
  const generatedImages = workflowState?.generated_images

  if (!finalContent) {
    return null
  }

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>Final Output</CardTitle>
        <CardDescription>
          The generated content is ready for review.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <pre className="p-4 bg-muted rounded-md text-sm overflow-x-auto whitespace-pre-wrap break-words">
          {finalContent}
        </pre>
        {generatedImages && generatedImages.length > 0 && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Generated Images:</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {generatedImages.map((image, index) => (
                <div
                  key={index}
                  className="relative aspect-square rounded-lg overflow-hidden border"
                >
                  <Image
                    src={image.s3_url}
                    alt={image.image_name || `Generated Image ${index + 1}`}
                    fill
                    className="object-cover"
                    sizes="(max-width: 640px) 100vw, 50vw"
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 