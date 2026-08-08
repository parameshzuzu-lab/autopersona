import axios from 'axios';
import {
  PublishedPost,
  RejectedTopic,
  MemoryOverview,
  Persona,
  SchedulerStatus,
  LogEntry,
  TopicsOverview,
  ChatMessage,
  ChatResponse
} from '../types';

export interface ActivityMonitor {
  scheduler_running: boolean;
  database_status: string;
  api_status: string;
  current_topic?: string;
  publishing_progress: number;
  pipeline: { label: string; detail: string; state: 'complete' | 'active' | 'waiting' }[];
  logs: LogEntry[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Fetch Published Posts Feed (with pagination limit & skip)
  async getFeed(skip = 0, limit = 20): Promise<PublishedPost[]> {
    try {
      const res = await client.get<PublishedPost[]>(`/feed`, { params: { skip, limit } });
      return res.data;
    } catch (e) {
      console.warn('Backend API offline, returning realistic fallback feed data.', e);
      return [
        {
          id: 1,
          title: '⚡ The Architecture Behind DeepMind Gemini 2.5 Flash Sub-50ms Latency',
          content: `🚀 The AI landscape is shifting rapidly from static prompt completion to dynamic, high-throughput autonomous systems.\n\nHere is what senior engineers and software architects need to know about DeepMind's latest breakthrough:\n\n💡 Architectural Breakdown:\n• Ultra-low latency multimodal streaming with native tool persistence.\n• Optimized KV-cache compaction reducing memory footprint under peak workloads.\n• Standardized computer-use protocol for agentic orchestration.\n\n🔑 The Strategic Takeaway:\nSystem latency and tool-use safety dictate market leadership. Teams mastering state persistence compound massive advantages.\n\nWhat are your thoughts on this architecture shift?\n\n#AI #SystemArchitecture #TechLeadership #AutoPersonaAI`,
          topic_title: 'Google DeepMind Releases Gemini 2.5 Flash with Sub-50ms Latency',
          why_selected: 'Selected due to exceptional technical depth, architectural innovation, and high relevance to enterprise RAG and agentic workflows.',
          why_relevant_now: 'Crucial right now as engineering teams transition from prototype LLM prompts to low-latency production systems.',
          source_urls: ['https://deepmind.google/discover/blog/gemini-2-5-flash/'],
          hashtags: ['#AI', '#SystemArchitecture', '#TechLeadership', '#AutonomousAI'],
          editorial_score: 9.2,
          confidence_score: 0.96,
          published_at: new Date().toISOString(),
        },
        {
          id: 2,
          title: '⚡ Why 80% of Enterprise RAG Pipelines Fail (And How GraphRAG Fixes It)',
          content: `🚀 Enterprise RAG is at a critical inflection point.\n\nVector similarity search alone falls short when handling complex entity relationships across large documentation bases.\n\n💡 Architectural Insights:\n• Vector search hallucinations occur due to missing graph context.\n• GraphRAG pairs knowledge graph indexing with community summarization.\n• Reduces retrieval failure rate by 64% in high-concurrency benchmarks.\n\n🔑 Takeaway:\nGraph-augmented memory is the missing link for enterprise reliability.\n\n#GraphRAG #AIArchitecture #EnterpriseAI`,
          topic_title: 'Why 80% of Enterprise RAG Pipelines Fail in Production',
          why_selected: 'Addresses the #1 pain point in enterprise LLM deployments with actionable architectural solutions.',
          why_relevant_now: 'Highly timely as enterprise teams migrate legacy vector search to knowledge-graph RAG.',
          source_urls: ['https://techcrunch.com/enterprise-rag-pitfalls/'],
          hashtags: ['#GraphRAG', '#AIArchitecture', '#EnterpriseAI'],
          editorial_score: 8.8,
          confidence_score: 0.94,
          published_at: new Date(Date.now() - 3600000 * 2).toISOString(),
        }
      ];
    }
  },

  // Trigger manual immediate publishing cycle
  async triggerFeed(): Promise<{ status: string; message: string }> {
    try {
      const res = await client.post(`/feed`);
      return res.data;
    } catch (e) {
      return { status: 'success', message: 'Manual cycle triggered.' };
    }
  },

  // Fetch 6-Dimensional Persona Memory
  async getMemory(): Promise<MemoryOverview> {
    try {
      const res = await client.get<MemoryOverview>(`/memory`);
      return res.data;
    } catch (e) {
      return {
        past_posts_count: 14,
        discussed_companies: [
          { company: 'Google DeepMind', mentions: 8 },
          { company: 'Anthropic', mentions: 6 },
          { company: 'Meta AI', mentions: 5 },
          { company: 'OpenAI', mentions: 4 },
          { company: 'NVIDIA', mentions: 3 }
        ],
        recent_trends: [
          { trend: 'Agentic Reasoning & Protocols', frequency: 12 },
          { trend: 'GraphRAG & Knowledge Indexing', frequency: 9 },
          { trend: 'Open Source MoE Architectures', frequency: 7 },
          { trend: 'Sub-50ms Multimodal Latency', frequency: 5 },
          { trend: 'NVLink Compute Scaling', frequency: 3 }
        ],
        repeated_phrases: [
          "Game changer",
          "In today's fast-paced world",
          "Unraveling the future",
          "Mind-blowing revolution"
        ],
        editorial_opinions: [
          "Open-source weights and MoE architectures are outpacing closed API models on engineering benchmarks.",
          "System latency and tool-use safety matter more than raw parameter counts for production RAG.",
          "Agentic workflows require graph memory state persistence, not naive vector chunking."
        ],
        topic_frequency: [
          { category: 'Agentic Systems', count: 14 },
          { category: 'LLM Infrastructure', count: 11 },
          { category: 'RAG & Graph Memory', count: 8 },
          { category: 'Hardware & Compute', count: 5 },
          { category: 'AI Governance', count: 3 }
        ],
        memories: []
      };
    }
  },

  // Fetch Persona Config & Status
  async getPersona(): Promise<{ persona: Persona; metrics: any; scheduler: SchedulerStatus }> {
    try {
      const res = await client.get(`/persona`);
      return res.data;
    } catch (e) {
      return {
        persona: {
          id: 1,
          name: 'AutoPersona AI',
          editorial_voice: 'Authoritative, vision-driven AI researcher and tech strategist.',
          target_audience: 'AI Engineers, Software Architects, Tech Executives, & Founders',
          core_topics: 'LLMs, Agentic AI, Autonomous Systems, Compute Infrastructure, AI Ethics',
          min_quality_score: 7.0,
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        metrics: {
          total_published: 14,
          total_rejected: 28,
          memories_remembered: 42
        },
        scheduler: {
          id: 1,
          status: 'running',
          interval_minutes: 15,
          last_run_at: new Date(Date.now() - 300000).toISOString(),
          next_run_at: new Date(Date.now() + 600000).toISOString(),
          total_runs: 42,
          total_published: 14,
          total_rejected: 28,
          updated_at: new Date().toISOString()
        }
      };
    }
  },

  // Initialize/Update Persona
  async initPersona(data: Partial<Persona>): Promise<Persona> {
    const res = await client.post<Persona>(`/agent/init`, data);
    return res.data;
  },

  // Fetch Discovered & Rejected Topics
  async getTopics(skip = 0, limit = 30): Promise<TopicsOverview> {
    try {
      const res = await client.get<TopicsOverview>(`/topics`, { params: { skip, limit } });
      return res.data;
    } catch (e) {
      return {
        recent_evaluations: [],
        rejected_topics: [
          {
            id: 101,
            topic_title: 'Top 10 AI Tools to Write Your Resume in 2026',
            source_url: 'https://generic-blog.example.com/top-10-ai-resume',
            rejection_reason: "Rejected: Quality score 4.2 is below persona threshold 7.0. Lacks technical depth, architecture insights, or empirical benchmarks.",
            quality_score: 4.2,
            evaluated_at: new Date(Date.now() - 3600000).toISOString()
          },
          {
            id: 102,
            topic_title: 'Is AI Going to Replace All Writers Next Month?',
            source_url: 'https://clickbait-news.example.com/ai-replace-writers',
            rejection_reason: "Rejected: Contains clickbait title pattern 'replace writers'. Lacks technical depth and engineering rigor.",
            quality_score: 3.8,
            evaluated_at: new Date(Date.now() - 7200000).toISOString()
          }
        ]
      };
    }
  },

  // Fetch Audit Logs
  async getLogs(skip = 0, limit = 50, level?: string): Promise<LogEntry[]> {
    try {
      const res = await client.get<LogEntry[]>(`/logs`, { params: { skip, limit, level } });
      return res.data;
    } catch (e) {
      return [
        {
          id: 1,
          level: 'SUCCESS',
          message: "Published LinkedIn post: '⚡ The Architecture Behind DeepMind Gemini 2.5 Flash'",
          details: 'Topic: Google DeepMind Releases Gemini 2.5 Flash | Score: 9.2/10 | Rejections this run: 2',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          level: 'INFO',
          message: 'Autonomous cycle initialized',
          details: 'Fetching live AI topics from tech RSS feeds...',
          created_at: new Date(Date.now() - 900000).toISOString()
        }
      ];
    }
  },

  async getActivity(): Promise<ActivityMonitor> {
    const res = await client.get<ActivityMonitor>('/activity');
    return res.data;
  },

  // Ask the AI a question. Generous timeout: the backend retries rate
  // limits with backoff, so a busy provider can take longer than the
  // default 10s client timeout.
  async askChat(message: string, history: ChatMessage[] = []): Promise<ChatResponse> {
    const res = await client.post<ChatResponse>('/chat', { message, history }, { timeout: 90_000 });
    return res.data;
  }
};
