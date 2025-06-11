import type { TrendingTopic, NoteworthyFact, TweetDraft, GeneratedImage } from "@/types/workflow"

export const mockTrendingTopics: TrendingTopic[] = [
  {
    id: "1",
    topic: "Artificial Intelligence in Healthcare",
    description: "AI-powered diagnostic tools are revolutionizing medical care",
    relevanceScore: 95,
    justification: "High engagement on medical AI breakthroughs, trending across tech and healthcare communities",
    category: "Technology",
  },
  {
    id: "2",
    topic: "Sustainable Energy Solutions",
    description: "New developments in renewable energy storage",
    relevanceScore: 88,
    justification: "Growing interest in climate solutions, recent policy announcements driving discussion",
    category: "Environment",
  },
]

export const mockNoteworthyFacts: NoteworthyFact[] = [
  {
    id: "1",
    fact: "The first AI system to diagnose diseases was developed in 1972 at Stanford University, called MYCIN, which could identify bacterial infections.",
    source: "Stanford University Archives",
    relevanceToTrend: "Connects current AI healthcare trends to historical foundation of medical AI",
    historicalContext: "MYCIN was one of the earliest expert systems, paving the way for modern AI diagnostics",
    supportingData: [
      "MYCIN achieved 65% accuracy in diagnosis",
      "It was never used in practice due to legal and ethical concerns",
      "Led to development of modern clinical decision support systems",
    ],
  },
  {
    id: "2",
    fact: "The world's first solar cell was created in 1883 by Charles Fritts, achieving only 1% efficiency compared to today's 26% efficiency panels.",
    source: "IEEE History Center",
    relevanceToTrend: "Shows the remarkable progress in renewable energy technology over 140 years",
    historicalContext: "Early solar technology laid groundwork for modern renewable energy revolution",
    supportingData: [
      "First solar cell used selenium wafers",
      "Modern silicon cells are 26x more efficient",
      "Solar costs have dropped 99% since 1976",
    ],
  },
]

export const mockTweetDrafts: TweetDraft[] = [
  {
    id: "1",
    content:
      "🤖 Did you know? The first AI medical system was built in 1972! MYCIN could diagnose bacterial infections with 65% accuracy. Fast forward to today - AI is revolutionizing healthcare with precision that saves lives daily. #AIHealthcare #MedTech #Innovation",
    characterCount: 247,
    hashtags: ["#AIHealthcare", "#MedTech", "#Innovation"],
    tone: "informative",
  },
  {
    id: "2",
    content:
      "From 1972's MYCIN to today's AI diagnostics - we've come SO far! 🚀 What started as a 65% accurate bacterial infection detector is now saving lives with superhuman precision. The future of healthcare is here! #AI #Healthcare #TechHistory",
    characterCount: 234,
    hashtags: ["#AI", "#Healthcare", "#TechHistory"],
    tone: "engaging",
  },
  {
    id: "3",
    content:
      'MYCIN (1972): "I think you have a bacterial infection... maybe?" 🤔\n\nModern AI: "Based on 10,000 data points, here\'s your precise diagnosis, treatment plan, and recovery timeline." 💪\n\n#AIEvolution #HealthTech #Progress',
    characterCount: 219,
    hashtags: ["#AIEvolution", "#HealthTech", "#Progress"],
    tone: "humorous",
  },
]

export const mockGeneratedImages: GeneratedImage[] = [
  {
    id: "1",
    url: "/placeholder.svg?height=400&width=600",
    prompt:
      "A vintage computer from 1972 next to a modern AI healthcare diagnostic system, showing the evolution of medical technology",
    style: "Digital illustration",
    dimensions: "600x400",
  },
  {
    id: "2",
    url: "/placeholder.svg?height=400&width=600",
    prompt:
      "Split screen showing a 1883 solar cell next to modern solar panels, representing renewable energy evolution",
    style: "Historical comparison",
    dimensions: "600x400",
  },
]

// Simulate API delays
export const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export const mockApiService = {
  getTrendingTopic: async (): Promise<TrendingTopic> => {
    await delay(1500)
    return mockTrendingTopics[0]
  },

  getNoteworthyFact: async (topicId: string): Promise<NoteworthyFact> => {
    await delay(2000)
    return mockNoteworthyFacts[0]
  },

  generateTweetDrafts: async (topicId: string, factId: string): Promise<TweetDraft[]> => {
    await delay(2500)
    return mockTweetDrafts
  },

  generateImage: async (prompt: string): Promise<GeneratedImage> => {
    await delay(3000)
    return mockGeneratedImages[0]
  },

  publishTweet: async (tweetId: string, imageId?: string): Promise<{ success: boolean; tweetUrl: string }> => {
    await delay(1000)
    return {
      success: true,
      tweetUrl: `https://x.com/user/status/${Date.now()}`,
    }
  },
}
