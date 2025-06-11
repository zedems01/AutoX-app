"use client"

import type React from "react"
import { createContext, useContext, useReducer, type ReactNode } from "react"
import type {
  WorkflowState,
  WorkflowStep,
  TrendingTopic,
  NoteworthyFact,
  TweetDraft,
  GeneratedImage,
} from "@/types/workflow"

type WorkflowAction =
  | { type: "SET_STEP"; payload: WorkflowStep }
  | { type: "SET_PROCESSING"; payload: boolean }
  | { type: "SET_TRENDING_TOPIC"; payload: TrendingTopic }
  | { type: "SET_NOTEWORTHY_FACT"; payload: NoteworthyFact }
  | { type: "SET_SELECTED_TWEET"; payload: TweetDraft }
  | { type: "SET_GENERATED_IMAGE"; payload: GeneratedImage }
  | { type: "RESET_WORKFLOW" }

const initialState: WorkflowState = {
  currentStep: "trend-validation",
  isProcessing: false,
}

function workflowReducer(state: WorkflowState, action: WorkflowAction): WorkflowState {
  switch (action.type) {
    case "SET_STEP":
      return { ...state, currentStep: action.payload }
    case "SET_PROCESSING":
      return { ...state, isProcessing: action.payload }
    case "SET_TRENDING_TOPIC":
      return { ...state, trendingTopic: action.payload }
    case "SET_NOTEWORTHY_FACT":
      return { ...state, noteworthyFact: action.payload }
    case "SET_SELECTED_TWEET":
      return { ...state, selectedTweet: action.payload }
    case "SET_GENERATED_IMAGE":
      return { ...state, generatedImage: action.payload }
    case "RESET_WORKFLOW":
      return initialState
    default:
      return state
  }
}

const WorkflowContext = createContext<{
  state: WorkflowState
  dispatch: React.Dispatch<WorkflowAction>
} | null>(null)

export function WorkflowProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(workflowReducer, initialState)

  return <WorkflowContext.Provider value={{ state, dispatch }}>{children}</WorkflowContext.Provider>
}

export function useWorkflow() {
  const context = useContext(WorkflowContext)
  if (!context) {
    throw new Error("useWorkflow must be used within a WorkflowProvider")
  }
  return context
}
