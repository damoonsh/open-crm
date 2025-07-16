# Design Document

## Data Modeling

### User Model
```python
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, Integer, String, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class GroupRoleType(enum.Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sessions = relationship("UserSession", back_populates="user")
    workspaces = relationship("Workspace", secondary="workspace_users", back_populates="users")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    reported_tasks = relationship("Task", foreign_keys="Task.reporter_id", back_populates="reporter")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token_jti = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
```

### Workspace Model
```python
from datetime import datetime
from sqlalchemy import UniqueConstraint, Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class GroupRoleType(enum.Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"

# Association table for workspace users
workspace_users = Table(
    'workspace_users',
    Base.metadata,
    Column('workspace_id', Integer, ForeignKey('workspaces.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role', Enum(GroupRoleType), nullable=False, default=GroupRoleType.member),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow),
    UniqueConstraint('workspace_id', 'user_id', name='_workspace_user_uc')
)

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", secondary=workspace_users, back_populates="workspaces")
    tasks = relationship("Task", back_populates="workspace", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="workspace", cascade="all, delete-orphan")
```

### Category Model
```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.task import TaskStatus

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=False, default='#6366f1')  # Hex color code
    position = Column(Integer, nullable=False, default=0)  # For ordering
    is_archived = Column(Boolean, nullable=False, default=False)
    
    # Default workflow settings
    default_status = Column(TaskStatus, nullable=False, default=TaskStatus.open)
    allowed_statuses = Column(JSON, nullable=False, default=lambda: ["open", "in_progress", "review", "closed"])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="categories")
    tasks = relationship("Task", back_populates="category")
```

### Task Model
```python
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Enum, Text, DateTime, String, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class PriorityType(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    review = "review"
    closed = "closed"
    blocked = "blocked"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id', ondelete='CASCADE'))
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    assignee_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reporter_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    priority = Column(Enum(PriorityType), nullable=False, default=PriorityType.medium)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.open)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    story_points = Column(Integer, nullable=True)
    labels = Column(JSON, nullable=True)  # Store as JSON array of strings
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    blocking_dependencies = relationship("TaskDependency", foreign_keys="TaskDependency.blocking_task_id", back_populates="blocking_task")
    blocked_by_dependencies = relationship("TaskDependency", foreign_keys="TaskDependency.blocked_task_id", back_populates="blocked_task")
```

### TaskDependency Model
```python
class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    blocking_task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)  # Task that blocks
    blocked_task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)   # Task that is blocked
    dependency_type = Column(String(20), nullable=False, default='blocks')  # blocks, depends_on
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    blocking_task = relationship("Task", foreign_keys=[blocking_task_id], back_populates="blocking_dependencies")
    blocked_task = relationship("Task", foreign_keys=[blocked_task_id], back_populates="blocked_by_dependencies")
    created_by = relationship("User")
    
    __table_args__ = (
        # Ensure unique dependency pairs
        UniqueConstraint('blocking_task_id', 'blocked_task_id', name='_blocking_blocked_uc'),
        # Prevent self-dependencies
        CheckConstraint('blocking_task_id != blocked_task_id', name='_no_self_dependency'),
    )
```

### Comment Model
```python
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    edited_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    user = relationship("User")
    replies = relationship("CommentReply", back_populates="comment", cascade="all, delete-orphan")

class CommentReply(Base):
    __tablename__ = "comment_replies"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    edited_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    comment = relationship("Comment", back_populates="replies")
    user = relationship("User")
```

## Routes

### Authentication Routes
```python
# POST /auth/login
# POST /auth/register
# POST /auth/logout
# GET /auth/me
```

### Workspace Routes
```python
# GET /workspaces - List user's workspaces
# POST /workspaces - Create workspace
# GET /workspaces/{workspace_id} - Get workspace details
# PUT /workspaces/{workspace_id} - Update workspace
# DELETE /workspaces/{workspace_id} - Delete workspace
# GET /workspaces/{workspace_id}/users - List workspace users
# POST /workspaces/{workspace_id}/users - Add user to workspace
# PUT /workspaces/{workspace_id}/users/{user_id} - Update user role
# DELETE /workspaces/{workspace_id}/users/{user_id} - Remove user from workspace
```

### Category Routes
```python
# GET /workspaces/{workspace_id}/categories - List categories in workspace
# POST /workspaces/{workspace_id}/categories - Create category
# GET /categories/{category_id} - Get category details
# PUT /categories/{category_id} - Update category
# DELETE /categories/{category_id} - Delete category
# PUT /categories/{category_id}/position - Update category position
```

### Task Routes
```python
# GET /workspaces/{workspace_id}/tasks - List tasks in workspace
# POST /workspaces/{workspace_id}/tasks - Create task
# GET /tasks/{task_id} - Get task details
# PUT /tasks/{task_id} - Update task
# DELETE /tasks/{task_id} - Delete task
# PUT /tasks/{task_id}/status - Update task status
# PUT /tasks/{task_id}/category - Update task category
# PUT /tasks/{task_id}/workspace - Move task to different workspace
```

### Task Dependency Routes
```python
# GET /tasks/{task_id}/dependencies - Get task dependencies
# POST /tasks/{task_id}/dependencies - Add dependency
# DELETE /tasks/{task_id}/dependencies/{blocking_task_id} - Remove dependency
```

### Comment Routes
```python
# GET /tasks/{task_id}/comments - List task comments
# POST /tasks/{task_id}/comments - Create comment
# GET /comments/{comment_id} - Get comment details
# PUT /comments/{comment_id} - Update comment
# DELETE /comments/{comment_id} - Delete comment
# POST /comments/{comment_id}/replies - Reply to comment
```

## Input Schemas

### Authentication Schemas
```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
```

### Workspace Schemas
```python
class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class WorkspaceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

class WorkspaceUserAdd(BaseModel):
    user_email: EmailStr
    role: GroupRoleType = GroupRoleType.member

class WorkspaceUserUpdate(BaseModel):
    role: GroupRoleType
```

### Task Schemas
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    category_id: Optional[int] = None
    priority: PriorityType = PriorityType.medium
    assignee_id: Optional[int] = None
    story_points: Optional[int] = Field(None, ge=1, le=100)
    labels: Optional[List[str]] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    category_id: Optional[int] = None
    priority: Optional[PriorityType] = None
    assignee_id: Optional[int] = None
    story_points: Optional[int] = Field(None, ge=1, le=100)
    labels: Optional[List[str]] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskWorkspaceMove(BaseModel):
    workspace_id: int

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: PriorityType
    workspace_id: int
    category_id: Optional[int]
    assignee_id: Optional[int]
    reporter_id: Optional[int]
    story_points: Optional[int]
    labels: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    blocking_dependencies: List[int] = []
    blocked_by_dependencies: List[int] = []
```

### Category Schemas
```python
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: str = Field(default="#6366f1", regex="^#[0-9A-Fa-f]{6}$")
    position: int = Field(default=0, ge=0)
    default_status: TaskStatus = TaskStatus.open
    allowed_statuses: List[str] = Field(default=["open", "in_progress", "review", "closed"])

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    position: Optional[int] = Field(None, ge=0)
    is_archived: Optional[bool] = None
    default_status: Optional[TaskStatus] = None
    allowed_statuses: Optional[List[str]] = None

class CategoryResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    description: Optional[str]
    color: str
    position: int
    is_archived: bool
    default_status: TaskStatus
    allowed_statuses: List[str]
    created_at: datetime
    updated_at: datetime
```

### Dependency Schemas
```python
class DependencyCreate(BaseModel):
    blocking_task_id: int

class DependencyResponse(BaseModel):
    id: int
    dependent_task_id: int
    blocking_task_id: int
    created_at: datetime
```

### Comment Schemas
```python
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentReplyCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    created_at: datetime
    edited_at: datetime
    user: UserResponse
    replies: List['CommentReplyResponse'] = []

class CommentReplyResponse(BaseModel):
    id: int
    content: str
    comment_id: int
    user_id: int
    created_at: datetime
    edited_at: datetime
    user: UserResponse
```

## Frontend Per Functionality

### Authentication Frontend
**Components:**
- `LoginForm.vue` - Login form with email/password
- `RegisterForm.vue` - Registration form
- `AuthGuard.vue` - Route protection component

**Store:**
- `authStore.ts` - Manages user authentication state, login/logout actions

**Routes:**
- `/login` - Login page
- `/register` - Registration page

**Key Features:**
- Form validation with error display
- JWT token storage and management
- Automatic redirect after login
- Route guards for protected pages

### Workspace Management Frontend
**Components:**
- `WorkspaceList.vue` - Grid/list view of user workspaces
- `WorkspaceCard.vue` - Individual workspace display
- `WorkspaceForm.vue` - Create/edit workspace modal
- `WorkspaceSettings.vue` - Workspace settings and user management

**Store:**
- `workspaceStore.ts` - Manages workspace data, CRUD operations

**Routes:**
- `/workspaces` - Workspace list page
- `/workspaces/:id` - Individual workspace kanban view

**Key Features:**
- Workspace creation with validation
- User invitation and role management
- Workspace deletion with confirmation
- Real-time workspace updates

### Kanban Board Frontend
**Components:**
- `KanbanBoard.vue` - Main kanban board layout
- `KanbanColumn.vue` - Individual category columns (TODO, In Progress, etc.)
- `TaskCard.vue` - Draggable task cards
- `TaskModal.vue` - Detailed task view/edit modal

**Store:**
- `taskStore.ts` - Manages task data, drag-and-drop state

**Key Features:**
- Drag-and-drop task movement between columns
- Real-time updates when tasks change
- Visual indicators for dependencies and priorities
- Quick task creation from column headers
- Filtering and sorting options

### Task Management Frontend
**Components:**
- `TaskForm.vue` - Create/edit task form
- `TaskDetails.vue` - Detailed task view
- `TaskDependencies.vue` - Dependency management interface
- `TaskAssignment.vue` - User assignment dropdown

**Key Features:**
- Rich text editor for task descriptions
- Dependency visualization and management
- User assignment with search
- Priority and category selection
- Task history and audit trail

### Comment System Frontend
**Components:**
- `CommentThread.vue` - Main comment display
- `CommentItem.vue` - Individual comment with replies
- `CommentForm.vue` - Comment creation/edit form
- `CommentReply.vue` - Reply form component

**Store:**
- `commentStore.ts` - Manages comment data and threading

**Key Features:**
- Threaded comment display
- Real-time comment updates
- Rich text comment editing
- Comment deletion with confirmation
- @mention functionality for user notifications

### Shared Frontend Components
**Components:**
- `UserAvatar.vue` - User profile picture/initials
- `PriorityBadge.vue` - Priority level indicator
- `StatusBadge.vue` - Task status indicator
- `LoadingSpinner.vue` - Loading state component
- `ConfirmDialog.vue` - Confirmation modal
- `NotificationToast.vue` - Success/error notifications

**Composables:**
- `useApi.ts` - HTTP client with error handling
- `useAuth.ts` - Authentication utilities
- `usePermissions.ts` - Permission checking utilities
- `useWebSocket.ts` - Real-time updates via WebSocket

**Key Features:**
- Consistent design system
- Responsive layout for mobile/desktop
- Accessibility compliance (ARIA labels, keyboard navigation)
- Error boundary handling
- Optimistic UI updates