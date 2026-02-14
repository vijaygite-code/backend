from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import date, datetime
import enum
from ..core.database import Base

class TaskType(str, enum.Enum):
    EMAIL = "email"
    NOTIFICATION = "notification"
    CHALLENGE_PROPOSAL = "challenge_proposal"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class MindTask(Base):
    __tablename__ = "mind_tasks"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TaskType), nullable=False)
    content = Column(JSON, nullable=False) # Flexible payload
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Link to user if specific to a user interaction, but mostly system tasks
    
class MotivationQuote(Base):
    __tablename__ = "motivation_quotes"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    for_date = Column(Date, unique=True, index=True)

class UserQuery(Base):
    __tablename__ = "user_queries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True) # AI answer
    escalated_to_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class MonitoringAction(str, enum.Enum):
    WARNING = "warning"
    BAN = "ban"
    FLAG = "flag"

class MonitoringLog(Base):
    __tablename__ = "monitoring_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(Enum(MonitoringAction), nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id])

    # New fields for Reporting
    source = Column(String, default="AI") # "AI" or "USER"
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)

    reporter = relationship("User", foreign_keys=[reporter_id])
    post = relationship("Post")
