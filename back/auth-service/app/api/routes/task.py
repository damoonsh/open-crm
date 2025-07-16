from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate, TaskWorkspaceMove
from app.core.security import oauth2_scheme, get_user_id_from_token

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return TaskService(db).create_task(task, user_id)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return TaskService(db).get_task(task_id)

@router.get("/workspace/{workspace_id}", response_model=list[TaskResponse])
async def get_workspace_tasks(workspace_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return TaskService(db).get_workspace_tasks(workspace_id, user_id)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return TaskService(db).update_task(task_id, user_id, task)

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    return TaskService(db).delete_task(task_id, user_id)

@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int, 
    status_update: TaskStatusUpdate, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """Update task status"""
    user_id = get_user_id_from_token(token)
    return TaskService(db).update_task_status(task_id, status_update, user_id)

@router.put("/{task_id}/category", response_model=TaskResponse)
async def update_task_category(
    task_id: int, 
    category_id: int, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """Update task category"""
    user_id = get_user_id_from_token(token)
    return TaskService(db).update_task_category(task_id, category_id, user_id)

@router.put("/{task_id}/workspace", response_model=TaskResponse)
async def move_task_to_workspace(
    task_id: int, 
    workspace_move: TaskWorkspaceMove, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """Move task to different workspace"""
    user_id = get_user_id_from_token(token)
    return TaskService(db).move_task_to_workspace(task_id, workspace_move, user_id)