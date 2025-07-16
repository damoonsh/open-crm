from pydantic import BaseModel
from typing import Optional

class CommentBase(BaseModel):
    task_id: int
    content: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class CommentResponse(CommentBase):
    id: int
    user_id: int
    created_at: str
    edited_at: str

    class Config:
        orm_mode = True

class CommentReplyBase(BaseModel):
    comment_id: int
    content: str

class CommentReplyCreate(CommentReplyBase):
    pass

class CommentReplyUpdate(BaseModel):
    content: Optional[str] = None

class CommentReplyResponse(CommentReplyBase):
    id: int
    user_id: int
    created_at: str
    edited_at: str

    class Config:
        orm_mode = True