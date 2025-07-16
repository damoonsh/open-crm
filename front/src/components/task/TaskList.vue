<template>
  <div class="task-list">
    <div v-if="loading" class="text-center pa-4">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="error" class="error-message">
      <v-alert type="error" dismissible @click:close="clearError">
        {{ error }}
      </v-alert>
    </div>

    <div v-else>
      <!-- List Header -->
      <div class="list-header">
        <div class="list-controls">
          <v-select
            v-model="sortBy"
            :items="sortOptions"
            label="Sort by"
            variant="outlined"
            density="compact"
            hide-details
            style="max-width: 200px;"
          />
          
          <v-select
            v-model="groupBy"
            :items="groupOptions"
            label="Group by"
            variant="outlined"
            density="compact"
            hide-details
            style="max-width: 200px;"
          />
        </div>
        
        <div class="list-stats">
          <v-chip size="small" variant="outlined">
            {{ filteredTasks.length }} tasks
          </v-chip>
        </div>
      </div>

      <!-- Task Groups -->
      <div v-if="groupBy !== 'none'" class="grouped-tasks">
        <div
          v-for="group in groupedTasks"
          :key="group.key"
          class="task-group"
        >
          <div class="group-header">
            <h3 class="group-title">
              <v-icon v-if="group.icon" left>{{ group.icon }}</v-icon>
              {{ group.title }}
            </h3>
            <v-chip size="small" variant="outlined">
              {{ group.tasks.length }}
            </v-chip>
          </div>
          
          <div class="group-tasks">
            <TaskListItem
              v-for="task in group.tasks"
              :key="task.id"
              :task="task"
              @click="$emit('task-click', task)"
            />
          </div>
        </div>
      </div>

      <!-- Ungrouped Tasks -->
      <div v-else class="ungrouped-tasks">
        <TaskListItem
          v-for="task in sortedTasks"
          :key="task.id"
          :task="task"
          @click="$emit('task-click', task)"
        />
      </div>

      <!-- Empty State -->
      <div v-if="filteredTasks.length === 0" class="empty-state">
        <v-icon size="64" color="grey-lighten-2">mdi-clipboard-text-outline</v-icon>
        <h3>No tasks found</h3>
        <p v-if="hasActiveFilters">Try adjusting your filters to see more tasks</p>
        <p v-else>Create your first task to get started</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useTaskStore } from '@/stores/tasks';
import { useCategoryStore } from '@/stores/categories';
import TaskListItem from './TaskListItem.vue';
import type { Task } from '@/stores/tasks';

interface Props {
  workspaceId: number;
  filters: {
    search: string;
    status: string[];
    priority: string[];
    assignee: number[];
  };
}

interface Emits {
  (e: 'task-click', task: Task): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const taskStore = useTaskStore();
const categoryStore = useCategoryStore();

const sortBy = ref('created_desc');
const groupBy = ref<'none' | 'status' | 'priority' | 'category' | 'assignee'>('none');

// Computed properties
const tasks = computed(() => taskStore.tasks);
const loading = computed(() => taskStore.loading);
const error = computed(() => taskStore.error);

const hasActiveFilters = computed(() => {
  return props.filters.search ||
         props.filters.status.length > 0 ||
         props.filters.priority.length > 0 ||
         props.filters.assignee.length > 0;
});

const filteredTasks = computed(() => {
  let filtered = tasks.value.filter(task => task.workspace_id === props.workspaceId);

  // Apply search filter
  if (props.filters.search) {
    const query = props.filters.search.toLowerCase();
    filtered = filtered.filter(task =>
      task.title.toLowerCase().includes(query) ||
      task.description.toLowerCase().includes(query)
    );
  }

  // Apply status filter
  if (props.filters.status.length > 0) {
    filtered = filtered.filter(task =>
      props.filters.status.includes(task.status)
    );
  }

  // Apply priority filter
  if (props.filters.priority.length > 0) {
    filtered = filtered.filter(task =>
      props.filters.priority.includes(task.priority)
    );
  }

  // Apply assignee filter
  if (props.filters.assignee.length > 0) {
    filtered = filtered.filter(task =>
      task.assignee_id && props.filters.assignee.includes(task.assignee_id)
    );
  }

  return filtered;
});

const sortedTasks = computed(() => {
  const sorted = [...filteredTasks.value];
  
  switch (sortBy.value) {
    case 'title_asc':
      return sorted.sort((a, b) => a.title.localeCompare(b.title));
    case 'title_desc':
      return sorted.sort((a, b) => b.title.localeCompare(a.title));
    case 'created_asc':
      return sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    case 'created_desc':
      return sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    case 'updated_asc':
      return sorted.sort((a, b) => new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime());
    case 'updated_desc':
      return sorted.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
    case 'priority':
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return sorted.sort((a, b) => (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0));
    default:
      return sorted;
  }
});

const groupedTasks = computed(() => {
  if (groupBy.value === 'none') return [];

  const groups = new Map<string, Task[]>();
  
  filteredTasks.value.forEach(task => {
    let groupKey = '';
    
    switch (groupBy.value) {
      case 'status':
        groupKey = task.status;
        break;
      case 'priority':
        groupKey = task.priority;
        break;
      case 'category':
        groupKey = task.category_id?.toString() || 'uncategorized';
        break;
      case 'assignee':
        groupKey = task.assignee_id?.toString() || 'unassigned';
        break;
    }
    
    if (!groups.has(groupKey)) {
      groups.set(groupKey, []);
    }
    groups.get(groupKey)!.push(task);
  });

  return Array.from(groups.entries()).map(([key, tasks]) => ({
    key,
    title: getGroupTitle(groupBy.value, key),
    icon: getGroupIcon(groupBy.value, key),
    tasks: sortTasksInGroup(tasks)
  })).sort((a, b) => getGroupOrder(groupBy.value, a.key) - getGroupOrder(groupBy.value, b.key));
});

// Options
const sortOptions = [
  { title: 'Created (Newest)', value: 'created_desc' },
  { title: 'Created (Oldest)', value: 'created_asc' },
  { title: 'Updated (Newest)', value: 'updated_desc' },
  { title: 'Updated (Oldest)', value: 'updated_asc' },
  { title: 'Title (A-Z)', value: 'title_asc' },
  { title: 'Title (Z-A)', value: 'title_desc' },
  { title: 'Priority', value: 'priority' }
];

const groupOptions = [
  { title: 'None', value: 'none' },
  { title: 'Status', value: 'status' },
  { title: 'Priority', value: 'priority' },
  { title: 'Category', value: 'category' },
  { title: 'Assignee', value: 'assignee' }
];

// Methods
const getGroupTitle = (groupType: string, key: string): string => {
  switch (groupType) {
    case 'status':
      return key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    case 'priority':
      return key.charAt(0).toUpperCase() + key.slice(1) + ' Priority';
    case 'category':
      if (key === 'uncategorized') return 'Uncategorized';
      const category = categoryStore.categories.find(cat => cat.id.toString() === key);
      return category?.name || 'Unknown Category';
    case 'assignee':
      if (key === 'unassigned') return 'Unassigned';
      return `User ${key}`; // TODO: Get actual user names
    default:
      return key;
  }
};

const getGroupIcon = (groupType: string, key: string): string => {
  switch (groupType) {
    case 'status':
      const statusIcons: Record<string, string> = {
        open: 'mdi-circle-outline',
        in_progress: 'mdi-play-circle',
        review: 'mdi-eye-circle',
        closed: 'mdi-check-circle',
        blocked: 'mdi-block-helper'
      };
      return statusIcons[key] || 'mdi-help-circle';
    case 'priority':
      const priorityIcons: Record<string, string> = {
        high: 'mdi-arrow-up',
        medium: 'mdi-minus',
        low: 'mdi-arrow-down'
      };
      return priorityIcons[key] || 'mdi-minus';
    case 'category':
      return key === 'uncategorized' ? 'mdi-folder-outline' : 'mdi-folder';
    case 'assignee':
      return key === 'unassigned' ? 'mdi-account-outline' : 'mdi-account';
    default:
      return 'mdi-folder';
  }
};

const getGroupOrder = (groupType: string, key: string): number => {
  switch (groupType) {
    case 'status':
      const statusOrder: Record<string, number> = {
        open: 1,
        in_progress: 2,
        review: 3,
        blocked: 4,
        closed: 5
      };
      return statusOrder[key] || 999;
    case 'priority':
      const priorityOrder: Record<string, number> = {
        high: 1,
        medium: 2,
        low: 3
      };
      return priorityOrder[key] || 999;
    default:
      return 0;
  }
};

const sortTasksInGroup = (tasks: Task[]): Task[] => {
  return [...tasks].sort((a, b) => {
    // Sort by priority first, then by created date
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    const aPriority = priorityOrder[a.priority] || 0;
    const bPriority = priorityOrder[b.priority] || 0;
    
    if (aPriority !== bPriority) {
      return bPriority - aPriority;
    }
    
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
};

const clearError = () => {
  taskStore.clearError();
};

// Watch for workspace changes
watch(() => props.workspaceId, () => {
  taskStore.fetchTasks(props.workspaceId);
});
</script>

<style scoped>
.task-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  background: white;
  flex-shrink: 0;
}

.list-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.list-stats {
  display: flex;
  align-items: center;
}

.grouped-tasks,
.ungrouped-tasks {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

.task-group {
  margin-bottom: 32px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.group-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.group-tasks {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

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
  margin: 0;
  color: #999;
}

.error-message {
  margin: 16px 24px;
}

/* Responsive design */
@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .list-controls {
    flex-direction: column;
    gap: 12px;
  }

  .grouped-tasks,
  .ungrouped-tasks {
    padding: 12px 16px;
  }
}
</style>