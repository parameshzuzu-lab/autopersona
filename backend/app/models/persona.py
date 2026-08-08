from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from datetime import datetime
from app.core.database import Base

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, default="AutoPersona AI")
    editorial_voice = Column(Text, nullable=False, default="Authoritative, vision-driven AI researcher and tech strategist.")
    target_audience = Column(Text, nullable=False, default="AI Engineers, Software Architects, Tech Executives, & Founders")
    core_topics = Column(Text, nullable=False, default="LLMs, Agentic AI, Autonomous Systems, Compute Infrastructure, AI Ethics")
    min_quality_score = Column(Float, nullable=False, default=7.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
