from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, and_, func
from app.models.category import Category
from app.models.workspace import workspace_users, GroupRoleType
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from typing import List


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, workspace_id: int, category_data: CategoryCreate, user_id: int) -> CategoryResponse:
        """Create a new category in a workspace"""
        # Verify user has access to workspace
        self._verify_workspace_access(workspace_id, user_id)
        
        # Check if category name already exists in workspace
        existing_category = self.db.execute(
            select(Category).where(
                and_(
                    Category.workspace_id == workspace_id,
                    Category.name == category_data.name,
                    Category.is_archived == False
                )
            )
        ).scalar_one_or_none()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists in this workspace"
            )
        
        # Get next position if not specified
        if category_data.position == 0:
            max_position = self.db.execute(
                select(func.max(Category.position))
                .where(Category.workspace_id == workspace_id)
            ).scalar() or 0
            category_data.position = max_position + 1
        
        # Create new category
        new_category = Category(
            workspace_id=workspace_id,
            name=category_data.name,
            description=category_data.description,
            color=category_data.color,
            position=category_data.position,
            default_status=category_data.default_status,
            allowed_statuses=category_data.allowed_statuses
        )
        
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        
        return CategoryResponse.from_orm(new_category)

    def get_category(self, category_id: int, user_id: int) -> CategoryResponse:
        """Get a specific category by ID"""
        category = self.db.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Verify user has access to workspace
        self._verify_workspace_access(category.workspace_id, user_id)
        
        return CategoryResponse.from_orm(category)

    def get_workspace_categories(self, workspace_id: int, user_id: int) -> List[CategoryResponse]:
        """Get all categories for a workspace"""
        # Verify user has access to workspace
        self._verify_workspace_access(workspace_id, user_id)
        
        categories = self.db.execute(
            select(Category)
            .where(
                and_(
                    Category.workspace_id == workspace_id,
                    Category.is_archived == False
                )
            )
            .order_by(Category.position)
        ).scalars().all()
        
        return [CategoryResponse.from_orm(category) for category in categories]

    def update_category(self, category_id: int, category_data: CategoryUpdate, user_id: int) -> CategoryResponse:
        """Update a category"""
        category = self.db.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Verify user has access to workspace
        self._verify_workspace_access(category.workspace_id, user_id)
        
        # Check if new name conflicts with existing categories
        if category_data.name and category_data.name != category.name:
            existing_category = self.db.execute(
                select(Category).where(
                    and_(
                        Category.workspace_id == category.workspace_id,
                        Category.name == category_data.name,
                        Category.id != category_id,
                        Category.is_archived == False
                    )
                )
            ).scalar_one_or_none()
            
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name already exists in this workspace"
                )
        
        # Update category fields
        update_data = {}
        if category_data.name is not None:
            update_data["name"] = category_data.name
        if category_data.description is not None:
            update_data["description"] = category_data.description
        if category_data.color is not None:
            update_data["color"] = category_data.color
        if category_data.position is not None:
            update_data["position"] = category_data.position
        if category_data.is_archived is not None:
            update_data["is_archived"] = category_data.is_archived
        if category_data.default_status is not None:
            update_data["default_status"] = category_data.default_status
        if category_data.allowed_statuses is not None:
            update_data["allowed_statuses"] = category_data.allowed_statuses
        
        if update_data:
            self.db.execute(
                update(Category)
                .where(Category.id == category_id)
                .values(**update_data)
            )
            self.db.commit()
        
        # Refresh and return updated category
        self.db.refresh(category)
        return CategoryResponse.from_orm(category)

    def delete_category(self, category_id: int, user_id: int):
        """Delete a category (soft delete by archiving)"""
        category = self.db.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Verify user has access to workspace
        self._verify_workspace_access(category.workspace_id, user_id)
        
        # Soft delete by archiving
        self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(is_archived=True)
        )
        self.db.commit()
        
        return {"message": "Category archived successfully"}

    def update_category_position(self, category_id: int, new_position: int, user_id: int):
        """Update category position for reordering"""
        category = self.db.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Verify user has access to workspace
        self._verify_workspace_access(category.workspace_id, user_id)
        
        old_position = category.position
        
        if new_position == old_position:
            return {"message": "Position unchanged"}
        
        # Update positions of other categories
        if new_position > old_position:
            # Moving down - shift categories up
            self.db.execute(
                update(Category)
                .where(
                    and_(
                        Category.workspace_id == category.workspace_id,
                        Category.position > old_position,
                        Category.position <= new_position,
                        Category.id != category_id
                    )
                )
                .values(position=Category.position - 1)
            )
        else:
            # Moving up - shift categories down
            self.db.execute(
                update(Category)
                .where(
                    and_(
                        Category.workspace_id == category.workspace_id,
                        Category.position >= new_position,
                        Category.position < old_position,
                        Category.id != category_id
                    )
                )
                .values(position=Category.position + 1)
            )
        
        # Update the category's position
        self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(position=new_position)
        )
        
        self.db.commit()
        return {"message": "Category position updated successfully"}

    def _verify_workspace_access(self, workspace_id: int, user_id: int):
        """Verify user has access to workspace"""
        user_role = self.db.execute(
            select(workspace_users.c.role)
            .where(
                and_(
                    workspace_users.c.workspace_id == workspace_id,
                    workspace_users.c.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to workspace"
            )
        
        return user_role