import { renderHook, act } from "@testing-library/react"
import { WorkflowProvider, useWorkflow } from "@/contexts/workflow-context"
import type { ReactNode } from "react"

const wrapper = ({ children }: { children: ReactNode }) => <WorkflowProvider>{children}</WorkflowProvider>

describe("WorkflowContext", () => {
  it("should initialize with default state", () => {
    const { result } = renderHook(() => useWorkflow(), { wrapper })

    expect(result.current.state.currentStep).toBe("trend-validation")
    expect(result.current.state.isProcessing).toBe(false)
    expect(result.current.state.trendingTopic).toBeUndefined()
  })

  it("should update step when SET_STEP action is dispatched", () => {
    const { result } = renderHook(() => useWorkflow(), { wrapper })

    act(() => {
      result.current.dispatch({ type: "SET_STEP", payload: "context-validation" })
    })

    expect(result.current.state.currentStep).toBe("context-validation")
  })

  it("should set processing state", () => {
    const { result } = renderHook(() => useWorkflow(), { wrapper })

    act(() => {
      result.current.dispatch({ type: "SET_PROCESSING", payload: true })
    })

    expect(result.current.state.isProcessing).toBe(true)
  })

  it("should reset workflow to initial state", () => {
    const { result } = renderHook(() => useWorkflow(), { wrapper })

    // Set some state
    act(() => {
      result.current.dispatch({ type: "SET_STEP", payload: "completed" })
      result.current.dispatch({ type: "SET_PROCESSING", payload: true })
    })

    // Reset workflow
    act(() => {
      result.current.dispatch({ type: "RESET_WORKFLOW" })
    })

    expect(result.current.state.currentStep).toBe("trend-validation")
    expect(result.current.state.isProcessing).toBe(false)
  })
})
