from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    memory_type = Column(String(50), nullable=False, index=True, default="recent_trend")
    # Memory types: published_post, rejected_topic, discussed_company, recent_trend, repeated_phrase, editorial_opinion
    entity_name = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    phrases = Column(Text, nullable=True) # JSON string array of key phrases
    frequency_count = Column(Integer, default=1)
    post_id = Column(Integer, ForeignKey("published_posts.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
