from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class PublishedPosts(Base):
    __tablename__ = "published_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # LinkedIn-style post body (<= 250 words)
    topic_title = Column(String(255), nullable=False)
    why_selected = Column(Text, nullable=True)
    why_relevant_now = Column(Text, nullable=True)
    source_urls = Column(Text, nullable=True) # Stored as JSON string list of URLs
    hashtags = Column(Text, nullable=True) # Stored as JSON string list of hashtags
    editorial_score = Column(Float, nullable=False, default=8.5)
    confidence_score = Column(Float, nullable=False, default=0.92)
    published_at = Column(DateTime, default=datetime.utcnow, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)

class RejectedTopics(Base):
    __tablename__ = "rejected_topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_title = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=True)
    rejection_reason = Column(Text, nullable=False)
    quality_score = Column(Float, nullable=False)
    evaluated_at = Column(DateTime, default=datetime.utcnow, index=True)
