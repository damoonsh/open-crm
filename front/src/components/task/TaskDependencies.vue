<template>
  <v-card class="task-dependencies">
    <v-card-title>
      <div class="dependencies-header">
        <v-icon left>mdi-link</v-icon>
        Task Dependencies
      </div>
    </v-card-title>

    <v-card-text>
      <div v-if="loading" class="text-center pa-4">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <div v-else-if="error" class="error-message">
        <v-alert type="error" dismissible @click:close="clearError">
          {{ error }}
        </v-alert>
      </div>

      <div v-else>
        <!-- Blocked By Section -->
        <div class="dependency-section">
          <div class="section-header">
            <h4>Blocked By</h4>
            <p class="section-description">
              This task cannot be completed until the following tasks are done:
            </p>
          </div>

          <div v-if="blockedByTasks.length === 0" class="empty-state">
            <v-icon color="grey-lighten-2">mdi-check-circle</v-icon>
            <p>No blocking dependencies</p>
          </div>

          <div v-else class="dependency-list">
            <div
              v-for="dependency in blockedByTasks"
              :key="dependency.id"
              class="dependency-item blocked-by"
            >
              <div class="dependency-info">
                <div class="task-title">
                  <v-icon color="warning" size="small">mdi-lock</v-icon>
                  Task #{{ dependency.blocking_task_id }}
                </div>
                <div class="task-details">
                  <v-chip size="x-small" :color="getTaskStatusColor(dependency.blocking_task_id)">
                    {{ getTaskStatus(dependency.blocking_task_id) }}
                  </v-chip>
                  <span class="task-name">{{ getTaskTitle(dependency.blocking_task_id) }}</span>
                </div>
              </div>
              
              <div v-if="canManageDependencies" class="dependency-actions">
                <v-btn
                  icon
                  size="small"
                  @click="removeDependency(dependency.blocking_task_id)"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </div>
            </div>
          </div>

          <!-- Add Blocking Dependency -->
          <div v-if="canManageDependencies" class="add-dependency">
            <v-select
              v-model="newBlockingTask"
              :items="availableBlockingTasks"
              label="Add blocking task"
              clearable
              variant="outlined"
              density="compact"
            />
            <v-btn
              color="primary"
              size="small"
              :disabled="!newBlockingTask"
              @click="addBlockingDependency"
            >
              Add Dependency
            </v-btn>
          </div>
        </div>

        <v-divider class="my-6" />

        <!-- Blocking Section -->
        <div class="dependency-section">
          <div class="section-header">
            <h4>Blocking</h4>
            <p class="section-description">
              The following tasks are waiting for this task to be completed:
            </p>
          </div>

          <div v-if="blockingTasks.length === 0" class="empty-state">
            <v-icon color="grey-lighten-2">mdi-arrow-right</v-icon>
            <p>Not blocking any tasks</p>
          </div>

          <div v-else class="dependency-list">
            <div
              v-for="dependency in blockingTasks"
              :key="dependency.id"
              class="dependency-item blocking"
            >
              <div class="dependency-info">
                <div class="task-title">
                  <v-icon color="info" size="small">mdi-arrow-right</v-icon>
                  Task #{{ dependency.blocked_task_id }}
                </div>
                <div class="task-details">
                  <v-chip size="x-small" :color="getTaskStatusColor(dependency.blocked_task_id)">
                    {{ getTaskStatus(dependency.blocked_task_id) }}
                  </v-chip>
                  <span class="task-name">{{ getTaskTitle(dependency.blocked_task_id) }}</span>
                </div>
              </div>
              
              <div v-if="canManageDependencies" class="dependency-actions">
                <v-btn
                  icon
                  size="small"
                  @click="removeDependency(dependency.blocked_task_id, false)"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <!-- Dependency Validation Warnings -->
        <div v-if="validationWarnings.length > 0" class="validation-warnings">
          <v-alert
            v-for="warning in validationWarnings"
            :key="warning"
            type="warning"
            variant="tonal"
            class="mb-2"
          >
            {{ warning }}
          </v-alert>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTaskStore } from '@/stores/tasks';
import { useAuthStore } from '@/stores/auth';
import type { Task, TaskDependency } from '@/stores/tasks';

interface Props {
  task: Task;
  workspaceId: number;
}

const props = defineProps<Props>();

const taskStore = useTaskStore();
const authStore = useAuthStore();

const newBlockingTask = ref<number | null>(null);
const validationWarnings = ref<string[]>([]);

// Computed properties
const loading = computed(() => taskStore.loading);
const error = computed(() => taskStore.error);

const canManageDependencies = computed(() => {
  return authStore.canEditTasks(props.workspaceId);
});

const blockedByTasks = computed(() => {
  return props.task.blocked_by_dependencies || [];
});

const blockingTasks = computed(() => {
  return props.task.blocking_dependencies || [];
});

const availableBlockingTasks = computed(() => {
  const allTasks = taskStore.tasks.filter(task => 
    task.id !== props.task.id && 
    task.workspace_id === props.workspaceId
  );
  
  const alreadyBlocking = blockedByTasks.value.map(dep => dep.blocking_task_id);
  
  return allTasks
    .filter(task => !alreadyBlocking.includes(task.id))
    .map(task => ({
      title: `#${task.id} - ${task.title}`,
      value: task.id
    }));
});

// Methods
const getTaskTitle = (taskId: number): string => {
  const task = taskStore.getTaskById(taskId);
  return task?.title || 'Unknown Task';
};

const getTaskStatus = (taskId: number): string => {
  const task = taskStore.getTaskById(taskId);
  return task?.status || 'unknown';
};

const getTaskStatusColor = (taskId: number): string => {
  const status = getTaskStatus(taskId);
  const colors: Record<string, string> = {
    open: 'blue',
    in_progress: 'orange',
    review: 'purple',
    closed: 'green',
    blocked: 'red'
  };
  return colors[status] || 'grey';
};

const addBlockingDependency = async () => {
  if (!newBlockingTask.value || !canManageDependencies.value) return;

  try {
    // Check for circular dependencies
    if (await wouldCreateCircularDependency(newBlockingTask.value, props.task.id)) {
      validationWarnings.value.push(
        'Cannot add this dependency as it would create a circular reference.'
      );
      return;
    }

    await taskStore.addTaskDependency(props.task.id, newBlockingTask.value);
    newBlockingTask.value = null;
    validationWarnings.value = [];
    
    // Refresh task data
    await taskStore.fetchTasks(props.workspaceId);
  } catch (error) {
    console.error('Error adding dependency:', error);
  }
};

const removeDependency = async (otherTaskId: number, isBlocking: boolean = true) => {
  if (!canManageDependencies.value) return;

  try {
    if (isBlocking) {
      // Remove blocking dependency (otherTaskId blocks this task)
      await taskStore.removeTaskDependency(props.task.id, otherTaskId);
    } else {
      // Remove blocked dependency (this task blocks otherTaskId)
      await taskStore.removeTaskDependency(otherTaskId, props.task.id);
    }
    
    validationWarnings.value = [];
    
    // Refresh task data
    await taskStore.fetchTasks(props.workspaceId);
  } catch (error) {
    console.error('Error removing dependency:', error);
  }
};

const wouldCreateCircularDependency = async (blockingTaskId: number, blockedTaskId: number): Promise<boolean> => {
  // Simple circular dependency check
  // In a real implementation, this would do a more thorough graph traversal
  const blockingTask = taskStore.getTaskById(blockingTaskId);
  if (!blockingTask) return false;

  // Check if the blocking task is already blocked by the current task
  const blockingTaskDeps = blockingTask.blocked_by_dependencies || [];
  return blockingTaskDeps.some(dep => dep.blocking_task_id === blockedTaskId);
};

const clearError = () => {
  taskStore.clearError();
};

// Lifecycle
onMounted(() => {
  // Ensure we have all task data
  taskStore.fetchTasks(props.workspaceId);
});
</script>

<style scoped>
.dependencies-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dependency-section {
  margin-bottom: 24px;
}

.section-header h4 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.section-description {
  margin: 0 0 16px 0;
  color: #666;
  font-size: 0.9rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  text-align: center;
  color: #999;
}

.empty-state p {
  margin: 8px 0 0 0;
}

.dependency-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dependency-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.dependency-item.blocked-by {
  border-left: 4px solid #ff9800;
}

.dependency-item.blocking {
  border-left: 4px solid #2196f3;
}

.dependency-info {
  flex: 1;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 4px;
}

.task-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-name {
  color: #666;
  font-size: 0.9rem;
}

.dependency-actions {
  display: flex;
  gap: 4px;
}

.add-dependency {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-top: 16px;
}

.add-dependency .v-select {
  flex: 1;
}

.validation-warnings {
  margin-top: 16px;
}

.error-message {
  margin-bottom: 16px;
}
</style>