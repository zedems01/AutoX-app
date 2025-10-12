"use client"

import React from "react"
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
  // FormLabel,
  FormMessage,
} from "@/components/ui/form"
// import {
//   Card,
//   CardContent,
//   CardDescription,
//   CardHeader,
//   CardTitle,
// } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { validateStep } from "@/lib/api"
import { Trend } from "@/types"
import {
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"

const formSchema = z.object({
  selected_topic: z.string().min(1, {
    message: "You need to select a topic to continue.",
  }),
})

interface TopicSelectionProps {
  onSubmitted: () => void
}

export function TopicSelection({ onSubmitted }: TopicSelectionProps) {
  const { threadId, workflowState, setWorkflowState, forceReconnect } = useWorkflowContext()
  const trendingTopics = workflowState?.trending_topics ?? []

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  const mutation = useMutation({
    mutationFn: validateStep,
    onSuccess: (data) => {
      toast.success("Topic selected! The workflow will now continue.", { duration: 20000 })
      setWorkflowState(data)
      // The onSubmitted callback will close the modal immediately.
      onSubmitted()
      // Force WebSocket reconnection to resume the workflow
      if (forceReconnect) {
        setTimeout(() => forceReconnect(), 100)
      }
    },
    onError: (error) => {
      toast.error(`Validation failed: ${error.message}`, { duration: 15000 })
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    if (!threadId) {
      toast.error("Session expired. Please start over.", { duration: 15000 })
      return
    }

    const selectedTopic = trendingTopics.find(
      (topic) => topic.name === values.selected_topic
    )

    if (!selectedTopic) {
      toast.error("Invalid topic selected. Please try again.", { duration: 15000 })
      return
    }

    mutation.mutate({
      thread_id: threadId,
      validation_result: {
        action: "approve",
        data: {
          extra_data: { selected_topic: selectedTopic },
        },
      },
    })
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>Action: Select a Trending Topic</DialogTitle>
        <DialogDescription>
          Choose one of the current trending topics to generate content about.
        </DialogDescription>
      </DialogHeader>
      <div className="py-4 max-h-[70vh] overflow-y-auto">
        {trendingTopics.length > 0 ? (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="selected_topic"
                render={({ field }) => (
                  <FormItem className="space-y-3">
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        className="rounded-lg border"
                      >
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead className="w-[50px]"></TableHead>
                              <TableHead>Topic</TableHead>
                              <TableHead className="text-right">
                                Tweet Count
                              </TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {trendingTopics.map((topic: Trend) => (
                              <TableRow key={topic.name}>
                                <TableCell>
                                  <RadioGroupItem value={topic.name} className="cursor-pointer"/>
                                </TableCell>
                                <TableCell className="font-medium">
                                  {topic.name}
                                </TableCell>
                                <TableCell className="text-right">
                                  {topic.tweet_count ? topic.tweet_count.toLocaleString() : 'N/A'}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </RadioGroup>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button
                  type="submit"
                  className="w-full cursor-pointer"
                  disabled={mutation.isPending}
                >
                  {mutation.isPending && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Approve and Continue
                </Button>
              </DialogFooter>
            </form>
          </Form>
        ) : (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="mr-2 h-8 w-8 animate-spin" />
            <p>Loading trending topics...</p>
          </div>
        )}
      </div>
    </>
  )
} 