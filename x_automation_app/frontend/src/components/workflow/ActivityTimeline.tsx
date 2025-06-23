"use client"

import {
  BrainCircuit,
  FileCheck2,
  Hand,
  Image,
  ListFilter,
  Loader2,
  PenSquare,
  Search,
  Send,
  ShieldCheck,
  TrendingUp,
  Users,
  CheckCircle,
} from "lucide-react"

import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { StreamEvent } from "@/types"
import { Badge } from "@/components/ui/badge"

const getStepConfig = (event: StreamEvent) => {
  let icon = Loader2
  let title = "Processing..."
  let description = `Running: ${event.name}`
  let status: "running" | "completed" | "error" =
    event.event === "on_chain_start" ? "running" : "completed"

  // Special handling for waiting steps to prevent eternal spinners
  if (event.name.startsWith("await_")) {
    status = "completed"
  }

  switch (event.name) {
    case "trend_harvester":
      icon = TrendingUp
      title = "Trend Harvesting"
      if (status === "completed") {
        const trends = event.data.output?.trending_topics || []
        const trendNames = trends.map((t: any) => t.name).join(", ")
        description = `Gathered ${trends.length} trending topics: ${trendNames}.`
      }
      break
    case "tweet_searcher":
      icon = Search
      title = "Tweet Searching"
      if (status === "completed") {
        const tweets = event.data.output?.tweet_search_results || []
        const topic = event.data.input?.selected_topic?.name || "the selected topic"
        description = `Found ${tweets.length} tweets for "${topic}".`
      }
      break
    case "opinion_analyzer":
      icon = Users
      title = "Opinion Analysis"
      if (status === "completed") {
        const sentiment = event.data.output?.overall_sentiment || "N/A"
        description = `Analyzed opinions. Overall sentiment: ${sentiment}.`
      }
      break
    case "query_generator":
      icon = ListFilter
      title = "Generating Search Queries"
      if (status === "completed") {
        const queries = event.data.output?.query_list || []
        description = `Generated queries: ${queries.join(", ")}`
      }
      break
    case "web_research":
      icon = Search
      title = "Web Research"
      if (status === "completed") {
        const sources = event.data.output?.sources_gathered || []
        const query = event.data.input?.search_query || "the provided topic"
        description = `Gathered ${sources.length} sources for query: "${query}".`
      }
      break
    case "reflection":
      icon = BrainCircuit
      title = "Reflection"
      if (status === "completed") {
        const critique =
          event.data.output?.critique || "No further information required."
        description = `Critique: ${critique.substring(0, 200)}...`
      }
      break
    case "finalize_answer":
      icon = FileCheck2
      title = "Finalizing Deep Research"
      description = "Successfully finalized deep research report."
      break
    case "writer":
      icon = PenSquare
      title = "Content Writing"
      if (status === "completed") {
        const voice = event.data.input?.brand_voice
        const audience = event.data.input?.target_audience
        let details = "Drafted content and image prompts."
        if (voice) details += ` Voice: ${voice}.`
        if (audience) details += ` Audience: ${audience}.`
        description = details
      }
      break
    case "quality_assurer":
      icon = ShieldCheck
      title = "Quality Assurance"
      description = "Content and prompts reviewed for quality."
      break
    case "image_generator":
      icon = Image
      title = "Image Generation"
      if (status === "completed") {
        const images = event.data.output?.images || []
        if (images.length > 0) {
          const imageNames = images.map((img: any) => img.image_name).join(", ")
          description = `Generated ${images.length} images: ${imageNames}.`
        } else {
          description = "No images were generated."
        }
      }
      break
    case "publicator":
      icon = Send
      title = "Publication & Formatting"
      if (status === "completed") {
        const id = event.data.output?.publication_id
        const destination = event.data.input?.output_destination

        if (destination === "Download") {
          description =
            "Final content has been generated and formatted for download."
        } else if (id) {
          description = `Content published with ID: ${id}.`
        } else {
          description = "Content processed and packaged for publication."
        }
      }
      break
    case "await_topic_selection":
      icon = Hand
      title = "Awaiting Topic Selection"
      description = "Please select a topic to proceed."
      break
    case "await_content_validation":
      icon = Hand
      title = "Awaiting Content Validation"
      description = "Please review and validate the content."
      break
    case "await_image_validation":
      icon = Hand
      title = "Awaiting Image Validation"
      description = "Please review and validate the images."
      break
    default:
      title = event.name.replace(/_/g, " ")
      description = `Status: ${status}`
  }

  return {
    icon: icon,
    title,
    description,
    status,
  }
}

function TimelineItem({ event }: { event: StreamEvent }) {
  const { icon: Icon, title, description, status } = getStepConfig(event)
  const isRunning = status === "running"
  const isCompleted = status === "completed"

  return (
    <div className="flex items-start space-x-4">
      <div className="flex flex-col items-center">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-full ${
            isRunning
              ? "bg-primary/20 text-primary"
              : isCompleted
                ? "bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400"
                : "bg-muted"
          }`}
        >
          <Icon className={`h-5 w-5 ${isRunning ? "animate-spin" : ""}`} />
        </div>
        <div className="h-full w-px bg-muted"></div>
      </div>
      <div className="pt-2">
        <h3 className="flex items-center gap-2 font-semibold">
          {title}
          {isCompleted && (
            <CheckCircle className="h-5 w-5 text-green-500" />
          )}
        </h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}

export function ActivityTimeline() {
  const { events } = useWorkflowContext()

  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-muted rounded-lg">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">
          Waiting for workflow to start and send its first event...
        </p>
      </div>
    )
  }

  // Create a map of run IDs to the latest event for that run
  const latestEventsMap = new Map<string, StreamEvent>()
  events.forEach((event) => {
    // Only track our allowed events
    if (getStepConfig(event).title !== "Processing...") {
      latestEventsMap.set(event.run_id, event)
    }
  })

  // Convert the map back to an array for rendering
  const uniqueLatestEvents = Array.from(latestEventsMap.values())

  return (
    <div className="space-y-4 relative">
      {uniqueLatestEvents.map((event, index) => (
        <div key={`${event.run_id}-${index}`} className="relative">
          <TimelineItem event={event} />
          {index < uniqueLatestEvents.length - 1 && (
            <div
              className="absolute left-5 top-10 h-full border-l-2 border-border"
              style={{ height: "calc(100% - 2.5rem)" }}
            />
          )}
        </div>
      ))}
      <WorkflowCompletionStatus events={uniqueLatestEvents} />
    </div>
  )
}

function WorkflowCompletionStatus({ events }: { events: StreamEvent[] }) {
  const { workflowState } = useWorkflowContext()
  const lastEvent = events[events.length - 1]

  if (workflowState?.current_step === "END") {
    return (
      <Badge variant="green" className="mt-4">
        Workflow Completed
      </Badge>
    )
  }

  if (
    lastEvent?.name.startsWith("await_") &&
    lastEvent?.event === "on_chain_start"
  ) {
    return (
      <Badge variant="yellow" className="mt-4">
        Action Required
      </Badge>
    )
  }

  return null
} 