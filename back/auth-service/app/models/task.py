from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Enum, Text, DateTime, String, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class PriorityType(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    review = "review"
    closed = "closed"
    blocked = "blocked"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id', ondelete='CASCADE'))
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    assignee_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reporter_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    priority = Column(Enum(PriorityType), nullable=False, default=PriorityType.medium)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.open)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    story_points = Column(Integer, nullable=True)
    labels = Column(JSON, nullable=True)  # Store as JSON array of strings
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    blocking_dependencies = relationship("TaskDependency", foreign_keys="TaskDependency.blocking_task_id", back_populates="blocking_task")
    blocked_by_dependencies = relationship("TaskDependency", foreign_keys="TaskDependency.blocked_task_id", back_populates="blocked_task")

class DependencyType(enum.Enum):
    blocks = "blocks"
    depends_on = "depends_on"


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    blocking_task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)  # Task that blocks
    blocked_task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)   # Task that is blocked
    dependency_type = Column(String(20), nullable=False, default='blocks')  # blocks, depends_on
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    blocking_task = relationship("Task", foreign_keys=[blocking_task_id], back_populates="blocking_dependencies")
    blocked_task = relationship("Task", foreign_keys=[blocked_task_id], back_populates="blocked_by_dependencies")
    created_by = relationship("User")
    
    __table_args__ = (
        # Ensure unique dependency pairs
        UniqueConstraint('blocking_task_id', 'blocked_task_id', name='_blocking_blocked_uc'),
        # Prevent self-dependencies
        CheckConstraint('blocking_task_id != blocked_task_id', name='_no_self_dependency'),
    )