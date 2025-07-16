from datetime import datetime
from sqlalchemy import UniqueConstraint, Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class GroupRoleType(enum.Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"

# Association table for workspace users
workspace_users = Table(
    'workspace_users',
    Base.metadata,
    Column('workspace_id', Integer, ForeignKey('workspaces.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role', Enum(GroupRoleType), nullable=False, default=GroupRoleType.member),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow),
    UniqueConstraint('workspace_id', 'user_id', name='_workspace_user_uc')
)

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", secondary=workspace_users, back_populates="workspaces")
    tasks = relationship("Task", back_populates="workspace", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="workspace", cascade="all, delete-orphan")
