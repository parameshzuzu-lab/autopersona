export interface PublishedPost {
  id: number;
  title: string;
  content: string;
  topic_title: string;
  why_selected?: string;
  why_relevant_now?: string;
  source_urls?: string[];
  hashtags?: string[];
  editorial_score: number;
  confidence_score: number;
  published_at: string;
  persona_id?: number;
}

export interface RejectedTopic {
  id: number;
  topic_title: string;
  source_url?: string;
  rejection_reason: string;
  quality_score: number;
  evaluated_at: string;
}

export interface MemoryItem {
  id: number;
  memory_type: string;
  entity_name: string;
  content: string;
  phrases?: string[];
  frequency_count: number;
  post_id?: number;
  created_at: string;
}

export interface MemoryOverview {
  past_posts_count: number;
  discussed_companies: { company: string; mentions: number }[];
  recent_trends: { trend: string; frequency: number }[];
  repeated_phrases: string[];
  editorial_opinions: string[];
  topic_frequency: { category: string; count: number }[];
  memories: MemoryItem[];
}

export interface Persona {
  id: number;
  name: string;
  editorial_voice: string;
  target_audience: string;
  core_topics: string;
  min_quality_score: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SchedulerStatus {
  id: number;
  status: string;
  interval_minutes: number;
  last_run_at?: string;
  next_run_at?: string;
  total_runs: number;
  total_published: number;
  total_rejected: number;
  last_error?: string;
  updated_at: string;
}

export interface LogEntry {
  id: number;
  level: string;
  message: string;
  details?: string;
  created_at: string;
}

export interface DiscoveredTopic {
  title: string;
  source_url?: string;
  summary: string;
  category: string;
  published_at?: string;
}

export interface TopicEvaluation {
  topic: DiscoveredTopic;
  quality_score: number;
  is_approved: boolean;
  reason: string;
}

export interface TopicsOverview {
  recent_evaluations: TopicEvaluation[];
  rejected_topics: RejectedTopic[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  reply: string;
  sources?: string[];
  mode: 'azure' | 'gemini' | 'openai' | 'local' | 'local_error' | 'local_offline' | 'error';
  error?: string;
}
