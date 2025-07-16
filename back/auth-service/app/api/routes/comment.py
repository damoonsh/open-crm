from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.comment_service import CommentService
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentReplyCreate, CommentReplyUpdate, CommentReplyResponse
from app.core.security import oauth2_scheme, get_user_id_from_token

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).create_comment(comment, user_id)

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return CommentService(db).get_comment(comment_id)

@router.get("/task/{task_id}", response_model=list[CommentResponse])
async def get_task_comments(task_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).get_task_comments(task_id, user_id)

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).update_comment(comment_id, user_id, comment)

@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).delete_comment(comment_id, user_id)

@router.post("/replies", response_model=CommentReplyResponse)
async def create_comment_reply(reply: CommentReplyCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).create_comment_reply(reply, user_id)

@router.get("/replies/{reply_id}", response_model=CommentReplyResponse)
async def get_comment_reply(reply_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return CommentService(db).get_comment_reply(reply_id)

@router.get("/{comment_id}/replies", response_model=list[CommentReplyResponse])
async def get_comment_replies(comment_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).get_comment_replies(comment_id, user_id)

@router.put("/replies/{reply_id}", response_model=CommentReplyResponse)
async def update_comment_reply(reply_id: int, reply: CommentReplyUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).update_comment_reply(reply_id, user_id, reply)

@router.delete("/replies/{reply_id}")
async def delete_comment_reply(reply_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return CommentService(db).delete_comment_reply(reply_id, user_id)