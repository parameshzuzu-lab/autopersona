from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base

class SchedulerStatus(Base):
    __tablename__ = "scheduler_status"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(String(50), nullable=False, default="running")  # running, paused, executing, error
    interval_minutes = Column(Integer, nullable=False, default=15)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    total_runs = Column(Integer, default=0)
    total_published = Column(Integer, default=0)
    total_rejected = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(String(20), nullable=False, default="INFO") # INFO, WARN, ERROR, SUCCESS
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
