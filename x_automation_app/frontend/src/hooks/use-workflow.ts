"use client"

import { useEffect, useState } from "react"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { OverallState } from "@/types"

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export const useWorkflow = (threadId: string | null) => {
  const { setWorkflowState } = useWorkflowContext()
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!threadId) {
      return
    }

    const wsUrl = `${WS_BASE_URL}/workflow/ws/${threadId}`
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      console.log("WebSocket connection established")
      setIsConnected(true)
      setError(null)
    }

    socket.onmessage = (event) => {
      try {
        const newState: OverallState = JSON.parse(event.data)
        console.log("Received new state:", newState)
        setWorkflowState(newState)
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e)
        setError("Failed to parse server message.")
      }
    }

    socket.onerror = (event) => {
      console.error("WebSocket error:", event)
      setError("WebSocket connection error.")
      setIsConnected(false)
    }

    socket.onclose = () => {
      console.log("WebSocket connection closed")
      setIsConnected(false)
    }

    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close()
      }
    }
  }, [threadId, setWorkflowState])

  return { isConnected, error }
}
