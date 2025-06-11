import { Dashboard } from "@/components/dashboard"
import { WorkflowProvider } from "@/contexts/workflow-context"

export default function Home() {
  return (
    <WorkflowProvider>
      <Dashboard />
    </WorkflowProvider>
  )
}
