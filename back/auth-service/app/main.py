from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, workspace_router, task_router, comment_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(workspace_router.router, prefix="/workspaces", tags=["workspaces"])
app.include_router(task_router.router, prefix="/tasks", tags=["tasks"])
app.include_router(comment_router.router, prefix="/comments", tags=["comments"])

@app.on_event("startup")
async def startup_event():
    logger.info("Auth Service started successfully")

@app.get("/")
async def root():
    return {"message": "Auth Service is running!"}