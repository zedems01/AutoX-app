"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { startWorkflow } from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { WorkflowDashboard } from "@/components/workflow/workflow-dashboard"
import { DetailedOutput } from "@/components/workflow/DetailedOutput"

const formSchema = z
  .object({
    is_autonomous_mode: z.boolean(),
    show_details: z.boolean(),
    output_destination: z.enum(["GET_OUTPUTS", "PUBLISH_X"], {
      required_error: "You need to select an output destination.",
    }),
    has_user_provided_topic: z.boolean(),
    user_provided_topic: z.string().optional(),
    x_content_type: z.enum(["TWEET_THREAD", "SINGLE_TWEET"], {
      required_error: "You need to select a content type.",
    }),
    content_length: z.enum(["SHORT", "MEDIUM", "LONG"], {
      required_error: "You need to select a content length.",
    }),
    brand_voice: z.string().optional(),
    target_audience: z.string().optional(),
    user_config: z
      .object({
        gemini_base_model: z.string().optional(),
        gemini_reasoning_model: z.string().optional(),
        openai_model: z.string().optional(),
        trends_count: z.number().optional(),
        trends_woeid: z.number().optional(),
        max_tweets_to_retrieve: z.number().optional(),
        tweets_language: z.string().optional(),
        content_language: z.string().optional(),
      })
      .optional(),
  })
  .refine(
    (data) => {
      if (data.has_user_provided_topic) {
        return !!data.user_provided_topic && data.user_provided_topic.length > 0
      }
      return true
    },
    {
      message: "A topic is required when you choose to provide one.",
      path: ["user_provided_topic"],
    }
  )

type FormSchemaType = z.infer<typeof formSchema>
const userConfigFields: (keyof NonNullable<FormSchemaType['user_config']>)[] = [
  "gemini_base_model",
  "gemini_reasoning_model",
  "openai_model",
  "trends_count",
  "trends_woeid",
  "max_tweets_to_retrieve",
  "tweets_language",
  "content_language",
]

export default function WorkflowConfigPage() {
  const router = useRouter()
  const { authStatus, session, userDetails, proxy } = useAuth()
  const { setThreadId, setShowDetails } = useWorkflowContext()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      is_autonomous_mode: true,
      show_details: false,
      has_user_provided_topic: false,
      user_provided_topic: "",
      output_destination: "GET_OUTPUTS",
      x_content_type: "SINGLE_TWEET",
      content_length: "SHORT",
      brand_voice: "",
      target_audience: "",
      user_config: {
        gemini_base_model: "",
        gemini_reasoning_model: "",
        openai_model: "",
        trends_count: undefined,
        trends_woeid: undefined,
        max_tweets_to_retrieve: undefined,
        tweets_language: "",
        content_language: "",
      },
    },
  })

  const mutation = useMutation({
    mutationFn: startWorkflow,
    onSuccess: (data) => {
      toast.success("Workflow started successfully!", { duration: 20000 })
      setThreadId(data.thread_id)
    },
    onError: (error) => {
      toast.error(`Workflow failed to start: ${error.message}`, { duration: 15000 })
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    // Check if user needs to be logged in for the selected action
    if (values.output_destination === 'PUBLISH_X' && authStatus !== 'authenticated') {
      toast.error("You must be logged in to publish directly to X.")
      router.push('/login')
      return
    }

    const cleanedValues = JSON.parse(JSON.stringify(values), (key, value) => {
      // Keep number fields that are 0, but remove empty strings.
      if (value === "") {
        return undefined
      }
      return value
    })

    // If user_config becomes an empty object after cleaning, set it to undefined
    if (
      cleanedValues.user_config &&
      Object.keys(cleanedValues.user_config).length === 0
    ) {
      cleanedValues.user_config = undefined
    }
    
    // Set the detail view state before starting the workflow
    setShowDetails(cleanedValues.show_details)

    const payload = {
      ...cleanedValues,
      session: session ?? undefined,
      userDetails: userDetails ?? undefined,
      proxy: proxy ?? undefined,
    }
    mutation.mutate(payload)
  }

  const hasUserProvidedTopic = form.watch("has_user_provided_topic")

  if (authStatus === 'verifying') {
    return (
      <div className="flex justify-center items-center pt-10">
        <Loader2 className="h-8 w-8 animate-spin" />
        <p className="ml-2">Verifying session...</p>
      </div>
    )
  }

  return (
    <div>
      <div className="grid grid-cols-1 gap-12 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Configure Your Workflow</CardTitle>
              <CardDescription>
                Fill out the details below to launch your automated content
                workflow.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-8"
                >
                  {/* --- Core Settings --- */}
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="is_autonomous_mode"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel>Autonomous Mode</FormLabel>
                            <FormDescription>
                              Enable to let the AI run without human validation
                              steps.
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="show_details"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel>Show Detailed View</FormLabel>
                            <FormDescription>
                              Display a detailed breakdown of the workflow
                              outputs.
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="output_destination"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <FormLabel>Output Destination</FormLabel>
                          <FormControl>
                            <RadioGroup
                              onValueChange={field.onChange}
                              defaultValue={field.value}
                              className="flex flex-col space-y-1"
                            >
                              <FormItem className="flex items-center space-x-3 space-y-0">
                                <FormControl>
                                  <RadioGroupItem value="GET_OUTPUTS" />
                                </FormControl>
                                <FormLabel className="font-normal">
                                  Just get the generated content
                                </FormLabel>
                              </FormItem>
                              <FormItem className="flex items-center space-x-3 space-y-0">
                                <FormControl>
                                  <RadioGroupItem value="PUBLISH_X" />
                                </FormControl>
                                <FormLabel className="font-normal">
                                  Publish directly to X (Twitter)
                                </FormLabel>
                              </FormItem>
                            </RadioGroup>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* --- Topic & Content --- */}
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="has_user_provided_topic"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel>Provide Specific Topic</FormLabel>
                            <FormDescription>
                              Do you want to provide your own topic or use trends?
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    {hasUserProvidedTopic && (
                      <FormField
                        control={form.control}
                        name="user_provided_topic"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Your Topic</FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder="e.g., 'The future of artificial intelligence in education'"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    )}
                    <FormField
                      control={form.control}
                      name="x_content_type"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <FormLabel>Content Type</FormLabel>
                          <FormControl>
                            <RadioGroup
                              onValueChange={field.onChange}
                              defaultValue={field.value}
                              className="flex flex-col space-y-1"
                            >
                              <FormItem className="flex items-center space-x-3 space-y-0">
                                <FormControl>
                                  <RadioGroupItem value="TWEET_THREAD" />
                                </FormControl>
                                <FormLabel className="font-normal">
                                  Tweet Thread
                                </FormLabel>
                              </FormItem>
                              <FormItem className="flex items-center space-x-3 space-y-0">
                                <FormControl>
                                  <RadioGroupItem value="SINGLE_TWEET" />
                                </FormControl>
                                <FormLabel className="font-normal">
                                  Single Tweet
                                </FormLabel>
                              </FormItem>
                            </RadioGroup>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="content_length"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Content Length</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select content length" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="SHORT">Short</SelectItem>
                              <SelectItem value="MEDIUM">Medium</SelectItem>
                              <SelectItem value="LONG">Long</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* --- Voice & Audience --- */}
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="brand_voice"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Brand Voice</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Describe the tone and style, e.g., 'Informative, witty, and slightly informal'"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="target_audience"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Target Audience</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="e.g., 'Tech enthusiasts and AI developers'"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* --- Advanced Configuration --- */}
                  <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="item-1">
                      <AccordionTrigger>Advanced Configuration</AccordionTrigger>
                      <AccordionContent className="space-y-4 p-1">
                        <p className="text-sm text-muted-foreground">
                          Optional: Override default agent settings. Leave blank
                          to use defaults.
                        </p>
                        {userConfigFields.map((key) => {
                          const isNumberField = [
                            "trends_count",
                            "trends_woeid",
                            "max_tweets_to_retrieve",
                          ].includes(key)

                          return (
                            <FormField
                              key={key}
                              control={form.control}
                              name={`user_config.${key}`}
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel className="capitalize">
                                    {key.replace(/_/g, " ")}
                                  </FormLabel>
                                  <FormControl>
                                    <Input
                                      {...field}
                                      type={isNumberField ? "number" : "text"}
                                      value={field.value ?? ""}
                                      onChange={(e) => {
                                        if (isNumberField) {
                                          const value = e.target.value
                                          field.onChange(
                                            value === ""
                                              ? undefined
                                              : Number(value)
                                          )
                                        } else {
                                          field.onChange(e)
                                        }
                                      }}
                                    />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          )
                        })}
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={mutation.isPending}
                  >
                    {mutation.isPending && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Launch Workflow
                  </Button>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
        <div className="lg:col-span-3">
          <WorkflowDashboard />
        </div>
      </div>
      <DetailedOutput />
    </div>
  )
}
