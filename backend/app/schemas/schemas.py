from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Persona Schemas ---
class PersonaInitRequest(BaseModel):
    name: Optional[str] = Field(default="AutoPersona AI", max_length=255)
    editorial_voice: Optional[str] = Field(
        default="Authoritative, vision-driven AI researcher and tech strategist.",
        description="The persona tone and editorial voice style"
    )
    target_audience: Optional[str] = Field(
        default="AI Engineers, Software Architects, Tech Executives, & Founders"
    )
    core_topics: Optional[str] = Field(
        default="LLMs, Agentic AI, Autonomous Systems, Compute Infrastructure, AI Ethics"
    )
    min_quality_score: Optional[float] = Field(default=7.0, ge=1.0, le=10.0)

class PersonaResponse(BaseModel):
    id: int
    name: str
    editorial_voice: str
    target_audience: str
    core_topics: str
    min_quality_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- PublishedPosts Schemas ---
class PublishedPostResponse(BaseModel):
    id: int
    title: str
    content: str  # Body (<= 250 words)
    topic_title: str
    why_selected: Optional[str] = None
    why_relevant_now: Optional[str] = None
    source_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    editorial_score: float
    confidence_score: float
    published_at: datetime
    persona_id: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True

# --- RejectedTopics Schemas ---
class RejectedTopicResponse(BaseModel):
    id: int
    topic_title: str
    source_url: Optional[str]
    rejection_reason: str
    quality_score: float
    evaluated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- Memory Schemas ---
class MemoryResponse(BaseModel):
    id: int
    memory_type: str
    entity_name: str
    content: str
    phrases: Optional[List[str]] = None
    frequency_count: int
    post_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class MemoryOverviewResponse(BaseModel):
    past_posts_count: int
    discussed_companies: List[Dict[str, Any]]
    recent_trends: List[Dict[str, Any]]
    repeated_phrases: List[str]
    editorial_opinions: List[str]
    topic_frequency: List[Dict[str, Any]]
    memories: List[MemoryResponse]

# --- SchedulerStatus Schemas ---
class SchedulerStatusResponse(BaseModel):
    id: int
    status: str
    interval_minutes: int
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    total_runs: int
    total_published: int
    total_rejected: int
    last_error: Optional[str]
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- ExecutionLog Schemas ---
class LogResponse(BaseModel):
    id: int
    level: str
    message: str
    details: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- Topic / Discovery Schemas ---
class DiscoveredTopicItem(BaseModel):
    title: str
    source_url: Optional[str]
    summary: str
    category: str
    published_at: Optional[datetime] = None

class TopicEvaluationResult(BaseModel):
    topic: DiscoveredTopicItem
    quality_score: float
    is_approved: bool
    reason: str

class TopicsOverviewResponse(BaseModel):
    recent_evaluations: List[TopicEvaluationResult]
    rejected_topics: List[RejectedTopicResponse]

# --- Generic Response Schemas ---
class GenericResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None

# --- Chat Schemas ---
class ChatMessageItem(BaseModel):
    role: str = Field(description="'user' or 'assistant'")
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's question to the AI persona")
    history: Optional[List[ChatMessageItem]] = Field(
        default=None,
        description="Optional recent conversation history to provide conversational context"
    )

class ChatResponse(BaseModel):
    reply: str
    sources: Optional[List[str]] = Field(default=None, description="Grounded source URLs from memory/feed used to inform the answer")
    mode: str = Field(..., description="'azure', 'gemini', 'openai', 'local', or 'error'")
    error: Optional[str] = Field(default=None, description="Human-friendly error message when the model call failed")
