from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import (
    WorkspaceCreate, 
    WorkspaceUpdate, 
    WorkspaceResponse, 
    WorkspaceUserAdd, 
    WorkspaceUserUpdate, 
    WorkspaceUserResponse
)
from app.core.security import oauth2_scheme, get_user_id_from_token

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return WorkspaceService(db).create_workspace(workspace, user_id)

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return WorkspaceService(db).get_workspace(workspace_id)

@router.get("/", response_model=list[WorkspaceResponse])
async def get_user_workspaces(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return WorkspaceService(db).get_user_workspaces(user_id)

@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(workspace_id: int, workspace: WorkspaceUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return WorkspaceService(db).update_workspace(workspace_id, user_id, workspace)

@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return WorkspaceService(db).delete_workspace(workspace_id, user_id)

# Workspace User Management Routes

@router.get("/{workspace_id}/users", response_model=List[WorkspaceUserResponse])
async def get_workspace_users(
    workspace_id: int, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """Get all users in a workspace with their roles"""
    user_id = get_user_id_from_token(token)
    return WorkspaceService(db).get_workspace_users(workspace_id, user_id)

@router.post("/{workspace_id}/users", response_model=WorkspaceUserResponse)
async def add_user_to_workspace(
    workspace_id: int,
    user_data: WorkspaceUserAdd,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Add a user to a workspace with specified role"""
    requesting_user_id = get_user_id_from_token(token)
    return WorkspaceService(db).add_user_to_workspace(workspace_id, user_data, requesting_user_id)

@router.put("/{workspace_id}/users/{user_id}", response_model=WorkspaceUserResponse)
async def update_workspace_user_role(
    workspace_id: int,
    user_id: int,
    user_update: WorkspaceUserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Update a user's role in a workspace"""
    requesting_user_id = get_user_id_from_token(token)
    return WorkspaceService(db).update_workspace_user_role(workspace_id, user_id, user_update, requesting_user_id)

@router.delete("/{workspace_id}/users/{user_id}")
async def remove_user_from_workspace(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Remove a user from a workspace"""
    requesting_user_id = get_user_id_from_token(token)
    return WorkspaceService(db).remove_user_from_workspace(workspace_id, user_id, requesting_user_id)