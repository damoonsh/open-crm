from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class DependencyCreate(BaseModel):
    blocked_task_id: int = Field(..., gt=0, description="ID of the task that will be blocked")
    dependency_type: str = Field(default="blocks", description="Type of dependency relationship")

    @validator('dependency_type')
    def validate_dependency_type(cls, v):
        valid_types = ['blocks', 'depends_on']
        if v not in valid_types:
            raise ValueError(f'Invalid dependency type: {v}. Must be one of: {valid_types}')
        return v

    @validator('blocked_task_id')
    def validate_blocked_task_id(cls, v):
        if v <= 0:
            raise ValueError('blocked_task_id must be a positive integer')
        return v


class DependencyResponse(BaseModel):
    id: int = Field(..., description="Unique dependency identifier")
    blocking_task_id: int = Field(..., description="ID of the task that blocks")
    blocked_task_id: int = Field(..., description="ID of the task that is blocked")
    dependency_type: str = Field(..., description="Type of dependency relationship")
    created_at: datetime = Field(..., description="Timestamp when dependency was created")
    created_by_id: int = Field(..., description="ID of the user who created this dependency")
    
    # Optional nested task information for convenience
    blocking_task_title: Optional[str] = Field(None, description="Title of the blocking task")
    blocked_task_title: Optional[str] = Field(None, description="Title of the blocked task")

    class Config:
        from_attributes = True


class DependencyValidationRequest(BaseModel):
    """Schema for validating if a dependency can be created without causing circular references"""
    blocking_task_id: int = Field(..., gt=0, description="ID of the task that would block")
    blocked_task_id: int = Field(..., gt=0, description="ID of the task that would be blocked")

    @validator('blocked_task_id')
    def validate_different_tasks(cls, v, values):
        if 'blocking_task_id' in values and v == values['blocking_task_id']:
            raise ValueError('A task cannot depend on itself')
        return v


class DependencyValidationResponse(BaseModel):
    """Response schema for dependency validation"""
    is_valid: bool = Field(..., description="Whether the dependency can be created")
    reason: Optional[str] = Field(None, description="Reason why dependency is invalid (if applicable)")
    circular_path: Optional[list] = Field(None, description="Path showing circular dependency (if detected)")


class TaskDependencySummary(BaseModel):
    """Summary of all dependencies for a task"""
    task_id: int = Field(..., description="ID of the task")
    blocking_count: int = Field(..., description="Number of tasks this task blocks")
    blocked_by_count: int = Field(..., description="Number of tasks blocking this task")
    blocking_tasks: list[DependencyResponse] = Field(default=[], description="List of tasks this task blocks")
    blocked_by_tasks: list[DependencyResponse] = Field(default=[], description="List of tasks blocking this task")
    can_transition: bool = Field(..., description="Whether task can transition status based on dependencies")
    blocking_reasons: Optional[list[str]] = Field(None, description="Reasons why task cannot transition (if applicable)")