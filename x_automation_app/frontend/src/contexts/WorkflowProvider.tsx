"use client"

import React, { createContext, useState, useContext, ReactNode } from "react"
import { OverallState } from "@/types"

interface WorkflowContextType {
  threadId: string | null;
  setThreadId: (id: string | null) => void;
  workflowState: OverallState | null;
  setWorkflowState: React.Dispatch<React.SetStateAction<OverallState | null>>;
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

export const WorkflowProvider = ({ children }: { children: ReactNode }) => {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [workflowState, setWorkflowState] = useState<OverallState | null>(null);

  return (
    <WorkflowContext.Provider
      value={{ threadId, setThreadId, workflowState, setWorkflowState }}
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
