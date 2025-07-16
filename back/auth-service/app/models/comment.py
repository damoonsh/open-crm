from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    edited_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    user = relationship("User")
    replies = relationship("CommentReply", back_populates="comment", cascade="all, delete-orphan")

class CommentReply(Base):
    __tablename__ = "comment_replies"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    edited_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    comment = relationship("Comment", back_populates="replies")
    user = relationship("User")