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
  finalMarkdownContent: string | null;
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

export const WorkflowProvider = ({ children }: { children: ReactNode }) => {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [workflowState, setWorkflowState] = useState<OverallState | null>(null);
  const [events, setEvents] = useState<StreamEvent[]>([]);

  const finalMarkdownContent = useMemo(() => {
    if (workflowState?.final_markdown_content) {
      return workflowState.final_markdown_content;
    }
    // As a fallback, check the last event if the direct state isn't populated yet
    const lastEvent = events[events.length - 1];
    if (lastEvent?.name === "publicator" && lastEvent.event === "on_chain_end") {
      return lastEvent.data?.output?.final_markdown_content || null;
    }
    return null;
  }, [workflowState, events]);

  return (
    <WorkflowContext.Provider
      value={{
        threadId,
        setThreadId,
        workflowState,
        setWorkflowState,
        events,
        setEvents,
        finalMarkdownContent,
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
