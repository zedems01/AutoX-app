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
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
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
import { Label } from "@/components/ui/label"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { validateStep } from "@/lib/api"

const formSchema = z.object({
  final_content: z.string().min(1, "Content cannot be empty."),
})

const rejectionSchema = z.object({
  feedback: z.string().min(10, "Please provide at least 10 characters of feedback."),
})

export function ContentValidation() {
  const { threadId, workflowState, setWorkflowState } = useWorkflowContext()
  const [isRejectionDialogOpen, setRejectionDialogOpen] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    values: {
      final_content: workflowState?.final_content ?? "",
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
      toast.success("Validation submitted! The workflow will now continue.", { duration: 20000 })
      setWorkflowState(data)
      setRejectionDialogOpen(false)
      rejectionForm.reset()
    },
    onError: (error) => {
      toast.error(`Validation failed: ${error.message}`, { duration: 15000 })
    },
  })

  const handleValidation = (
    action: "approve" | "reject" | "edit",
    data?: any
  ) => {
    if (!threadId) {
      toast.error("Session expired. Please start over.", { duration: 15000 })
      return
    }

    mutation.mutate({
      thread_id: threadId,
      validation_result: { action, data },
    })
  }

  const onApprove = () => handleValidation("approve")
  const onEditAndApprove = (values: z.infer<typeof formSchema>) => {
    handleValidation("edit", {
      extra_data: { final_content: values.final_content },
    })
  }
  const onReject = (values: z.infer<typeof rejectionSchema>) => {
    handleValidation("reject", { feedback: values.feedback })
  }

  return (
    <>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onEditAndApprove)}>
          <Card>
            <CardHeader>
              <CardTitle>Action: Validate Generated Content</CardTitle>
              <CardDescription>
                Review the generated text and image prompts below. You can approve,
                reject with feedback, or edit the content and then approve.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
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
              <div className="space-y-2">
                <Label>Generated Image Prompts</Label>
                <div className="p-4 bg-muted rounded-lg space-y-2">
                  {workflowState?.final_image_prompts &&
                  workflowState.final_image_prompts.length > 0 ? (
                    workflowState.final_image_prompts.map((prompt, index) => (
                      <p key={index} className="font-mono text-sm">
                        - {prompt}
                      </p>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      No image prompts were generated for this content.
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end space-x-4">
              <Button
                variant="outline"
                onClick={onApprove}
                disabled={mutation.isPending}
              >
                Approve
              </Button>

              <Dialog open={isRejectionDialogOpen} onOpenChange={setRejectionDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="destructive" disabled={mutation.isPending}>
                    Reject
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Provide Feedback for Rejection</DialogTitle>
                    <DialogDescription>
                      Please explain why you are rejecting this content so the AI can
                      revise it effectively.
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
                                placeholder="e.g., 'This content is too formal. Please make it more casual and add a clear call to action.'"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <DialogFooter>
                        <DialogClose asChild>
                          <Button variant="ghost">Cancel</Button>
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

              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Save & Approve
              </Button>
            </CardFooter>
          </Card>
        </form>
      </Form>
    </>
  )
} 