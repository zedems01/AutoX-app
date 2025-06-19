# Implementation Plan: Detailed Workflow Output View

This plan outlines the steps to implement a new, optional detailed view for the workflow execution. This view will provide in-depth information about each major step of the process and will be enabled by a user-controlled setting on the main configuration page.

---

### I. Configuration Page (`src/app/page.tsx`)

1.  **Add "Show Details" Toggle:**
    -   Introduce a new `Switch` component to the main form (`formSchema`). This will be labeled "Show Detailed View".
    -   The corresponding form field will be `show_details: z.boolean()`, with a default value of `false`.

2.  **Pass Setting on Workflow Start:**
    -   The value of this `show_details` switch will be captured when the "Launch Workflow" button is clicked.
    -   This boolean value will be used to update a new state variable in our `WorkflowContext`, making the choice available to the entire application.

---

### II. Workflow Context (`src/contexts/WorkflowProvider.tsx`)

1.  **Extend Context State:**
    -   Add a new state variable to the `WorkflowContextType` to manage the visibility of the detailed view: `showDetails: boolean`.
    -   Include the corresponding setter function: `setShowDetails: (show: boolean) => void;`.

2.  **Update State on Workflow Start:**
    -   Modify the `onSubmit` function in `page.tsx`. After a workflow is successfully initiated, it will call `setShowDetails` from the context and pass the value from the new "Show Details" toggle.

---

### III. New Detailed View Components

1.  **Main Container (`src/components/workflow/DetailedOutput.tsx`):**
    -   Create a new file for the main container component.
    -   This component will consume `workflowState` and `showDetails` from `useWorkflowContext`.
    -   It will only render if `showDetails` is `true`, acting as the parent for all the detailed information cards.

2.  **Sub-Components for Each Detail:**
    -   Create several smaller, focused components, each responsible for displaying a specific piece of information. They will be logically organized, likely within a new `src/components/workflow/details/` directory.
    -   **`TrendingTopicsDetails.tsx`**: Displays a formatted list of `trending_topics` from the `workflowState`. It will only render when the data is available.
    -   **`OpinionAnalysisDetails.tsx`**: Displays the `opinion_summary` and `overall_sentiment`.
    -   **`GeneratedQueriesDetails.tsx`**: Displays the list of generated `search_query` strings.
    -   **`DeepResearchReport.tsx`**: Displays the `final_deep_research_report`.
    -   Each of these components will be styled using the existing `Card` component for a consistent look and feel.

---

### IV. Layout and Integration

1.  **Main Page Layout (`src/app/page.tsx`):**
    -   Adjust the main page's grid layout. The top section will continue to hold the configuration form and the `WorkflowDashboard` side-by-side.
    -   A new section will be added below this top grid to render the `<DetailedOutput />` component, which will span the full width of the container.

2.  **Dashboard Component (`src/components/workflow/workflow-dashboard.tsx`):**
    -   Modify the rendering of the `<FinalOutput />` component.
    -   It will now be rendered conditionally based on the context: `{!showDetails && <FinalOutput />}`.

3.  **Detailed View Integration:**
    -   Inside the new `DetailedOutput.tsx` component, the `<FinalOutput />` component will be included at the very end. This ensures it appears as the final step within the detailed view when that mode is active.

This plan ensures a clean separation of concerns, reuses existing components where appropriate, and implements the requested functionality with minimal disruption to the existing application flow.
