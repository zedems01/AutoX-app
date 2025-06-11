export interface TrendingTopic {
  id: string
  topic: string
  description: string
  relevanceScore: number
  justification: string
  category: string
}

export interface NoteworthyFact {
  id: string
  fact: string
  source: string
  relevanceToTrend: string
  historicalContext: string
  supportingData: string[]
}

export interface TweetDraft {
  id: string
  content: string
  characterCount: number
  hashtags: string[]
  tone: "informative" | "engaging" | "humorous" | "professional"
}

export interface GeneratedImage {
  id: string
  url: string
  prompt: string
  style: string
  dimensions: string
}

export type WorkflowStep =
  | "trend-validation"
  | "context-validation"
  | "tweet-validation"
  | "image-validation"
  | "publishing"
  | "completed"

export interface WorkflowState {
  currentStep: WorkflowStep
  trendingTopic?: TrendingTopic
  noteworthyFact?: NoteworthyFact
  selectedTweet?: TweetDraft
  generatedImage?: GeneratedImage
  isProcessing: boolean
}
