"use client"

import { useState } from "react"
import { ImageWithFallback } from "@/components/shared/ImageWithFallback"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { validateStep } from "@/lib/api"
import { ValidationResult } from "@/types"
import { cn } from "@/lib/utils"

const rejectionSchema = z.object({
  feedback: z
    .string()
    .min(10, "Please provide at least 10 characters of feedback."),
})

interface ImageValidationProps {
  onSubmitted: () => void
}

export function ImageValidation({ onSubmitted }: ImageValidationProps) {
  const { threadId, workflowState, setWorkflowState, forceReconnect } =
    useWorkflowContext()
  const [isRejectionDialogOpen, setRejectionDialogOpen] = useState(false)
  const generatedImages = workflowState?.generated_images ?? []
  const isSingleImage = generatedImages.length === 1

  const rejectionForm = useForm<z.infer<typeof rejectionSchema>>({
    resolver: zodResolver(rejectionSchema),
    defaultValues: {
      feedback: "",
    },
  })

  const mutation = useMutation({
    mutationFn: validateStep,
    onSuccess: (data) => {
      toast.success("Validation submitted! The workflow will now continue.", { duration: 20000 })
      setWorkflowState(data)
      setRejectionDialogOpen(false)
      rejectionForm.reset()
      onSubmitted() // Close the main modal
      // Force WebSocket reconnection to resume the workflow
      if (forceReconnect) {
        setTimeout(() => forceReconnect(), 100)
      }
    },
    onError: (error) => {
      toast.error(`Validation failed: ${error.message}`)
    },
  })

  const handleValidation = (
    action: "approve" | "reject",
    data?: { feedback: string }
  ) => {
    if (!threadId) {
      toast.error("Session expired. Please start over.")
      return
    }

    const validationResult: ValidationResult = { action }
    if (data) {
      validationResult.data = data
    }

    mutation.mutate({
      thread_id: threadId,
      validation_result: validationResult,
    })
  }

  const onApprove = () => handleValidation("approve")
  const onReject = (values: z.infer<typeof rejectionSchema>) => {
    handleValidation("reject", { feedback: values.feedback })
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>Action: Validate Generated Images</DialogTitle>
        <DialogDescription>
          Review the images generated for your content. Approve them to continue,
          or reject them with feedback to try again.
        </DialogDescription>
      </DialogHeader>
      <div className="py-4">
        {generatedImages.length > 0 ? (
          <div
            className={cn(
              "gap-4 max-h-[60vh] overflow-y-auto pr-4",
              isSingleImage
                ? "flex justify-center"
                : "grid grid-cols-1 sm:grid-cols-2"
            )}
          >
            {generatedImages.map((image, index) => (
              <div
                key={index}
                className={cn(
                  "relative aspect-square rounded-lg overflow-hidden border",
                  isSingleImage && "w-full sm:w-4/5"
                )}
              >
                <ImageWithFallback
                  src={image.s3_url}
                  fallbackSrc={`/images/${image.image_name}`}
                  alt={image.image_name || `Generated Image ${index + 1}`}
                  fill
                  className="object-cover"
                  sizes="(max-width: 640px) 100vw, 50vw"
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center p-8 border-dashed border-2 rounded-lg">
            <Loader2 className="mr-2 h-8 w-8 animate-spin" />
            <p>Loading generated images...</p>
          </div>
        )}
      </div>
      <DialogFooter className="flex justify-end space-x-2 pt-4">
        <Dialog
          open={isRejectionDialogOpen}
          onOpenChange={setRejectionDialogOpen}
        >
          <DialogTrigger asChild>
            <Button
              type="button"
              variant="destructive"
              disabled={mutation.isPending}
              className="cursor-pointer"
            >
              Reject
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Provide Feedback for Rejection</DialogTitle>
              <DialogDescription>
                Please explain why you are rejecting these images so the AI can
                generate better ones.
              </DialogDescription>
            </DialogHeader>
            <Form {...rejectionForm}>
              <form
                onSubmit={rejectionForm.handleSubmit(onReject)}
                className="space-y-4"
              >
                <FormField
                  control={rejectionForm.control}
                  name="feedback"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Textarea
                          rows={5}
                          placeholder="e.g., 'These images are too abstract...'"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <DialogFooter>
                  <DialogClose asChild>
                    <Button type="button" variant="ghost">
                      Cancel
                    </Button>
                  </DialogClose>
                  <Button
                    type="submit"
                    variant="destructive"
                    disabled={mutation.isPending}
                  >
                    {mutation.isPending && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Submit Rejection
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>

        <Button
          type="button"
          onClick={onApprove}
          disabled={mutation.isPending}
          className="cursor-pointer"
        >
          {mutation.isPending && (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          )}
          Approve Images
        </Button>
      </DialogFooter>
    </>
  )
} 