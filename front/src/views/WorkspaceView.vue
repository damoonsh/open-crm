<template>
  <div class="workspace-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p>Loading workspace...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <v-alert type="error" dismissible @click:close="clearError">
        {{ error }}
      </v-alert>
      <v-btn color="primary" @click="loadWorkspace">Retry</v-btn>
    </div>

    <!-- Access Denied -->
    <div v-else-if="!hasAccess" class="access-denied">
      <v-icon size="96" color="grey-lighten-2">mdi-lock</v-icon>
      <h2>Access Denied</h2>
      <p>You don't have permission to view this workspace.</p>
      <v-btn color="primary" to="/workspaces">Back to Workspaces</v-btn>
    </div>

    <!-- Main Content -->
    <div v-else class="workspace-content">
      <!-- Workspace Header -->
      <div class="workspace-header">
        <div class="workspace-info">
          <div class="breadcrumb">
            <v-btn variant="text" to="/workspaces" size="small">
              <v-icon left>mdi-arrow-left</v-icon>
              Workspaces
            </v-btn>
            <v-icon>mdi-chevron-right</v-icon>
            <span class="current-workspace">{{ workspace?.name }}</span>
          </div>
          
          <div class="workspace-title">
            <h1>{{ workspace?.name }}</h1>
            <p v-if="workspace?.description" class="workspace-description">
              {{ workspace.description }}
            </p>
          </div>
        </div>

        <div class="workspace-actions">
          <!-- View Toggle -->
          <v-btn-toggle v-model="currentView" mandatory>
            <v-btn value="kanban">
              <v-icon left>mdi-view-column</v-icon>
              Kanban
            </v-btn>
            <v-btn value="list">
              <v-icon left>mdi-format-list-bulleted</v-icon>
              List
            </v-btn>
          </v-btn-toggle>

          <!-- Quick Actions -->
          <v-btn
            v-if="canCreateTasks"
            color="primary"
            @click="showTaskForm = true"
          >
            <v-icon left>mdi-plus</v-icon>
            New Task
          </v-btn>

          <!-- Workspace Menu -->
          <v-menu>
            <template #activator="{ props: menuProps }">
              <v-btn icon v-bind="menuProps">
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item v-if="canManageWorkspace" @click="showWorkspaceSettings = true">
                <v-list-item-title>Workspace Settings</v-list-item-title>
              </v-list-item>
              <v-list-item @click="showCategoryManagement = true">
                <v-list-item-title>Manage Categories</v-list-item-title>
              </v-list-item>
              <v-list-item @click="showTaskFilters = !showTaskFilters">
                <v-list-item-title>
                  {{ showTaskFilters ? 'Hide' : 'Show' }} Filters
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </div>

      <!-- Task Filters Panel -->
      <v-expand-transition>
        <div v-if="showTaskFilters" class="filters-panel">
          <v-card>
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="3">
                  <v-text-field
                    v-model="filters.search"
                    placeholder="Search tasks..."
                    variant="outlined"
                    density="compact"
                    hide-details
                  >
                    <template #prepend-inner>
                      <v-icon>mdi-magnify</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                
                <v-col cols="12" sm="3">
                  <v-select
                    v-model="filters.status"
                    :items="statusFilterOptions"
                    label="Status"
                    multiple
                    chips
                    variant="outlined"
                    density="compact"
                    hide-details
                  />
                </v-col>
                
                <v-col cols="12" sm="3">
                  <v-select
                    v-model="filters.priority"
                    :items="priorityFilterOptions"
                    label="Priority"
                    multiple
                    chips
                    variant="outlined"
                    density="compact"
                    hide-details
                  />
                </v-col>
                
                <v-col cols="12" sm="3">
                  <v-select
                    v-model="filters.assignee"
                    :items="assigneeFilterOptions"
                    label="Assignee"
                    multiple
                    chips
                    variant="outlined"
                    density="compact"
                    hide-details
                  />
                </v-col>
              </v-row>
              
              <div class="filter-actions">
                <v-btn size="small" @click="clearFilters">Clear All</v-btn>
                <v-chip v-if="activeFiltersCount > 0" size="small" color="primary">
                  {{ activeFiltersCount }} active filters
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-expand-transition>

      <!-- Main Content Area -->
      <div class="main-content">
        <!-- Kanban View -->
        <div v-if="currentView === 'kanban'" class="kanban-view">
          <KanbanBoard :workspace-id="workspaceId" />
        </div>

        <!-- List View -->
        <div v-else-if="currentView === 'list'" class="list-view">
          <TaskList 
            :workspace-id="workspaceId"
            :filters="filters"
            @task-click="openTaskDetail"
          />
        </div>
      </div>
    </div>

    <!-- Task Form Dialog -->
    <TaskForm
      v-model="showTaskForm"
      :workspace-id="workspaceId"
      @saved="onTaskSaved"
      @cancelled="showTaskForm = false"
    />

    <!-- Workspace Settings Dialog -->
    <v-dialog v-model="showWorkspaceSettings" max-width="900">
      <WorkspaceSettings :workspace-id="workspaceId" />
    </v-dialog>

    <!-- Category Management Dialog -->
    <v-dialog v-model="showCategoryManagement" max-width="800">
      <CategoryList :workspace-id="workspaceId" />
    </v-dialog>

    <!-- Task Detail Dialog -->
    <v-dialog v-model="showTaskDetail" max-width="900">
      <TaskDetails
        v-if="selectedTask"
        :task="selectedTask"
        :workspace-id="workspaceId"
        @updated="onTaskUpdated"
        @closed="closeTaskDetail"
      />
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useWorkspaceStore } from '@/stores/workspace';
import { useTaskStore } from '@/stores/tasks';
import { useCategoryStore } from '@/stores/categories';
import { useAuthStore } from '@/stores/auth';
import KanbanBoard from '@/components/KanbanBoard.vue';
import TaskList from '@/components/task/TaskList.vue';
import TaskForm from '@/components/task/TaskForm.vue';
import TaskDetails from '@/components/task/TaskDetails.vue';
import WorkspaceSettings from '@/components/workspace/WorkspaceSettings.vue';
import CategoryList from '@/components/category/CategoryList.vue';
import type { Task } from '@/stores/tasks';

const route = useRoute();
const router = useRouter();
const workspaceStore = useWorkspaceStore();
const taskStore = useTaskStore();
const categoryStore = useCategoryStore();
const authStore = useAuthStore();

// Component state
const currentView = ref<'kanban' | 'list'>('kanban');
const showTaskFilters = ref(false);
const showTaskForm = ref(false);
const showWorkspaceSettings = ref(false);
const showCategoryManagement = ref(false);
const showTaskDetail = ref(false);
const selectedTask = ref<Task | null>(null);

// Filters
const filters = ref({
  search: '',
  status: [] as string[],
  priority: [] as string[],
  assignee: [] as number[]
});

// Computed properties
const workspaceId = computed(() => parseInt(route.params.id as string));
const workspace = computed(() => workspaceStore.currentWorkspace);
const loading = computed(() => workspaceStore.loading || taskStore.loading || categoryStore.loading);
const error = computed(() => workspaceStore.error || taskStore.error || categoryStore.error);

const hasAccess = computed(() => {
  return authStore.canViewWorkspace(workspaceId.value);
});

const canCreateTasks = computed(() => {
  return authStore.canEditTasks(workspaceId.value);
});

const canManageWorkspace = computed(() => {
  return authStore.canManageWorkspace(workspaceId.value);
});

const activeFiltersCount = computed(() => {
  return (filters.value.search ? 1 : 0) +
         filters.value.status.length +
         filters.value.priority.length +
         filters.value.assignee.length;
});

// Filter options
const statusFilterOptions = [
  { title: 'Open', value: 'open' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Review', value: 'review' },
  { title: 'Closed', value: 'closed' },
  { title: 'Blocked', value: 'blocked' }
];

const priorityFilterOptions = [
  { title: 'High', value: 'high' },
  { title: 'Medium', value: 'medium' },
  { title: 'Low', value: 'low' }
];

const assigneeFilterOptions = computed(() => {
  // TODO: Get actual users from workspace
  return [
    { title: 'User 1', value: 1 },
    { title: 'User 2', value: 2 }
  ];
});

// Methods
const loadWorkspace = async () => {
  if (!workspaceId.value) return;

  try {
    await Promise.all([
      workspaceStore.getWorkspace(workspaceId.value),
      taskStore.fetchTasks(workspaceId.value),
      categoryStore.fetchCategories(workspaceId.value),
      authStore.fetchWorkspacePermissions()
    ]);
  } catch (error) {
    console.error('Error loading workspace:', error);
  }
};

const clearFilters = () => {
  filters.value = {
    search: '',
    status: [],
    priority: [],
    assignee: []
  };
};

const openTaskDetail = (task: Task) => {
  selectedTask.value = task;
  showTaskDetail.value = true;
};

const closeTaskDetail = () => {
  selectedTask.value = null;
  showTaskDetail.value = false;
};

const onTaskSaved = () => {
  showTaskForm.value = false;
  // Refresh tasks
  taskStore.fetchTasks(workspaceId.value);
};

const onTaskUpdated = () => {
  // Refresh tasks
  taskStore.fetchTasks(workspaceId.value);
};

const clearError = () => {
  workspaceStore.clearError();
  taskStore.clearError();
  categoryStore.clearError();
};

// Lifecycle
onMounted(() => {
  loadWorkspace();
});

// Watch for route changes
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadWorkspace();
  }
});
</script>

<style scoped>
.workspace-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.loading-container,
.error-container,
.access-denied {
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

.access-denied h2 {
  margin: 16px 0 8px 0;
  color: #666;
}

.access-denied p {
  margin: 0 0 24px 0;
  color: #999;
}

.workspace-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.workspace-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
}

.workspace-info {
  flex: 1;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #666;
}

.current-workspace {
  font-weight: 500;
}

.workspace-title h1 {
  margin: 0 0 4px 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.workspace-description {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

.workspace-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filters-panel {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.main-content {
  flex: 1;
  overflow: hidden;
}

.kanban-view,
.list-view {
  height: 100%;
}

/* Responsive design */
@media (max-width: 768px) {
  .workspace-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .workspace-actions {
    justify-content: space-between;
  }

  .filters-panel .v-row {
    flex-direction: column;
  }
}
</style>