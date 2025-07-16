from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.task import TaskStatus


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=False, default='#6366f1')  # Hex color code
    position = Column(Integer, nullable=False, default=0)  # For ordering
    is_archived = Column(Boolean, nullable=False, default=False)
    
    # Default workflow settings
    default_status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.open)
    allowed_statuses = Column(JSON, nullable=False, default=lambda: ["open", "in_progress", "review", "closed"])  # JSON array
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="categories")
    tasks = relationship("Task", back_populates="category")

    __table_args__ = (
        # Ensure unique category names within a workspace
        {'schema': None}  # This will be handled by a unique constraint in migration
    )