from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, and_
from app.models.task import Task, PriorityType, TaskStatus, TaskDependency
from app.models.category import Category
from app.models.workspace import workspace_users, GroupRoleType, Workspace
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskWorkspaceMove

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: TaskCreate, user_id: int) -> Task:
        # Verify user has access to workspace and is not a viewer
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task_data.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if not user_role or user_role == GroupRoleType.viewer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to create tasks in this workspace"
            )

        # Create new task
        new_task = Task(
            workspace_id=task_data.workspace_id,
            priority=task_data.priority,
            description=task_data.description
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def get_task(self, task_id: int) -> Task:
        task = self.db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task

    def get_workspace_tasks(self, workspace_id: int, user_id: int) -> list[Task]:
        # Verify user has access to workspace
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this workspace"
            )

        return self.db.execute(
            select(Task).where(Task.workspace_id == workspace_id)
        ).scalars().all()

    def update_task(self, task_id: int, user_id: int, task_data: TaskUpdate) -> Task:
        task = self.get_task(task_id)

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
                detail="User does not have permission to update tasks in this workspace"
            )

        update_data = {}
        if task_data.priority:
            update_data["priority"] = task_data.priority
        if task_data.description:
            update_data["description"] = task_data.description

        self.db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
        )
        self.db.commit()
        return self.get_task(task_id)

    def delete_task(self, task_id: int, user_id: int):
        task = self.get_task(task_id)

        # Verify user is admin
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                workspace_users.c.workspace_id == task.workspace_id,
                workspace_users.c.user_id == user_id
            )
        ).scalar_one_or_none()
        if user_role != GroupRoleType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete tasks"
            )

        self.db.execute(delete(Task).where(Task.id == task_id))
        self.db.commit()
        return {"message": "Task deleted successfully"}

    def update_task_status(self, task_id: int, status_update: TaskStatusUpdate, user_id: int) -> Task:
        """Update task status with dependency validation"""
        task = self.get_task(task_id)
        
        # Verify user has access to workspace and is not a viewer
        self._verify_task_access(task, user_id, allow_viewer=False)
        
        # Check if status transition is allowed based on dependencies
        if status_update.status in [TaskStatus.closed]:
            # Check if any tasks depend on this one and are not completed
            dependent_tasks = self.db.execute(
                select(Task)
                .join(TaskDependency, Task.id == TaskDependency.blocked_task_id)
                .where(
                    and_(
                        TaskDependency.blocking_task_id == task_id,
                        Task.status != TaskStatus.closed
                    )
                )
            ).scalars().all()
            
            if dependent_tasks:
                task_titles = [t.title for t in dependent_tasks[:3]]  # Show first 3
                detail = f"Cannot close task while dependent tasks are open: {', '.join(task_titles)}"
                if len(dependent_tasks) > 3:
                    detail += f" and {len(dependent_tasks) - 3} more"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=detail
                )
        
        # Check if task is blocked by other tasks
        if status_update.status in [TaskStatus.in_progress, TaskStatus.closed]:
            blocking_tasks = self.db.execute(
                select(Task)
                .join(TaskDependency, Task.id == TaskDependency.blocking_task_id)
                .where(
                    and_(
                        TaskDependency.blocked_task_id == task_id,
                        Task.status != TaskStatus.closed
                    )
                )
            ).scalars().all()
            
            if blocking_tasks:
                task_titles = [t.title for t in blocking_tasks[:3]]
                detail = f"Cannot update status while blocked by: {', '.join(task_titles)}"
                if len(blocking_tasks) > 3:
                    detail += f" and {len(blocking_tasks) - 3} more"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=detail
                )
        
        # Update task status
        self.db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(status=status_update.status)
        )
        self.db.commit()
        
        return self.get_task(task_id)

    def update_task_category(self, task_id: int, category_id: int, user_id: int) -> Task:
        """Update task category"""
        task = self.get_task(task_id)
        
        # Verify user has access to workspace and is not a viewer
        self._verify_task_access(task, user_id, allow_viewer=False)
        
        # Verify category exists and belongs to same workspace
        if category_id:
            category = self.db.execute(
                select(Category).where(Category.id == category_id)
            ).scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
            
            if category.workspace_id != task.workspace_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category must belong to the same workspace as the task"
                )
        
        # Update task category
        self.db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(category_id=category_id)
        )
        self.db.commit()
        
        return self.get_task(task_id)

    def move_task_to_workspace(self, task_id: int, workspace_move: TaskWorkspaceMove, user_id: int) -> Task:
        """Move task to different workspace"""
        task = self.get_task(task_id)
        
        # Verify user has admin access to source workspace
        source_user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                and_(
                    workspace_users.c.workspace_id == task.workspace_id,
                    workspace_users.c.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if source_user_role != GroupRoleType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required to move tasks from workspace"
            )
        
        # Verify user has access to target workspace
        target_user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                and_(
                    workspace_users.c.workspace_id == workspace_move.workspace_id,
                    workspace_users.c.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if not target_user_role or target_user_role == GroupRoleType.viewer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to target workspace"
            )
        
        # Verify target workspace exists
        target_workspace = self.db.execute(
            select(Workspace).where(Workspace.id == workspace_move.workspace_id)
        ).scalar_one_or_none()
        
        if not target_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target workspace not found"
            )
        
        # Check for dependencies that would be broken
        cross_workspace_dependencies = self.db.execute(
            select(TaskDependency)
            .join(Task, TaskDependency.blocking_task_id == Task.id)
            .where(
                and_(
                    TaskDependency.blocked_task_id == task_id,
                    Task.workspace_id != workspace_move.workspace_id
                )
            )
        ).scalars().all()
        
        if cross_workspace_dependencies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move task with cross-workspace dependencies"
            )
        
        # Update task workspace and clear category (since categories are workspace-specific)
        self.db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(
                workspace_id=workspace_move.workspace_id,
                category_id=None  # Clear category since it belongs to old workspace
            )
        )
        self.db.commit()
        
        return self.get_task(task_id)

    def _verify_task_access(self, task: Task, user_id: int, allow_viewer: bool = True):
        """Verify user has access to task's workspace"""
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
        
        if not allow_viewer and user_role == GroupRoleType.viewer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Viewer access insufficient for this operation"
            )
        
        return user_role