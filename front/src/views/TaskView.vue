<template>
  <div class="task-detail-view">
    <!-- Header -->
    <div class="task-header">
      <div class="header-navigation">
        <v-btn
          variant="text"
          @click="goBack"
          prepend-icon="mdi-arrow-left"
        >
          Back to {{ backToText }}
        </v-btn>
        
        <div class="breadcrumb">
          <span class="workspace-name">{{ workspaceName }}</span>
          <v-icon>mdi-chevron-right</v-icon>
          <span class="task-id">Task #{{ taskId }}</span>
        </div>
      </div>
      
      <div class="header-actions">
        <v-btn
          v-if="canEditTasks"
          color="primary"
          @click="showEditDialog = true"
        >
          <v-icon left>mdi-pencil</v-icon>
          Edit Task
        </v-btn>
        
        <v-menu>
          <template #activator="{ props: menuProps }">
            <v-btn icon v-bind="menuProps">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item v-if="canEditTasks" @click="duplicateTask">
              <v-list-item-title>Duplicate Task</v-list-item-title>
            </v-list-item>
            <v-list-item v-if="canEditTasks" @click="showMoveDialog = true">
              <v-list-item-title>Move to Workspace</v-list-item-title>
            </v-list-item>
            <v-divider />
            <v-list-item v-if="canEditTasks" @click="confirmDelete" class="text-error">
              <v-list-item-title>Delete Task</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p>Loading task details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <v-alert type="error" dismissible @click:close="clearError">
        {{ error }}
      </v-alert>
      <v-btn color="primary" @click="loadTask">Retry</v-btn>
    </div>

    <!-- Task Not Found -->
    <div v-else-if="!task" class="not-found-container">
      <v-icon size="96" color="grey-lighten-2">mdi-file-document-outline</v-icon>
      <h2>Task Not Found</h2>
      <p>The task you're looking for doesn't exist or you don't have permission to view it.</p>
      <v-btn color="primary" @click="goBack">Go Back</v-btn>
    </div>

    <!-- Main Content -->
    <div v-else class="task-content">
      <v-row>
        <!-- Main Task Information -->
        <v-col cols="12" lg="8">
          <v-card class="task-main-card">
            <!-- Task Title and Status -->
            <v-card-title class="task-title-section">
              <div class="title-content">
                <h1 class="task-title">{{ task.title }}</h1>
                <TaskStatusBadges
                  :task="task"
                  :show-priority="true"
                  :show-story-points="true"
                  :show-dependencies="true"
                />
              </div>
            </v-card-title>

            <!-- Task Description -->
            <v-card-text class="task-description-section">
              <h3>Description</h3>
              <div class="task-description">
                {{ task.description || 'No description provided' }}
              </div>
            </v-card-text>

            <!-- Task Labels -->
            <v-card-text v-if="task.labels && task.labels.length > 0" class="task-labels-section">
              <h3>Labels</h3>
              <div class="labels-container">
                <v-chip
                  v-for="label in task.labels"
                  :key="label"
                  size="small"
                  variant="outlined"
                  class="mr-2 mb-2"
                >
                  {{ label }}
                </v-chip>
              </div>
            </v-card-text>

            <!-- Task Dependencies -->
            <v-card-text v-if="hasDependencies" class="task-dependencies-section">
              <TaskDependencies
                :task="task"
                :workspace-id="task.workspace_id"
              />
            </v-card-text>
          </v-card>

          <!-- Comments Section -->
          <v-card class="comments-card mt-6">
            <v-card-title>
              <v-icon left>mdi-comment-multiple</v-icon>
              Comments
            </v-card-title>
            <v-card-text>
              <Comments
                :task-id="task.id"
                :workspace-id="task.workspace_id"
              />
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Sidebar -->
        <v-col cols="12" lg="4">
          <div class="task-sidebar">
            <!-- Task Properties -->
            <v-card class="properties-card">
              <v-card-title>Task Properties</v-card-title>
              <v-card-text>
                <div class="property-list">
                  <div class="property-item">
                    <span class="property-label">Status:</span>
                    <v-chip :color="getStatusColor(task.status)" size="small">
                      {{ formatStatus(task.status) }}
                    </v-chip>
                  </div>
                  
                  <div class="property-item">
                    <span class="property-label">Priority:</span>
                    <v-chip :color="getPriorityColor(task.priority)" size="small">
                      {{ formatPriority(task.priority) }}
                    </v-chip>
                  </div>
                  
                  <div class="property-item">
                    <span class="property-label">Category:</span>
                    <span v-if="task.category_id">{{ getCategoryName(task.category_id) }}</span>
                    <span v-else class="text-grey">Uncategorized</span>
                  </div>
                  
                  <div class="property-item">
                    <span class="property-label">Assignee:</span>
                    <span v-if="task.assignee_id">{{ getAssigneeName(task.assignee_id) }}</span>
                    <span v-else class="text-grey">Unassigned</span>
                  </div>
                  
                  <div class="property-item">
                    <span class="property-label">Reporter:</span>
                    <span v-if="task.reporter_id">{{ getReporterName(task.reporter_id) }}</span>
                    <span v-else class="text-grey">Unknown</span>
                  </div>
                  
                  <div v-if="task.story_points" class="property-item">
                    <span class="property-label">Story Points:</span>
                    <span>{{ task.story_points }}</span>
                  </div>
                </div>
              </v-card-text>
            </v-card>

            <!-- Task Timeline -->
            <v-card class="timeline-card mt-4">
              <v-card-title>Timeline</v-card-title>
              <v-card-text>
                <div class="timeline-list">
                  <div class="timeline-item">
                    <v-icon color="success" size="small">mdi-plus-circle</v-icon>
                    <div class="timeline-content">
                      <div class="timeline-title">Task Created</div>
                      <div class="timeline-date">{{ formatDateTime(task.created_at) }}</div>
                    </div>
                  </div>
                  
                  <div v-if="task.updated_at !== task.created_at" class="timeline-item">
                    <v-icon color="info" size="small">mdi-pencil-circle</v-icon>
                    <div class="timeline-content">
                      <div class="timeline-title">Last Updated</div>
                      <div class="timeline-date">{{ formatDateTime(task.updated_at) }}</div>
                    </div>
                  </div>
                </div>
              </v-card-text>
            </v-card>

            <!-- Quick Actions -->
            <v-card v-if="canEditTasks" class="actions-card mt-4">
              <v-card-title>Quick Actions</v-card-title>
              <v-card-text>
                <div class="action-buttons">
                  <v-btn
                    block
                    variant="outlined"
                    @click="changeStatus"
                    class="mb-2"
                  >
                    <v-icon left>mdi-swap-horizontal</v-icon>
                    Change Status
                  </v-btn>
                  
                  <v-btn
                    block
                    variant="outlined"
                    @click="changePriority"
                    class="mb-2"
                  >
                    <v-icon left>mdi-flag</v-icon>
                    Change Priority
                  </v-btn>
                  
                  <v-btn
                    block
                    variant="outlined"
                    @click="assignTask"
                    class="mb-2"
                  >
                    <v-icon left>mdi-account</v-icon>
                    Assign Task
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </div>
        </v-col>
      </v-row>
    </div>

    <!-- Edit Task Dialog -->
    <TaskForm
      v-model="showEditDialog"
      :task="task"
      :workspace-id="task?.workspace_id || 0"
      @saved="onTaskUpdated"
      @cancelled="showEditDialog = false"
    />

    <!-- Move Task Dialog -->
    <TaskMoveDialog
      v-if="task"
      v-model="showMoveDialog"
      :task="task"
      @moved="onTaskMoved"
      @cancelled="showMoveDialog = false"
    />

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Task</v-card-title>
        <v-card-text>
          Are you sure you want to delete "{{ task?.title }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteTask">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Success/Error Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTaskStore } from '@/stores/tasks';
import { useWorkspaceStore } from '@/stores/workspace';
import { useCategoryStore } from '@/stores/categories';
import { useAuthStore } from '@/stores/auth';
import TaskStatusBadges from '@/components/task/TaskStatusBadges.vue';
import TaskDependencies from '@/components/task/TaskDependencies.vue';
import TaskForm from '@/components/task/TaskForm.vue';
import TaskMoveDialog from '@/components/task/TaskMoveDialog.vue';
import Comments from '@/components/task/Comments.vue';
import type { Task } from '@/stores/tasks';

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();
const workspaceStore = useWorkspaceStore();
const categoryStore = useCategoryStore();
const authStore = useAuthStore();

// Component state
const showEditDialog = ref(false);
const showMoveDialog = ref(false);
const showDeleteDialog = ref(false);
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
});

// Computed properties
const taskId = computed(() => {
  const idParam = route.params.id;
  const parsedId = typeof idParam === 'string' ? parseInt(idParam, 10) : Number(idParam);
  return isNaN(parsedId) ? null : parsedId;
});

const task = computed(() => taskStore.getTaskById(taskId.value || 0));
const loading = computed(() => taskStore.loading);
const error = computed(() => taskStore.error);

const workspaceName = computed(() => {
  if (!task.value) return 'Unknown Workspace';
  const workspace = workspaceStore.getWorkspaceById(task.value.workspace_id);
  return workspace?.name || 'Unknown Workspace';
});

const backToText = computed(() => {
  return task.value ? workspaceName.value : 'Workspaces';
});

const canEditTasks = computed(() => {
  if (!task.value) return false;
  return authStore.canEditTasks(task.value.workspace_id);
});

const hasDependencies = computed(() => {
  if (!task.value) return false;
  return (task.value.blocking_dependencies && task.value.blocking_dependencies.length > 0) ||
         (task.value.blocked_by_dependencies && task.value.blocked_by_dependencies.length > 0);
});

// Methods
const loadTask = async () => {
  if (!taskId.value) return;

  try {
    await Promise.all([
      taskStore.fetchTasks(0), // This will load all tasks - we need the specific task
      categoryStore.fetchCategories(0) // We'll need to get workspace ID first
    ]);

    // If we have the task, load its workspace data
    if (task.value) {
      await Promise.all([
        workspaceStore.getWorkspace(task.value.workspace_id),
        categoryStore.fetchCategories(task.value.workspace_id)
      ]);
    }
  } catch (error) {
    console.error('Error loading task:', error);
  }
};

const goBack = () => {
  if (task.value) {
    router.push(`/workspace/${task.value.workspace_id}`);
  } else {
    router.push('/workspaces');
  }
};

const duplicateTask = async () => {
  if (!task.value || !canEditTasks.value) return;

  try {
    const duplicateData = {
      title: `${task.value.title} (Copy)`,
      description: task.value.description,
      category_id: task.value.category_id,
      priority: task.value.priority,
      assignee_id: task.value.assignee_id,
      story_points: task.value.story_points,
      labels: task.value.labels ? [...task.value.labels] : []
    };

    await taskStore.createTask(task.value.workspace_id, duplicateData);
    showSnackbar('Task duplicated successfully', 'success');
  } catch (error) {
    console.error('Error duplicating task:', error);
    showSnackbar('Failed to duplicate task', 'error');
  }
};

const confirmDelete = () => {
  showDeleteDialog.value = true;
};

const deleteTask = async () => {
  if (!task.value) return;

  try {
    await taskStore.deleteTask(task.value.id);
    showSnackbar('Task deleted successfully', 'success');
    showDeleteDialog.value = false;
    goBack();
  } catch (error) {
    console.error('Error deleting task:', error);
    showSnackbar('Failed to delete task', 'error');
  }
};

const onTaskUpdated = () => {
  showEditDialog.value = false;
  showSnackbar('Task updated successfully', 'success');
  loadTask(); // Refresh task data
};

const onTaskMoved = (workspaceId: number) => {
  showMoveDialog.value = false;
  showSnackbar('Task moved successfully', 'success');
  router.push(`/workspace/${workspaceId}`);
};

const changeStatus = () => {
  // TODO: Implement quick status change
  showSnackbar('Quick status change coming soon', 'info');
};

const changePriority = () => {
  // TODO: Implement quick priority change
  showSnackbar('Quick priority change coming soon', 'info');
};

const assignTask = () => {
  // TODO: Implement quick assignment
  showSnackbar('Quick assignment coming soon', 'info');
};

const clearError = () => {
  taskStore.clearError();
};

const showSnackbar = (text: string, color: string) => {
  snackbar.value = { show: true, text, color };
};

// Utility methods
const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    open: 'blue',
    in_progress: 'orange',
    review: 'purple',
    closed: 'green',
    blocked: 'red'
  };
  return colors[status] || 'grey';
};

const getPriorityColor = (priority: string): string => {
  const colors: Record<string, string> = {
    high: 'error',
    medium: 'warning',
    low: 'success'
  };
  return colors[priority] || 'grey';
};

const formatStatus = (status: string): string => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatPriority = (priority: string): string => {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
};

const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString();
};

const getCategoryName = (categoryId: number): string => {
  const category = categoryStore.categories.find(cat => cat.id === categoryId);
  return category?.name || 'Unknown Category';
};

const getAssigneeName = (assigneeId: number): string => {
  // TODO: Get actual user name from user store
  return `User ${assigneeId}`;
};

const getReporterName = (reporterId: number): string => {
  // TODO: Get actual user name from user store
  return `User ${reporterId}`;
};

// Lifecycle
onMounted(() => {
  loadTask();
});

// Watch for route changes
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadTask();
  }
});
</script>

<style scoped>
.task-detail-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.task-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-navigation {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #666;
}

.workspace-name {
  font-weight: 500;
}

.task-id {
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loading-container,
.error-container,
.not-found-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 48px;
  text-align: center;
}

.loading-container p {
  margin-top: 16px;
  color: #666;
}

.not-found-container h2 {
  margin: 16px 0 8px 0;
  color: #666;
}

.not-found-container p {
  margin: 0 0 24px 0;
  color: #999;
}

.task-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.task-main-card {
  margin-bottom: 24px;
}

.task-title-section {
  padding-bottom: 16px;
}

.title-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  line-height: 1.3;
}

.task-description-section h3,
.task-labels-section h3,
.task-dependencies-section h3 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.task-description {
  line-height: 1.6;
  color: #666;
  white-space: pre-wrap;
}

.labels-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.task-sidebar {
  position: sticky;
  top: 24px;
}

.properties-card,
.timeline-card,
.actions-card {
  margin-bottom: 16px;
}

.property-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.property-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.property-label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.timeline-content {
  flex: 1;
}

.timeline-title {
  font-weight: 500;
  margin-bottom: 2px;
}

.timeline-date {
  font-size: 0.85rem;
  color: #666;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Responsive design */
@media (max-width: 1024px) {
  .task-content .v-row {
    flex-direction: column-reverse;
  }
  
  .task-sidebar {
    position: static;
    margin-bottom: 24px;
  }
}

@media (max-width: 768px) {
  .task-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-navigation {
    justify-content: space-between;
  }

  .title-content {
    align-items: flex-start;
  }

  .property-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>