from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserUpdate
from app.core.security import create_access_token, verify_password, get_password_hash

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserCreate) -> Token:
        # Check if email exists
        user = self.db.execute(select(User).where(User.email == user_data.email)).scalar_one_or_none()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username exists
        user = self.db.execute(select(User).where(User.username == user_data.username)).scalar_one_or_none()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user with all required fields
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password)
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Create and return access token
        access_token = create_access_token(new_user.id)
        return Token(access_token=access_token)

    def login_user(self, user_data: UserLogin) -> Token:
        user = self.db.execute(select(User).where(User.email == user_data.email)).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        access_token = create_access_token(user.id)
        return Token(access_token=access_token)

    def update_user(self, user_id: int, user_data: UserUpdate):
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        update_data = {}
        if user_data.email:
            # Check if new email is already taken
            existing_user = self.db.execute(
                select(User).where(User.email == user_data.email)
            ).scalar_one_or_none()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            update_data["email"] = user_data.email

        if user_data.password:
            update_data["hashed_password"] = get_password_hash(user_data.password)

        self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        self.db.commit()
        return self.get_user_by_id(user_id)

    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        self.db.execute(delete(User).where(User.id == user_id))
        self.db.commit()
        return {"message": "User deleted successfully"}

    def get_user_by_id(self, user_id: int):
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        return user