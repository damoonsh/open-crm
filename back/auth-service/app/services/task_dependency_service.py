from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, and_
from app.models.task import Task, TaskDependency, TaskStatus
from app.models.workspace import workspace_users
from app.schemas.dependency import (
    DependencyCreate, 
    DependencyResponse, 
    DependencyValidationRequest,
    DependencyValidationResponse,
    TaskDependencySummary
)
from typing import List, Set


class TaskDependencyService:
    def __init__(self, db: Session):
        self.db = db

    def add_dependency(self, blocking_task_id: int, dependency_data: DependencyCreate, user_id: int) -> DependencyResponse:
        """Add a dependency between tasks"""
        blocked_task_id = dependency_data.blocked_task_id
        
        # Verify both tasks exist and user has access
        blocking_task = self._get_task_with_access(blocking_task_id, user_id)
        blocked_task = self._get_task_with_access(blocked_task_id, user_id)
        
        # Prevent self-dependency
        if blocking_task_id == blocked_task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot depend on itself"
            )
        
        # Check if dependency already exists
        existing_dependency = self.db.execute(
            select(TaskDependency).where(
                and_(
                    TaskDependency.blocking_task_id == blocking_task_id,
                    TaskDependency.blocked_task_id == blocked_task_id
                )
            )
        ).scalar_one_or_none()
        
        if existing_dependency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dependency already exists"
            )
        
        # Check for circular dependencies
        if self._would_create_circular_dependency(blocking_task_id, blocked_task_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create dependency: would result in circular dependency"
            )
        
        # Create new dependency
        new_dependency = TaskDependency(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=dependency_data.dependency_type,
            created_by_id=user_id
        )
        
        self.db.add(new_dependency)
        self.db.commit()
        self.db.refresh(new_dependency)
        
        return DependencyResponse(
            id=new_dependency.id,
            blocking_task_id=new_dependency.blocking_task_id,
            blocked_task_id=new_dependency.blocked_task_id,
            dependency_type=new_dependency.dependency_type,
            created_at=new_dependency.created_at,
            created_by_id=new_dependency.created_by_id,
            blocking_task_title=blocking_task.title,
            blocked_task_title=blocked_task.title
        )

    def remove_dependency(self, blocking_task_id: int, blocked_task_id: int, user_id: int):
        """Remove a dependency between tasks"""
        # Verify both tasks exist and user has access
        self._get_task_with_access(blocking_task_id, user_id)
        self._get_task_with_access(blocked_task_id, user_id)
        
        # Find and delete the dependency
        dependency = self.db.execute(
            select(TaskDependency).where(
                and_(
                    TaskDependency.blocking_task_id == blocking_task_id,
                    TaskDependency.blocked_task_id == blocked_task_id
                )
            )
        ).scalar_one_or_none()
        
        if not dependency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dependency not found"
            )
        
        self.db.execute(
            delete(TaskDependency).where(TaskDependency.id == dependency.id)
        )
        self.db.commit()
        
        return {"message": "Dependency removed successfully"}

    def get_task_dependencies(self, task_id: int, user_id: int) -> TaskDependencySummary:
        """Get all dependencies for a task"""
        # Verify task exists and user has access
        task = self._get_task_with_access(task_id, user_id)
        
        # Get tasks this task blocks
        blocking_dependencies = self.db.execute(
            select(TaskDependency, Task)
            .join(Task, TaskDependency.blocked_task_id == Task.id)
            .where(TaskDependency.blocking_task_id == task_id)
        ).all()
        
        # Get tasks that block this task
        blocked_by_dependencies = self.db.execute(
            select(TaskDependency, Task)
            .join(Task, TaskDependency.blocking_task_id == Task.id)
            .where(TaskDependency.blocked_task_id == task_id)
        ).all()
        
        blocking_list = [
            DependencyResponse(
                id=dep.id,
                blocking_task_id=dep.blocking_task_id,
                blocked_task_id=dep.blocked_task_id,
                dependency_type=dep.dependency_type,
                created_at=dep.created_at,
                created_by_id=dep.created_by_id,
                blocking_task_title=task.title,
                blocked_task_title=blocked_task.title
            )
            for dep, blocked_task in blocking_dependencies
        ]
        
        blocked_by_list = [
            DependencyResponse(
                id=dep.id,
                blocking_task_id=dep.blocking_task_id,
                blocked_task_id=dep.blocked_task_id,
                dependency_type=dep.dependency_type,
                created_at=dep.created_at,
                created_by_id=dep.created_by_id,
                blocking_task_title=blocking_task.title,
                blocked_task_title=task.title
            )
            for dep, blocking_task in blocked_by_dependencies
        ]
        
        # Check if task can transition based on dependencies
        can_transition, blocking_reasons = self._can_task_transition(task_id)
        
        return TaskDependencySummary(
            task_id=task_id,
            blocking_count=len(blocking_list),
            blocked_by_count=len(blocked_by_list),
            blocking_tasks=blocking_list,
            blocked_by_tasks=blocked_by_list,
            can_transition=can_transition,
            blocking_reasons=blocking_reasons if not can_transition else None
        )

    def validate_dependency(self, validation_request: DependencyValidationRequest, user_id: int) -> DependencyValidationResponse:
        """Validate if a dependency can be created"""
        blocking_task_id = validation_request.blocking_task_id
        blocked_task_id = validation_request.blocked_task_id
        
        try:
            # Verify both tasks exist and user has access
            self._get_task_with_access(blocking_task_id, user_id)
            self._get_task_with_access(blocked_task_id, user_id)
            
            # Check for self-dependency
            if blocking_task_id == blocked_task_id:
                return DependencyValidationResponse(
                    is_valid=False,
                    reason="A task cannot depend on itself"
                )
            
            # Check if dependency already exists
            existing_dependency = self.db.execute(
                select(TaskDependency).where(
                    and_(
                        TaskDependency.blocking_task_id == blocking_task_id,
                        TaskDependency.blocked_task_id == blocked_task_id
                    )
                )
            ).scalar_one_or_none()
            
            if existing_dependency:
                return DependencyValidationResponse(
                    is_valid=False,
                    reason="Dependency already exists"
                )
            
            # Check for circular dependencies
            if self._would_create_circular_dependency(blocking_task_id, blocked_task_id):
                circular_path = self._find_circular_path(blocking_task_id, blocked_task_id)
                return DependencyValidationResponse(
                    is_valid=False,
                    reason="Would create circular dependency",
                    circular_path=circular_path
                )
            
            return DependencyValidationResponse(is_valid=True)
            
        except HTTPException as e:
            return DependencyValidationResponse(
                is_valid=False,
                reason=e.detail
            )

    def _get_task_with_access(self, task_id: int, user_id: int) -> Task:
        """Get task and verify user has access"""
        task = self.db.execute(
            select(Task).where(Task.id == task_id)
        ).scalar_one_or_none()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify user has access to workspace
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                and_(
                    workspace_users.c.workspace_id == task.workspace_id,
                    workspace_users.c.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to task"
            )
        
        return task

    def _would_create_circular_dependency(self, blocking_task_id: int, blocked_task_id: int) -> bool:
        """Check if adding this dependency would create a circular dependency"""
        # Use DFS to check if there's already a path from blocked_task to blocking_task
        visited = set()
        return self._has_path_to_task(blocked_task_id, blocking_task_id, visited)

    def _has_path_to_task(self, start_task_id: int, target_task_id: int, visited: Set[int]) -> bool:
        """Check if there's a dependency path from start_task to target_task using DFS"""
        if start_task_id == target_task_id:
            return True
        
        if start_task_id in visited:
            return False
        
        visited.add(start_task_id)
        
        # Get all tasks that this task blocks
        blocked_tasks = self.db.execute(
            select(TaskDependency.blocked_task_id)
            .where(TaskDependency.blocking_task_id == start_task_id)
        ).scalars().all()
        
        for blocked_task_id in blocked_tasks:
            if self._has_path_to_task(blocked_task_id, target_task_id, visited):
                return True
        
        return False

    def _find_circular_path(self, blocking_task_id: int, blocked_task_id: int) -> List[int]:
        """Find the circular path that would be created"""
        # This is a simplified version - in practice you might want more detailed path tracking
        path = [blocking_task_id, blocked_task_id]
        
        # Try to find path back to blocking_task_id from blocked_task_id
        visited = set()
        if self._build_path_to_task(blocked_task_id, blocking_task_id, visited, path):
            return path
        
        return [blocking_task_id, blocked_task_id, blocking_task_id]  # Simple circular indication

    def _build_path_to_task(self, current_task_id: int, target_task_id: int, visited: Set[int], path: List[int]) -> bool:
        """Build the actual path showing circular dependency"""
        if current_task_id == target_task_id:
            return True
        
        if current_task_id in visited:
            return False
        
        visited.add(current_task_id)
        
        blocked_tasks = self.db.execute(
            select(TaskDependency.blocked_task_id)
            .where(TaskDependency.blocking_task_id == current_task_id)
        ).scalars().all()
        
        for blocked_task_id in blocked_tasks:
            path.append(blocked_task_id)
            if self._build_path_to_task(blocked_task_id, target_task_id, visited, path):
                return True
            path.pop()
        
        return False

    def _can_task_transition(self, task_id: int) -> tuple[bool, List[str]]:
        """Check if task can transition status based on dependencies"""
        # Get tasks that block this task
        blocking_tasks = self.db.execute(
            select(Task)
            .join(TaskDependency, Task.id == TaskDependency.blocking_task_id)
            .where(TaskDependency.blocked_task_id == task_id)
        ).scalars().all()
        
        blocking_reasons = []
        
        for blocking_task in blocking_tasks:
            if blocking_task.status not in [TaskStatus.closed]:
                blocking_reasons.append(f"Task '{blocking_task.title}' (#{blocking_task.id}) must be completed first")
        
        return len(blocking_reasons) == 0, blocking_reasons