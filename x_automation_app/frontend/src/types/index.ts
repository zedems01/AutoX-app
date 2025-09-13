// --- API Payloads ---

export interface LoginPayload {
  user_name: string;
  email: string;
  password: string;
  proxy: string;
  totp_secret: string;
}

export interface StartWorkflowPayload {
  is_autonomous_mode: boolean;
  output_destination?: "GET_OUTPUTS" | "PUBLISH_X";
  has_user_provided_topic: boolean;
  user_provided_topic?: string;
  x_content_type?: "TWEET_THREAD" | "SINGLE_TWEET";
  content_length?: "SHORT" | "MEDIUM" | "LONG";
  brand_voice?: string;
  target_audience?: string;
  user_config?: UserConfigSchema;
  
  session?: string;
  user_details?: UserDetails;
  proxy?: string;
}

export interface ValidateSessionPayload {
  session: string;
  proxy: string;
}

export interface ValidationPayload {
  thread_id: string;
  validation_result: ValidationResult;
}

// --- API Responses ---

export interface LoginResponse {
  session: string;
  userDetails: UserDetails;
  proxy: string;
}

export interface StartWorkflowResponse {
  thread_id: string;
  initial_state: OverallState;
}

export interface StreamEvent {
  event:
    | "on_chain_start"
    | "on_chain_end"
    | "on_tool_start"
    | "on_tool_end"
    | "on_llm_start"
    | "on_llm_stream"
    | "on_llm_end"
    | "on_retriever_start"
    | "on_retriever_end";
  name: string;
  run_id: string;
  tags: string[];
  metadata: Record<string, any>;
  data: {
    input?: any;
    output?: any;
    chunk?: any;
  };
}

// --- Core State & Supporting Types ---

export interface UserDetails {
  name?: string;
  username?: string;
}

export interface UserSession {
  session: string;
  userDetails: UserDetails;
  proxy: string;
}

export interface UserConfigSchema {
    gemini_model?: string;
    openrouter_model?: string;
    trends_count?: number;
    trends_woeid?: number;
    max_tweets_to_retrieve?: number;
    tweets_language?: string;
    content_language?: string;
}

export interface ValidationResult {
  action: "approve" | "reject" | "edit";
  data?: {
    feedback?: string;
    extra_data?: {
      final_content?: string;
      [key: string]: any; // Allow other properties
    };
  };
}

export interface Trend {
  name: string;
  tweet_count: number;
}

export interface TweetAuthor {
  userName: string;
  name: string;
  isVerified: boolean;
  followers: number;
  following: number;
}

export interface TweetSearched {
  text: string;
  source: string;
  retweetCount: number;
  replyCount: number;
  likeCount: number;
  quoteCount: number;
  viewCount: number;
  createdAt: string;
  lang: string;
  isReply: boolean;
  author: TweetAuthor;
}

export interface GeneratedImage {
  is_generated: boolean;
  image_name: string;
  local_file_path: string;
  s3_url: string;
}

export interface OverallState {
  // From login
  login_data?: string;
  proxy?: string;
  session?: string;
  user_details?: any;

  // From workflow start
  is_autonomous_mode: boolean;
  output_destination?: "GET_OUTPUTS" | "PUBLISH_X";
  has_user_provided_topic: boolean;
  user_provided_topic?: string;
  x_content_type?: string;
  content_length?: "SHORT" | "MEDIUM" | "LONG";
  brand_voice?: string;
  target_audience?: string;
  user_config?: UserConfigSchema;

  // From graph execution
  trending_topics?: Trend[];
  selected_topic?: Trend;
  tweet_search_results?: TweetSearched[];
  opinion_summary?: string;
  overall_sentiment?: string;
  topic_from_opinion_analysis?: string;
  final_deep_research_report?: string;
  search_query: string[];
  web_research_result: any[];
  sources_gathered: any[];
  initial_search_query_count: number;
  max_research_loops: number;
  research_loop_count: number;
  content_draft?: string;
  image_prompts?: string[];
  final_content?: string;
  final_image_prompts?: string[];
  generated_images?: GeneratedImage[];
  publication_id?: string;
  
  // State management
  messages: any[];
  validation_result?: ValidationResult;
  current_step: string;
  next_human_input_step?: | "await_2fa_code" | "await_topic_selection" | "await_content_validation" | "await_image_validation" | null;
  error_message?: string;
}
