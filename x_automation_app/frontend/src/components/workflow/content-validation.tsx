"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { validateStep } from "@/lib/api"
import { ValidationResult } from "@/types"

const formSchema = z.object({
  final_content: z.string().min(1, "Content cannot be empty."),
  final_image_prompts: z.string().optional(),
})

const rejectionSchema = z.object({
  feedback: z
    .string()
    .min(10, "Please provide at least 10 characters of feedback."),
})

interface ContentValidationProps {
  onSubmitted: () => void
}

export function ContentValidation({ onSubmitted }: ContentValidationProps) {
  const { threadId, workflowState, setWorkflowState, forceReconnect } =
    useWorkflowContext()
  const [isRejectionDialogOpen, setRejectionDialogOpen] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    values: {
      final_content: workflowState?.final_content ?? "",
      final_image_prompts:
        workflowState?.final_image_prompts?.join("\n") ?? "",
    },
  })

  const rejectionForm = useForm<z.infer<typeof rejectionSchema>>({
    resolver: zodResolver(rejectionSchema),
    defaultValues: {
      feedback: "",
    },
  })

  const mutation = useMutation({
    mutationFn: validateStep,
    onSuccess: (data) => {
      toast.success("Validation submitted! The workflow will now continue.")
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
    action: "approve" | "reject" | "edit",
    data?: { feedback: string } | { extra_data: any }
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

  const onEditAndApprove = (values: z.infer<typeof formSchema>) => {
    handleValidation("edit", {
      extra_data: {
        final_content: values.final_content,
        final_image_prompts: values.final_image_prompts
          ?.split("\n")
          .filter((p) => p.trim() !== ""),
      },
    })
  }
  const onReject = (values: z.infer<typeof rejectionSchema>) => {
    handleValidation("reject", { feedback: values.feedback })
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>Action: Validate Generated Content</DialogTitle>
        <DialogDescription>
          Review the generated text below. You can approve, reject with
          feedback, or edit the content and then approve.
        </DialogDescription>
      </DialogHeader>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onEditAndApprove)}
          className="space-y-4 pt-4"
        >
          <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-4">
            <FormField
              control={form.control}
              name="final_content"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Generated Content</FormLabel>
                  <FormControl>
                    <Textarea
                      rows={15}
                      className="font-mono text-sm"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="final_image_prompts"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Generated Image Prompts</FormLabel>
                  <FormControl>
                    <Textarea
                      rows={5}
                      className="font-mono text-sm"
                      placeholder="No image prompts were generated for this content."
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <DialogFooter className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onApprove}
              disabled={mutation.isPending}
            >
              Approve
            </Button>

            <Button
              type="button"
              variant="destructive"
              onClick={() => setRejectionDialogOpen(true)}
              disabled={mutation.isPending}
            >
              Reject
            </Button>

            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Save & Approve
            </Button>
          </DialogFooter>
        </form>
      </Form>

      {/* Rejection Dialog - Now OUTSIDE the main form */}
      <Dialog
        open={isRejectionDialogOpen}
        onOpenChange={setRejectionDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Provide Feedback for Rejection</DialogTitle>
            <DialogDescription>
              Please explain why you are rejecting this content so the AI
              can revise it effectively.
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
                        placeholder="e.g., 'This content is too formal...'"
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
    </>
  )
} 