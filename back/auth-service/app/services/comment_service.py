from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from app.models.comment import Comment, CommentReply
from app.models.workspace import workspace_users, GroupRoleType
from app.schemas.comment import CommentCreate, CommentUpdate, CommentReplyCreate, CommentReplyUpdate

class CommentService:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment_data: CommentCreate, user_id: int) -> Comment:
        # Verify user has access to workspace and is not a viewer
        task = self.db.execute(select(Task).where(Task.id == comment_data.task_id)).scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if not user_role or user_role == GroupRoleType.viewer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to comment in this workspace"
            )

        # Create new comment
        new_comment = Comment(
            task_id=comment_data.task_id,
            user_id=user_id,
            content=comment_data.content
        )
        self.db.add(new_comment)
        self.db.commit()
        self.db.refresh(new_comment)
        return new_comment

    def get_comment(self, comment_id: int) -> Comment:
        comment = self.db.execute(select(Comment).where(Comment.id == comment_id)).scalar_one_or_none()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        return comment

    def get_task_comments(self, task_id: int, user_id: int) -> list[Comment]:
        task = self.db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Verify user has access to workspace
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this workspace"
            )

        return self.db.execute(
            select(Comment).where(Comment.task_id == task_id)
        ).scalars().all()

    def update_comment(self, comment_id: int, user_id: int, comment_data: CommentUpdate) -> Comment:
        comment = self.get_comment(comment_id)

        # Verify user is comment owner
        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the comment owner can update it"
            )

        update_data = {}
        if comment_data.content:
            update_data["content"] = comment_data.content

        self.db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(**update_data)
        )
        self.db.commit()
        return self.get_comment(comment_id)

    def delete_comment(self, comment_id: int, user_id: int):
        comment = self.get_comment(comment_id)

        # Verify user is comment owner or workspace admin
        task = self.db.execute(select(Task).where(Task.id == comment.task_id)).scalar_one_or_none()
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if comment.user_id != user_id and user_role != GroupRoleType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only comment owner or workspace admin can delete comment"
            )

        self.db.execute(delete(Comment).where(Comment.id == comment_id))
        self.db.commit()
        return {"message": "Comment deleted successfully"}

    def create_comment_reply(self, reply_data: CommentReplyCreate, user_id: int) -> CommentReply:
        # Verify comment exists
        comment = self.get_comment(reply_data.comment_id)
        task = self.db.execute(select(Task).where(Task.id == comment.task_id)).scalar_one_or_none()

        # Verify user has access to workspace and is not a viewer
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if not user_role or user_role == GroupRoleType.viewer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to reply in this workspace"
            )

        # Create new reply
        new_reply = CommentReply(
            comment_id=reply_data.comment_id,
            user_id=user_id,
            content=reply_data.content
        )
        self.db.add(new_reply)
        self.db.commit()
        self.db.refresh(new_reply)
        return new_reply

    def get_comment_reply(self, reply_id: int) -> CommentReply:
        reply = self.db.execute(select(CommentReply).where(CommentReply.id == reply_id)).scalar_one_or_none()
        if not reply:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment reply not found"
            )
        return reply

    def get_comment_replies(self, comment_id: int, user_id: int) -> list[CommentReply]:
        comment = self.get_comment(comment_id)
        task = self.db.execute(select(Task).where(Task.id == comment.task_id)).scalar_one_or_none()

        # Verify user has access to workspace
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this workspace"
            )

        return self.db.execute(
            select(CommentReply).where(CommentReply.comment_id == comment_id)
        ).scalars().all()

    def update_comment_reply(self, reply_id: int, user_id: int, reply_data: CommentReplyUpdate) -> CommentReply:
        reply = self.get_comment_reply(reply_id)

        # Verify user is reply owner
        if reply.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the reply owner can update it"
            )

        update_data = {}
        if reply_data.content:
            update_data["content"] = reply_data.content

        self.db.execute(
            update(CommentReply)
            .where(CommentReply.id == reply_id)
            .values(**update_data)
        )
        self.db.commit()
        return self.get_comment_reply(reply_id)

    def delete_comment_reply(self, reply_id: int, user_id: int):
        reply = self.get_comment_reply(reply_id)
        comment = self.get_comment(reply.comment_id)
        task = self.db.execute(select(Task).where(Task.id == comment.task_id)).scalar_one_or_none()

        # Verify user is reply owner or workspace admin
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if reply.user_id != user_id and user_role != GroupRoleType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reply owner or workspace admin can delete reply"
            )

        self.db.execute(delete(CommentReply).where(CommentReply.id == reply_id))
        self.db.commit()
        return {"message": "Comment reply deleted successfully"}