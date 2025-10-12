"use client"

import React from "react"
import { useWorkflowContext } from "@/contexts/WorkflowProvider"
import { TrendingTopicsDetails } from "./details/TrendingTopicsDetails"
import { TweetSearchResultsDetails } from "./details/TweetSearchResultsDetails"
import { OpinionAnalysisDetails } from "./details/OpinionAnalysisDetails"
// import { GeneratedQueriesDetails } from "./details/GeneratedQueriesDetails"
import { DeepResearchReport } from "./details/DeepResearchReport"
import { FinalOutput } from "./FinalOutput"

export function DetailedOutput() {
  const { showDetails } = useWorkflowContext()

  if (!showDetails) {
    return null
  }

  return (
    <div className="mt-8 space-y-6">
      <h2 className="text-2xl font-bold text-center">Detailed Workflow Output</h2>
      <TrendingTopicsDetails />
      <TweetSearchResultsDetails />
      <OpinionAnalysisDetails />
      {/* <GeneratedQueriesDetails /> */}
      <DeepResearchReport />
      <FinalOutput />
    </div>
  )
} 