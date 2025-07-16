from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.task_dependency_service import TaskDependencyService
from app.schemas.dependency import (
    DependencyCreate, 
    DependencyResponse, 
    DependencyValidationRequest,
    DependencyValidationResponse,
    TaskDependencySummary
)
from app.core.security import oauth2_scheme, get_user_id_from_token

router = APIRouter(prefix="/tasks", tags=["task-dependencies"])

@router.get("/{task_id}/dependencies", response_model=TaskDependencySummary)
async def get_task_dependencies(
    task_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get all dependencies for a task"""
    user_id = get_user_id_from_token(token)
    return TaskDependencyService(db).get_task_dependencies(task_id, user_id)

@router.post("/{task_id}/dependencies", response_model=DependencyResponse)
async def add_task_dependency(
    task_id: int,
    dependency: DependencyCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Add a dependency to a task"""
    user_id = get_user_id_from_token(token)
    return TaskDependencyService(db).add_dependency(task_id, dependency, user_id)

@router.delete("/{task_id}/dependencies/{blocking_task_id}")
async def remove_task_dependency(
    task_id: int,
    blocking_task_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Remove a dependency from a task"""
    user_id = get_user_id_from_token(token)
    return TaskDependencyService(db).remove_dependency(task_id, blocking_task_id, user_id)

@router.post("/dependencies/validate", response_model=DependencyValidationResponse)
async def validate_dependency(
    validation_request: DependencyValidationRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Validate if a dependency can be created without causing circular references"""
    user_id = get_user_id_from_token(token)
    return TaskDependencyService(db).validate_dependency(validation_request, user_id)