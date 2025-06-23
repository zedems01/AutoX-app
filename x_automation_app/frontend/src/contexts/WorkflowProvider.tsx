"use client"

import React, { createContext, useState, useContext, ReactNode, useMemo } from "react"
import { OverallState, StreamEvent } from "@/types"

interface WorkflowContextType {
  threadId: string | null;
  setThreadId: (id: string | null) => void;
  workflowState: OverallState | null;
  setWorkflowState: React.Dispatch<React.SetStateAction<OverallState | null>>;
  events: StreamEvent[];
  setEvents: React.Dispatch<React.SetStateAction<StreamEvent[]>>;
  showDetails: boolean;
  setShowDetails: (show: boolean) => void;
  forceReconnect?: () => void;
  setForceReconnect: (fn: () => void) => void;
  isConnected: boolean;
  setIsConnected: (isConnected: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
  progress: number
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

export const WorkflowProvider = ({ children }: { children: ReactNode }) => {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [workflowState, setWorkflowState] = useState<OverallState | null>(null);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [showDetails, setShowDetails] = useState(false);
  const [forceReconnect, setForceReconnect] = useState<(() => void) | undefined>(undefined);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  const progress = useMemo(() => {
    const workflowSteps = [
      "trend_harvester",
      "await_topic_selection",
      "auto_select_topic",
      "tweet_searcher",
      "opinion_analyzer",
      "query_generator",
      "web_research",
      "reflection",
      "finalize_answer",
      "writer",
      "quality_assurer",
      "await_content_validation",
      "image_generator",
      "await_image_validation",
      "publicator",
    ]

    if (isComplete) return 100
    if (!workflowState?.current_step) return 0
    if (workflowState.current_step === "END") {
      setIsComplete(true)
      return 100
    }

    let stepForProgress = workflowState.current_step

    if (workflowState.next_human_input_step) {
      stepForProgress = workflowState.next_human_input_step
    }

    const stepIndex = workflowSteps.indexOf(stepForProgress)

    if (stepIndex !== -1) {
      const totalSteps = workflowSteps.length + 1
      return Math.round(((stepIndex + 1) / totalSteps) * 100)
    }

    return 0
  }, [workflowState, isComplete])

  return (
    <WorkflowContext.Provider
      value={{
        threadId,
        setThreadId,
        workflowState,
        setWorkflowState,
        events,
        setEvents,
        showDetails,
        setShowDetails,
        forceReconnect,
        setForceReconnect,
        isConnected,
        setIsConnected,
        error,
        setError,
        progress,
      }}
    >
      {children}
    </WorkflowContext.Provider>
  );
};

export const useWorkflowContext = () => {
  const context = useContext(WorkflowContext);
  if (context === undefined) {
    throw new Error("useWorkflowContext must be used within a WorkflowProvider");
  }
  return context;
};
