from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: str = Field(default="#6366f1", regex="^#[0-9A-Fa-f]{6}$", description="Hex color code for category")
    position: int = Field(default=0, ge=0, description="Position for ordering categories")
    default_status: TaskStatus = Field(default=TaskStatus.open, description="Default status for tasks in this category")
    allowed_statuses: List[str] = Field(
        default=["open", "in_progress", "review", "closed"], 
        description="List of allowed task statuses for this category"
    )

    @validator('allowed_statuses')
    def validate_allowed_statuses(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one status must be allowed')
        
        valid_statuses = [status.value for status in TaskStatus]
        for status in v:
            if status not in valid_statuses:
                raise ValueError(f'Invalid status: {status}. Must be one of: {valid_statuses}')
        
        if len(v) != len(set(v)):
            raise ValueError('Duplicate statuses are not allowed')
        
        return v

    @validator('color')
    def validate_color_format(cls, v):
        if not v.startswith('#'):
            raise ValueError('Color must start with #')
        if len(v) != 7:
            raise ValueError('Color must be exactly 7 characters long (including #)')
        return v.upper()


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$", description="Hex color code for category")
    position: Optional[int] = Field(None, ge=0, description="Position for ordering categories")
    is_archived: Optional[bool] = Field(None, description="Whether the category is archived")
    default_status: Optional[TaskStatus] = Field(None, description="Default status for tasks in this category")
    allowed_statuses: Optional[List[str]] = Field(None, description="List of allowed task statuses for this category")

    @validator('allowed_statuses')
    def validate_allowed_statuses(cls, v):
        if v is not None:
            if len(v) == 0:
                raise ValueError('At least one status must be allowed')
            
            valid_statuses = [status.value for status in TaskStatus]
            for status in v:
                if status not in valid_statuses:
                    raise ValueError(f'Invalid status: {status}. Must be one of: {valid_statuses}')
            
            if len(v) != len(set(v)):
                raise ValueError('Duplicate statuses are not allowed')
        
        return v

    @validator('color')
    def validate_color_format(cls, v):
        if v is not None:
            if not v.startswith('#'):
                raise ValueError('Color must start with #')
            if len(v) != 7:
                raise ValueError('Color must be exactly 7 characters long (including #)')
            return v.upper()
        return v


class CategoryResponse(BaseModel):
    id: int = Field(..., description="Unique category identifier")
    workspace_id: int = Field(..., description="ID of the workspace containing this category")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: str = Field(..., description="Hex color code for category")
    position: int = Field(..., description="Position for ordering categories")
    is_archived: bool = Field(..., description="Whether the category is archived")
    default_status: TaskStatus = Field(..., description="Default status for tasks in this category")
    allowed_statuses: List[str] = Field(..., description="List of allowed task statuses for this category")
    created_at: datetime = Field(..., description="Timestamp when category was created")
    updated_at: datetime = Field(..., description="Timestamp when category was last updated")

    class Config:
        from_attributes = True