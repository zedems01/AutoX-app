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
