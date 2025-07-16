from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.core.security import oauth2_scheme, get_user_id_from_token

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/workspace/{workspace_id}", response_model=List[CategoryResponse])
async def get_workspace_categories(
    workspace_id: int, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """Get all categories for a workspace"""
    user_id = get_user_id_from_token(token)
    return CategoryService(db).get_workspace_categories(workspace_id, user_id)

@router.post("/workspace/{workspace_id}", response_model=CategoryResponse)
async def create_category(
    workspace_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Create a new category in a workspace"""
    user_id = get_user_id_from_token(token)
    return CategoryService(db).create_category(workspace_id, category, user_id)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get a specific category by ID"""
    user_id = get_user_id_from_token(token)
    return CategoryService(db).get_category(category_id, user_id)

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Update a category"""
    user_id = get_user_id_from_token(token)
    return CategoryService(db).update_category(category_id, category, user_id)

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Delete a category"""
    user_id = get_user_id_from_token(token)
    return CategoryService(db).delete_category(category_id, user_id)

@router.put("/{category_id}/position")
async def update_category_position(
    category_id: int,
    position: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Update category position for reordering"""
    user_id = get_user_id_from_token(token)
    return CategoryService(db).update_category_position(category_id, position, user_id)