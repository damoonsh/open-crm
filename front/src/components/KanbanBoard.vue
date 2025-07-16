<template>
  <div class="kanban-board">
    <!-- Board Header -->
    <div class="board-header">
      <div class="board-title">
        <h2>{{ workspace?.name || 'Kanban Board' }}</h2>
        <v-chip v-if="totalTasks > 0" size="small" variant="outlined">
          {{ totalTasks }} tasks
        </v-chip>
      </div>
      
      <div class="board-actions">
        <!-- Filters -->
        <v-menu>
          <template #activator="{ props: menuProps }">
            <v-btn variant="outlined" v-bind="menuProps">
              <v-icon left>mdi-filter</v-icon>
              Filters
              <v-badge v-if="activeFiltersCount > 0" :content="activeFiltersCount" color="primary" />
            </v-btn>
          </template>
          <v-card min-width="300">
            <v-card-title>Filter Tasks</v-card-title>
            <v-card-text>
              <v-select
                v-model="filters.assignee"
                :items="assigneeOptions"
                label="Assignee"
                clearable
                multiple
                chips
              />
              <v-select
                v-model="filters.priority"
                :items="priorityOptions"
                label="Priority"
                clearable
                multiple
                chips
              />
              <v-select
                v-model="filters.labels"
                :items="labelOptions"
                label="Labels"
                clearable
                multiple
                chips
              />
            </v-card-text>
            <v-card-actions>
              <v-btn @click="clearFilters">Clear All</v-btn>
              <v-spacer />
              <v-btn color="primary" @click="applyFilters">Apply</v-btn>
            </v-card-actions>
          </v-card>
        </v-menu>

        <!-- Search -->
        <v-text-field
          v-model="searchQuery"
          placeholder="Search tasks..."
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 250px;"
        >
          <template #prepend-inner>
            <v-icon>mdi-magnify</v-icon>
          </template>
        </v-text-field>

        <!-- Board Settings -->
        <v-menu v-if="canManageWorkspace">
          <template #activator="{ props: menuProps }">
            <v-btn icon v-bind="menuProps">
              <v-icon>mdi-cog</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="showCategorySettings = true">
              <v-list-item-title>Category Settings</v-list-item-title>
            </v-list-item>
            <v-list-item @click="showWorkspaceSettings = true">
              <v-list-item-title>Workspace Settings</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p>Loading kanban board...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <v-alert type="error" dismissible @click:close="clearError">
        {{ error }}
      </v-alert>
    </div>

    <!-- Empty State -->
    <div v-else-if="categories.length === 0" class="empty-state">
      <v-icon size="96" color="grey-lighten-2">mdi-view-column</v-icon>
      <h3>No Categories Yet</h3>
      <p>Create your first category to start organizing tasks</p>
      <v-btn
        v-if="canManageWorkspace"
        color="primary"
        @click="showCreateCategory = true"
      >
        Create Category
      </v-btn>
    </div>

    <!-- Kanban Columns -->
    <div v-else class="kanban-columns">
      <CategoryColumn
        v-for="category in visibleCategories"
        :key="category.id"
        :category="category"
        :tasks="getTasksForCategory(category.id)"
        :workspace-id="workspaceId"
        @edit-category="editCategory"
        @delete-category="deleteCategory"
        @task-click="openTaskDetail"
        @task-moved="onTaskMoved"
      />
      
      <!-- Add Category Column -->
      <div v-if="canManageWorkspace" class="add-category-column">
        <v-btn
          variant="outlined"
          size="large"
          @click="showCreateCategory = true"
          class="add-category-btn"
        >
          <v-icon left>mdi-plus</v-icon>
          Add Category
        </v-btn>
      </div>
    </div>

    <!-- Real-time Updates Indicator -->
    <div v-if="isConnected" class="connection-status connected">
      <v-icon size="small">mdi-wifi</v-icon>
      Live
    </div>
    <div v-else class="connection-status disconnected">
      <v-icon size="small">mdi-wifi-off</v-icon>
      Offline
    </div>

    <!-- Category Form Dialog -->
    <CategoryForm
      v-model="showCreateCategory"
      :category="selectedCategory"
      :workspace-id="workspaceId"
      @saved="onCategorySaved"
      @cancelled="onCategoryFormCancelled"
    />

    <!-- Category Settings Dialog -->
    <v-dialog v-model="showCategorySettings" max-width="800">
      <CategorySettings :workspace-id="workspaceId" />
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

    <!-- Delete Category Confirmation -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Category</v-card-title>
        <v-card-text>
          Are you sure you want to delete "{{ categoryToDelete?.name }}"?
          This will also delete all {{ getTasksForCategory(categoryToDelete?.id || 0).length }} tasks in this category.
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="confirmDeleteCategory">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useCategoryStore } from '@/stores/categories';
import { useTaskStore } from '@/stores/tasks';
import { useWorkspaceStore } from '@/stores/workspace';
import { useAuthStore } from '@/stores/auth';
import CategoryColumn from '@/components/category/CategoryColumn.vue';
import CategoryForm from '@/components/category/CategoryForm.vue';
import CategorySettings from '@/components/category/CategorySettings.vue';
import TaskDetails from '@/components/task/TaskDetails.vue';
import type { Category } from '@/stores/categories';
import type { Task } from '@/stores/tasks';

interface Props {
  workspaceId: number;
}

const props = defineProps<Props>();

const categoryStore = useCategoryStore();
const taskStore = useTaskStore();
const workspaceStore = useWorkspaceStore();
const authStore = useAuthStore();

// Dialog states
const showCreateCategory = ref(false);
const showCategorySettings = ref(false);
const showWorkspaceSettings = ref(false);
const showTaskDetail = ref(false);
const showDeleteDialog = ref(false);

// Selected items
const selectedCategory = ref<Category | null>(null);
const selectedTask = ref<Task | null>(null);
const categoryToDelete = ref<Category | null>(null);

// Filters and search
const searchQuery = ref('');
const filters = ref({
  assignee: [] as number[],
  priority: [] as string[],
  labels: [] as string[]
});

// Real-time connection status
const isConnected = ref(true);
const connectionCheckInterval = ref<NodeJS.Timeout | null>(null);

// Computed properties
const categories = computed(() => categoryStore.categories.filter(cat => !cat.is_archived));
const tasks = computed(() => taskStore.tasks);
const workspace = computed(() => workspaceStore.currentWorkspace);
const loading = computed(() => categoryStore.loading || taskStore.loading);
const error = computed(() => categoryStore.error || taskStore.error);

const canManageWorkspace = computed(() => {
  return authStore.canManageWorkspace(props.workspaceId);
});

const totalTasks = computed(() => tasks.value.length);

const visibleCategories = computed(() => {
  return categories.value.sort((a, b) => a.position - b.position);
});

const filteredTasks = computed(() => {
  let filtered = tasks.value;

  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(task =>
      task.title.toLowerCase().includes(query) ||
      task.description.toLowerCase().includes(query)
    );
  }

  // Apply assignee filter
  if (filters.value.assignee.length > 0) {
    filtered = filtered.filter(task =>
      task.assignee_id && filters.value.assignee.includes(task.assignee_id)
    );
  }

  // Apply priority filter
  if (filters.value.priority.length > 0) {
    filtered = filtered.filter(task =>
      filters.value.priority.includes(task.priority)
    );
  }

  // Apply labels filter
  if (filters.value.labels.length > 0) {
    filtered = filtered.filter(task =>
      task.labels && task.labels.some(label =>
        filters.value.labels.includes(label)
      )
    );
  }

  return filtered;
});

const activeFiltersCount = computed(() => {
  return filters.value.assignee.length +
         filters.value.priority.length +
         filters.value.labels.length +
         (searchQuery.value.trim() ? 1 : 0);
});

// Filter options
const assigneeOptions = computed(() => {
  const assignees = new Set<number>();
  tasks.value.forEach(task => {
    if (task.assignee_id) assignees.add(task.assignee_id);
  });
  
  return Array.from(assignees).map(id => ({
    title: `User ${id}`, // TODO: Get actual user names
    value: id
  }));
});

const priorityOptions = [
  { title: 'High', value: 'high' },
  { title: 'Medium', value: 'medium' },
  { title: 'Low', value: 'low' }
];

const labelOptions = computed(() => {
  const labels = new Set<string>();
  tasks.value.forEach(task => {
    if (task.labels) {
      task.labels.forEach(label => labels.add(label));
    }
  });
  
  return Array.from(labels).map(label => ({
    title: label,
    value: label
  }));
});

// Methods
const getTasksForCategory = (categoryId: number): Task[] => {
  return filteredTasks.value.filter(task => task.category_id === categoryId);
};

const editCategory = (category: Category) => {
  selectedCategory.value = category;
  showCreateCategory.value = true;
};

const deleteCategory = (category: Category) => {
  categoryToDelete.value = category;
  showDeleteDialog.value = true;
};

const confirmDeleteCategory = async () => {
  if (categoryToDelete.value) {
    await categoryStore.deleteCategory(categoryToDelete.value.id);
    showDeleteDialog.value = false;
    categoryToDelete.value = null;
  }
};

const openTaskDetail = (task: Task) => {
  selectedTask.value = task;
  showTaskDetail.value = true;
};

const closeTaskDetail = () => {
  selectedTask.value = null;
  showTaskDetail.value = false;
};

const onTaskMoved = (task: Task, targetCategoryId: number) => {
  // Task has already been moved by CategoryColumn
  // This is just for any additional handling if needed
  console.log(`Task ${task.id} moved to category ${targetCategoryId}`);
};

const onTaskUpdated = () => {
  // Refresh tasks after update
  taskStore.fetchTasks(props.workspaceId);
};

const onCategorySaved = () => {
  showCreateCategory.value = false;
  selectedCategory.value = null;
  categoryStore.fetchCategories(props.workspaceId);
};

const onCategoryFormCancelled = () => {
  showCreateCategory.value = false;
  selectedCategory.value = null;
};

const clearFilters = () => {
  filters.value = {
    assignee: [],
    priority: [],
    labels: []
  };
  searchQuery.value = '';
};

const applyFilters = () => {
  // Filters are applied automatically via computed properties
  // This method is here for future enhancements
};

const clearError = () => {
  categoryStore.clearError();
  taskStore.clearError();
};

const checkConnection = () => {
  // Simple connection check - in a real app, this would ping the server
  isConnected.value = navigator.onLine;
};

// Lifecycle
onMounted(async () => {
  // Load initial data
  await Promise.all([
    categoryStore.fetchCategories(props.workspaceId),
    taskStore.fetchTasks(props.workspaceId),
    workspaceStore.getWorkspace(props.workspaceId)
  ]);

  // Set up connection monitoring
  connectionCheckInterval.value = setInterval(checkConnection, 5000);
  window.addEventListener('online', checkConnection);
  window.addEventListener('offline', checkConnection);
});

onUnmounted(() => {
  if (connectionCheckInterval.value) {
    clearInterval(connectionCheckInterval.value);
  }
  window.removeEventListener('online', checkConnection);
  window.removeEventListener('offline', checkConnection);
});

// Watch for workspace changes
watch(() => props.workspaceId, async (newWorkspaceId) => {
  if (newWorkspaceId) {
    await Promise.all([
      categoryStore.fetchCategories(newWorkspaceId),
      taskStore.fetchTasks(newWorkspaceId),
      workspaceStore.getWorkspace(newWorkspaceId)
    ]);
  }
});
</script>

<style scoped>
.kanban-board {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  position: relative;
}

.board-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.board-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.board-title h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.board-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 48px;
  text-align: center;
}

.empty-state h3 {
  margin: 16px 0 8px 0;
  color: #666;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #999;
}

.kanban-columns {
  display: flex;
  gap: 16px;
  padding: 24px;
  overflow-x: auto;
  flex: 1;
  align-items: flex-start;
}

.add-category-column {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 300px;
  height: 200px;
}

.add-category-btn {
  width: 100%;
  height: 100px;
  border: 2px dashed #ccc;
  border-radius: 8px;
}

.connection-status {
  position: fixed;
  bottom: 16px;
  right: 16px;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 1000;
}

.connection-status.connected {
  background: #4caf50;
  color: white;
}

.connection-status.disconnected {
  background: #f44336;
  color: white;
}

/* Responsive design */
@media (max-width: 768px) {
  .board-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .board-actions {
    justify-content: space-between;
  }

  .kanban-columns {
    padding: 16px;
    gap: 12px;
  }
}

/* Scrollbar styling */
.kanban-columns::-webkit-scrollbar {
  height: 8px;
}

.kanban-columns::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.kanban-columns::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.kanban-columns::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>