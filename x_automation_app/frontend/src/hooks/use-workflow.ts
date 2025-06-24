"use client"

import { useEffect, useState } from "react"
import useWebSocket from "react-use-websocket"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { OverallState, StreamEvent } from "@/types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

function isStreamEvent(data: any): data is StreamEvent {
  return "event" in data && "run_id" in data
}

// Mapping from agent/node names in the backend to state fields
const nodeStateMapping: Record<string, (data: any) => Partial<OverallState>> = {
  trend_harvester: (output) => ({ trending_topics: output?.trending_topics }),
  tweet_searcher: (output) => ({ tweet_search_results: output?.tweets }),
  opinion_analyzer: (output) => ({
    opinion_summary: output?.opinion_summary,
    overall_sentiment: output?.overall_sentiment,
    topic_from_opinion_analysis: output?.topic_from_opinion_analysis,
  }),
  query_generator: (output) => ({
    search_query: output?.query_list?.map((q: any) => q.query) || [],
  }),
  finalize_answer: (output) => ({
    final_deep_research_report: output?.final_deep_research_report,
  }),
  writer: (output) => ({
    content_draft: output?.content_draft,
    image_prompts: output?.image_prompts,
  }),
  quality_assurer: (output) => ({
    final_content: output?.final_content,
    final_image_prompts: output?.final_image_prompts,
  }),
  image_generator: (output) => ({ generated_images: output?.images }),
  publicator: (output) => ({ 
    publication_id: output?.publication_id,
  }),
}

export function useWorkflow(threadId: string | null) {
  const [reconnectKey, setReconnectKey] = useState(0)
  const {
    workflowState,
    setWorkflowState,
    setEvents,
    setForceReconnect,
    setIsConnected,
    setError,
  } = useWorkflowContext()

  const socketUrl = threadId
    ? `${API_BASE_URL.replace(
        /^http/,
        "ws",
      )}/workflow/ws/${threadId}?key=${reconnectKey}`
    : null

  const { lastJsonMessage, getWebSocket } = useWebSocket(socketUrl, {
    onOpen: () => {
      console.log("WebSocket connection established.")
      setIsConnected(true)
      setError(null)
    },
    onClose: () => {
      console.log("WebSocket connection closed.")
      setIsConnected(false)
    },
    onError: (event) => {
      console.error("WebSocket error:", event)
      setError("Failed to connect to workflow status.")
    },
    shouldReconnect: (closeEvent) => {
      // Do not reconnect if the workflow has successfully completed.
      if (workflowState?.current_step === "END") {
        console.log("Workflow has ended. Not reconnecting.")
        return false
      }
      // Otherwise, allow reconnection as default behavior.
      return true
    },
  })

  const forceReconnect = () => {
    console.log("Forcing WebSocket reconnection to resume workflow...")
    setReconnectKey((prev) => prev + 1)
  }

  // Register the forceReconnect function with the context
  useEffect(() => {
    setForceReconnect(() => forceReconnect)
  }, [setForceReconnect])

  useEffect(() => {
    if (lastJsonMessage) {
      if (isStreamEvent(lastJsonMessage)) {
        const event = lastJsonMessage
        // Add every event to the raw event log
        setEvents((prevEvents) => [...prevEvents, event])

        setWorkflowState((prevState) => {
          if (!prevState) return null

          const newState: OverallState = { ...prevState }

          if (event.event === "on_chain_start") {
            newState.current_step = event.name
          } else if (event.event === "on_chain_end") {
            const stateUpdater = nodeStateMapping[event.name]
            if (stateUpdater) {
              const updatedFields = stateUpdater(event.data.output)
              Object.assign(newState, updatedFields)
            }
            // If the publicator finishes, we can consider the workflow complete
            if (event.name === "publicator") {
              newState.current_step = "END"
            }
          }
          return newState
        })
      } else {
        // This is the initial, full state sent on connection
        setWorkflowState(lastJsonMessage as OverallState)
      }
    }
  }, [lastJsonMessage, setWorkflowState, setEvents])

  return { forceReconnect }
}
