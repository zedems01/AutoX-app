import type React from "react"
import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { TrendValidationStep } from "@/components/steps/trend-validation-step"
import { WorkflowProvider } from "@/contexts/workflow-context"
import { mockTrendingTopics } from "@/services/mock-data"

// Mock the toast hook
jest.mock("@/hooks/use-toast", () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <WorkflowProvider>{children}</WorkflowProvider>
    </QueryClientProvider>
  )
}

describe("TrendValidationStep", () => {
  it("should render loading state initially", () => {
    const Wrapper = createWrapper()
    render(<TrendValidationStep />, { wrapper: Wrapper })

    expect(screen.getByText("Analyzing Trending Topics...")).toBeInTheDocument()
    expect(screen.getByText("AI is analyzing current trends...")).toBeInTheDocument()
  })

  it("should display trending topic when loaded", async () => {
    const Wrapper = createWrapper()
    render(<TrendValidationStep />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText(mockTrendingTopics[0].topic)).toBeInTheDocument()
    })

    expect(screen.getByText(mockTrendingTopics[0].description)).toBeInTheDocument()
    expect(screen.getByText("Approve Topic")).toBeInTheDocument()
    expect(screen.getByText("Reject & Get New Topic")).toBeInTheDocument()
  })

  it("should have approve and reject buttons", async () => {
    const Wrapper = createWrapper()
    render(<TrendValidationStep />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText("Approve Topic")).toBeInTheDocument()
    })

    const approveButton = screen.getByText("Approve Topic")
    const rejectButton = screen.getByText("Reject & Get New Topic")

    expect(approveButton).toBeEnabled()
    expect(rejectButton).toBeEnabled()
  })
})
