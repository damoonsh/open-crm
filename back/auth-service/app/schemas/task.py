from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.task import PriorityType, TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(..., min_length=1, max_length=2000, description="Task description")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID for task organization")
    priority: PriorityType = Field(default=PriorityType.medium, description="Task priority level")
    assignee_id: Optional[int] = Field(None, gt=0, description="User ID of the assigned user")
    story_points: Optional[int] = Field(None, ge=1, le=100, description="Story points for task estimation")
    labels: Optional[List[str]] = Field(None, description="List of labels for task categorization")

    @validator('labels')
    def validate_labels(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 labels allowed')
            for label in v:
                if not isinstance(label, str) or len(label.strip()) == 0:
                    raise ValueError('Labels must be non-empty strings')
                if len(label) > 50:
                    raise ValueError('Label length cannot exceed 50 characters')
        return v

    @validator('title')
    def validate_title(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip() if v else v

    @validator('description')
    def validate_description(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Description cannot be empty or only whitespace')
        return v.strip() if v else v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, min_length=1, max_length=2000, description="Task description")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID for task organization")
    priority: Optional[PriorityType] = Field(None, description="Task priority level")
    assignee_id: Optional[int] = Field(None, gt=0, description="User ID of the assigned user")
    story_points: Optional[int] = Field(None, ge=1, le=100, description="Story points for task estimation")
    labels: Optional[List[str]] = Field(None, description="List of labels for task categorization")

    @validator('labels')
    def validate_labels(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 labels allowed')
            for label in v:
                if not isinstance(label, str) or len(label.strip()) == 0:
                    raise ValueError('Labels must be non-empty strings')
                if len(label) > 50:
                    raise ValueError('Label length cannot exceed 50 characters')
        return v

    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip() if v else v

    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Description cannot be empty or only whitespace')
        return v.strip() if v else v

class TaskStatusUpdate(BaseModel):
    status: TaskStatus = Field(..., description="New status for the task")

class TaskWorkspaceMove(BaseModel):
    workspace_id: int = Field(..., gt=0, description="ID of the target workspace to move the task to")

class TaskResponse(BaseModel):
    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    status: TaskStatus = Field(..., description="Current task status")
    priority: PriorityType = Field(..., description="Task priority level")
    workspace_id: int = Field(..., description="ID of the workspace containing this task")
    category_id: Optional[int] = Field(None, description="ID of the category this task belongs to")
    assignee_id: Optional[int] = Field(None, description="ID of the user assigned to this task")
    reporter_id: Optional[int] = Field(None, description="ID of the user who created this task")
    story_points: Optional[int] = Field(None, description="Story points for task estimation")
    labels: Optional[List[str]] = Field(None, description="List of labels for task categorization")
    created_at: datetime = Field(..., description="Timestamp when task was created")
    updated_at: datetime = Field(..., description="Timestamp when task was last updated")
    blocking_dependencies: List[int] = Field(default=[], description="List of task IDs that this task blocks")
    blocked_by_dependencies: List[int] = Field(default=[], description="List of task IDs that block this task")

    class Config:
        from_attributes = True