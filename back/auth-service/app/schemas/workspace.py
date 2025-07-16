from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.workspace import GroupRoleType

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(WorkspaceBase):
    name: Optional[str] = None

class WorkspaceUserAdd(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user to add to workspace")
    role: GroupRoleType = Field(default=GroupRoleType.member, description="Role to assign to the user")

class WorkspaceUserUpdate(BaseModel):
    role: GroupRoleType = Field(..., description="New role for the user")

class WorkspaceUserResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    role: GroupRoleType = Field(..., description="User role in workspace")
    created_at: datetime = Field(..., description="When user was added to workspace")

    class Config:
        from_attributes = True

class WorkspaceResponse(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    users: Optional[List[WorkspaceUserResponse]] = Field(None, description="List of workspace users")

    class Config:
        from_attributes = True