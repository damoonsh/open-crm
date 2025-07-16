from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session # Changed from AsyncSession
from app.schemas.auth import Token, UserCreate, UserLogin, UserUpdate
from app.core.db import get_db, get_current_user
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.login_user(user_data)

@router.api_route(
    "/me",
    methods=["GET", "PUT", "DELETE"],
    dependencies=[Depends(get_current_user)]
)
def handle_me_endpoint(
    request: Request,
    current_user = Depends(get_current_user),
    user_data: UserUpdate = None,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    if request.method == "GET":
        return current_user
    elif request.method == "PUT":
        return auth_service.update_user(current_user.id, user_data)
    elif request.method == "DELETE":
        return auth_service.delete_user(current_user.id)