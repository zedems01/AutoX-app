// --- API Payloads ---

export interface StartLoginPayload {
  email: string;
  password: string;
  proxy: string;
}

export interface CompleteLoginPayload {
  thread_id: string;
  two_fa_code: string;
}

export interface StartWorkflowPayload {
  thread_id: string;
  is_autonomous_mode: boolean;
  output_destination: "GET_OUTPUTS" | "PUBLISH_X";
  has_user_provided_topic: boolean;
  user_provided_topic?: string;
  x_content_type?: "TWEET_THREAD" | "SINGLE_TWEET";
  content_length?: "SHORT" | "MEDIUM" | "LONG";
  brand_voice?: string;
  target_audience?: string;
  user_config?: UserConfigSchema;
}

export interface ValidationPayload {
  thread_id: string;
  validation_result: ValidationResult;
}

// --- API Responses ---

export interface StartLoginResponse {
  thread_id: string;
  login_data: any; // Opaque data object
}

export interface CompleteLoginResponse {
  status: string;
  user_details: any; // User details object
}

// --- Core State & Supporting Types ---

export interface UserConfigSchema {
    gemini_base_model?: string;
    gemini_reasoning_model?: string;
    openai_model?: string;
    trends_count?: string;
    trends_woeid?: string;
    max_tweets_to_retrieve?: string;
    tweets_language?: string;
    content_language?: string;
}

export interface ValidationResult {
  action: "approve" | "reject" | "edit";
  data?: {
    feedback?: string;
    extra_data?: {
      final_content?: string;
    };
  };
}

export interface Trend {
  name: string;
  tweet_count: number;
}

export interface OverallState {
  // From login
  login_data?: any;
  proxy?: string;
  session?: any;
  user_details?: any;

  // From workflow start
  is_autonomous_mode: boolean;
  output_destination?: "GET_OUTPUTS" | "PUBLISH_X";
  has_user_provided_topic: boolean;
  user_provided_topic?: string;
  x_content_type?: "TWEET_THREAD" | "SINGLE_TWEET";
  content_length?: "SHORT" | "MEDIUM" | "LONG";
  brand_voice?: string;
  target_audience?: string;
  user_config?: UserConfigSchema;

  // From graph execution
  trending_topics?: Trend[];
  selected_topic?: Trend;
  tweet_search_results?: any[];
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
  generated_images?: string[]; // Assuming URLs or base64 strings
  publication_id?: string;
  
  // State management
  messages: any[];
  validation_result?: ValidationResult;
  current_step: string;
  next_human_input_step?: | "await_2fa_code" | "await_topic_selection" | "await_content_validation" | "await_image_validation" | null;
  error_message?: string;
}
