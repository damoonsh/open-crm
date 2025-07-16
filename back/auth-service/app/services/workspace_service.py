from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, and_
from app.models.workspace import Workspace, workspace_users, GroupRoleType
from app.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceUserAdd, WorkspaceUserUpdate, WorkspaceUserResponse
from typing import List

class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db

    def create_workspace(self, workspace_data: WorkspaceCreate, user_id: int) -> Workspace:
        # Check if workspace name exists
        workspace = self.db.execute(select(Workspace).where(Workspace.name == workspace_data.name)).scalar_one_or_none()
        if workspace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace name already taken"
            )

        # Create new workspace
        new_workspace = Workspace(
            name=workspace_data.name,
            description=workspace_data.description
        )
        self.db.add(new_workspace)
        self.db.flush()

        # Add creator as admin
        self.db.execute(workspace_users.insert().values(
            workspace_id=new_workspace.id,
            user_id=user_id,
            role=GroupRoleType.admin
        ))
        self.db.commit()
        self.db.refresh(new_workspace)
        return new_workspace

    def get_workspace(self, workspace_id: int) -> Workspace:
        workspace = self.db.execute(select(Workspace).where(Workspace.id == workspace_id)).scalar_one_or_none()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        return workspace

    def get_user_workspaces(self, user_id: int) -> list[Workspace]:
        return self.db.execute(
            select(Workspace)
            .join(workspace_users)
            .where(workspace_users.c.user_id == user_id)
        ).scalars().all()

    def update_workspace(self, workspace_id: int, user_id: int, workspace_data: WorkspaceUpdate) -> Workspace:
        workspace = self.get_workspace(workspace_id)

        # Check if user is admin
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if user_role != GroupRoleType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update workspace"
            )

        update_data = {}
        if workspace_data.name:
            # Check if new name is already taken
            existing_workspace = self.db.execute(
                select(Workspace).where(Workspace.name == workspace_data.name)
            ).scalar_one_or_none()
            if existing_workspace and existing_workspace.id != workspace_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workspace name already taken"
                )
            update_data["name"] = workspace_data.name
        if workspace_data.description is not None:
            update_data["description"] = workspace_data.description

        self.db.execute(
            update(Workspace)
            .where(Workspace.id == workspace_id)
            .values(**update_data)
        )
        self.db.commit()
        return self.get_workspace(workspace_id)

    def delete_workspace(self, workspace_id: int, user_id: int):
        workspace = self.get_workspace(workspace_id)

        # Check if user is admin
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if user_role != GroupRoleType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete workspace"
            )

        self.db.execute(delete(Workspace).where(Workspace.id == workspace_id))
        self.db.commit()
        return {"message": "Workspace deleted successfully"}

    def _check_workspace_admin_permission(self, workspace_id: int, user_id: int):
        """Helper method to check if user has admin permissions for workspace"""
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        
        if user_role != GroupRoleType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace admins can perform this action"
            )

    def get_workspace_users(self, workspace_id: int, requesting_user_id: int) -> List[WorkspaceUserResponse]:
        """Get all users in a workspace with their roles"""
        # Verify workspace exists and user has access
        self.get_workspace(workspace_id)
        
        # Check if requesting user is member of workspace
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == requesting_user_id
            )
        ).scalar_one_or_none()
        
        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )

        # Get all workspace users with their details
        result = self.db.execute(
            select(
                User.id,
                User.username,
                User.email,
                workspace_users.c.role,
                workspace_users.c.created_at
            )
            .join(workspace_users, User.id == workspace_users.c.user_id)
            .where(workspace_users.c.workspace_id == workspace_id)
        ).all()

        return [
            WorkspaceUserResponse(
                user_id=row.id,
                username=row.username,
                email=row.email,
                role=row.role,
                created_at=row.created_at
            )
            for row in result
        ]

    def add_user_to_workspace(self, workspace_id: int, user_data: WorkspaceUserAdd, requesting_user_id: int) -> WorkspaceUserResponse:
        """Add a user to a workspace with specified role"""
        # Verify workspace exists and requesting user is admin
        self.get_workspace(workspace_id)
        self._check_workspace_admin_permission(workspace_id, requesting_user_id)

        # Check if target user exists
        target_user = self.db.execute(
            select(User).where(User.id == user_data.user_id)
        ).scalar_one_or_none()
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if user is already in workspace
        existing_membership = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_data.user_id
            )
        ).scalar_one_or_none()

        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this workspace"
            )

        # Add user to workspace
        self.db.execute(
            workspace_users.insert().values(
                workspace_id=workspace_id,
                user_id=user_data.user_id,
                role=user_data.role
            )
        )
        self.db.commit()

        # Return the new workspace user
        result = self.db.execute(
            select(
                User.id,
                User.username,
                User.email,
                workspace_users.c.role,
                workspace_users.c.created_at
            )
            .join(workspace_users, User.id == workspace_users.c.user_id)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_data.user_id
            )
        ).first()

        return WorkspaceUserResponse(
            user_id=result.id,
            username=result.username,
            email=result.email,
            role=result.role,
            created_at=result.created_at
        )

    def update_workspace_user_role(self, workspace_id: int, user_id: int, user_update: WorkspaceUserUpdate, requesting_user_id: int) -> WorkspaceUserResponse:
        """Update a user's role in a workspace"""
        # Verify workspace exists and requesting user is admin
        self.get_workspace(workspace_id)
        self._check_workspace_admin_permission(workspace_id, requesting_user_id)

        # Check if target user is in workspace
        existing_membership = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()

        if not existing_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this workspace"
            )

        # Prevent admin from demoting themselves if they're the only admin
        if requesting_user_id == user_id and user_update.role != GroupRoleType.admin:
            admin_count = self.db.execute(
                select(workspace_users.c.user_id)
                .where(
                    workspace_users.c.workspace_id == workspace_id,
                    workspace_users.c.role == GroupRoleType.admin
                )
            ).rowcount

            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove admin role - workspace must have at least one admin"
                )

        # Update user role
        self.db.execute(
            update(workspace_users)
            .where(
                and_(
                    workspace_users.c.workspace_id == workspace_id,
                    workspace_users.c.user_id == user_id
                )
            )
            .values(role=user_update.role)
        )
        self.db.commit()

        # Return updated user info
        result = self.db.execute(
            select(
                User.id,
                User.username,
                User.email,
                workspace_users.c.role,
                workspace_users.c.created_at
            )
            .join(workspace_users, User.id == workspace_users.c.user_id)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).first()

        return WorkspaceUserResponse(
            user_id=result.id,
            username=result.username,
            email=result.email,
            role=result.role,
            created_at=result.created_at
        )

    def remove_user_from_workspace(self, workspace_id: int, user_id: int, requesting_user_id: int):
        """Remove a user from a workspace"""
        # Verify workspace exists and requesting user is admin
        self.get_workspace(workspace_id)
        self._check_workspace_admin_permission(workspace_id, requesting_user_id)

        # Check if target user is in workspace
        existing_membership = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()

        if not existing_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this workspace"
            )

        # Prevent removing the last admin
        if existing_membership == GroupRoleType.admin:
            admin_count = self.db.execute(
                select(workspace_users.c.user_id)
                .where(
                    workspace_users.c.workspace_id == workspace_id,
                    workspace_users.c.role == GroupRoleType.admin
                )
            ).rowcount

            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last admin from workspace"
                )

        # Remove user from workspace
        self.db.execute(
            delete(workspace_users)
            .where(
                and_(
                    workspace_users.c.workspace_id == workspace_id,
                    workspace_users.c.user_id == user_id
                )
            )
        )
        self.db.commit()

        return {"message": "User removed from workspace successfully"}