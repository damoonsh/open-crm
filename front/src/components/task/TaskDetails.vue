<template>
  <v-card class="task-details">
    <v-card-title class="task-details-header">
      <div class="task-title-section">
        <h3>{{ task.title }}</h3>
        <v-chip :color="getStatusColor(task.status)" size="small">
          {{ formatStatus(task.status) }}
        </v-chip>
      </div>
      <v-btn icon @click="$emit('closed')">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text class="task-details-content">
      <div class="task-info-grid">
        <!-- Basic Information -->
        <div class="info-section">
          <h4>Description</h4>
          <p class="task-description">{{ task.description || 'No description provided' }}</p>
        </div>

        <!-- Task Properties -->
        <div class="info-section">
          <h4>Properties</h4>
          <div class="property-list">
            <div class="property-item">
              <span class="property-label">Priority:</span>
              <v-chip :color="getPriorityColor(task.priority)" size="small">
                {{ formatPriority(task.priority) }}
              </v-chip>
            </div>
            
            <div class="property-item">
              <span class="property-label">Story Points:</span>
              <span>{{ task.story_points || 'Not set' }}</span>
            </div>
            
            <div class="property-item">
              <span class="property-label">Assignee:</span>
              <span>{{ task.assignee_id ? `User ${task.assignee_id}` : 'Unassigned' }}</span>
            </div>
            
            <div class="property-item">
              <span class="property-label">Reporter:</span>
              <span>{{ task.reporter_id ? `User ${task.reporter_id}` : 'Unknown' }}</span>
            </div>
            
            <div class="property-item">
              <span class="property-label">Created:</span>
              <span>{{ formatDate(task.created_at) }}</span>
            </div>
            
            <div class="property-item">
              <span class="property-label">Updated:</span>
              <span>{{ formatDate(task.updated_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Labels -->
        <div v-if="task.labels && task.labels.length > 0" class="info-section">
          <h4>Labels</h4>
          <div class="labels-list">
            <v-chip
              v-for="label in task.labels"
              :key="label"
              size="small"
              variant="outlined"
            >
              {{ label }}
            </v-chip>
          </div>
        </div>

        <!-- Dependencies -->
        <div v-if="hasDependencies" class="info-section">
          <h4>Dependencies</h4>
          
          <div v-if="task.blocked_by_dependencies && task.blocked_by_dependencies.length > 0" class="dependency-group">
            <h5>Blocked by:</h5>
            <div class="dependency-list">
              <v-chip
                v-for="depId in task.blocked_by_dependencies"
                :key="depId"
                size="small"
                color="warning"
                variant="outlined"
              >
                Task #{{ depId }}
              </v-chip>
            </div>
          </div>
          
          <div v-if="task.blocking_dependencies && task.blocking_dependencies.length > 0" class="dependency-group">
            <h5>Blocking:</h5>
            <div class="dependency-list">
              <v-chip
                v-for="depId in task.blocking_dependencies"
                :key="depId"
                size="small"
                color="info"
                variant="outlined"
              >
                Task #{{ depId }}
              </v-chip>
            </div>
          </div>
        </div>
      </div>
    </v-card-text>

    <v-card-actions>
      <v-btn
        v-if="canEditTasks"
        color="primary"
        @click="editTask"
      >
        Edit Task
      </v-btn>
      <v-spacer />
      <v-btn @click="$emit('closed')">Close</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import type { Task } from '@/stores/tasks';

interface Props {
  task: Task;
  workspaceId: number;
}

interface Emits {
  (e: 'updated'): void;
  (e: 'closed'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const authStore = useAuthStore();

// Computed properties
const canEditTasks = computed(() => {
  return authStore.canEditTasks(props.workspaceId);
});

const hasDependencies = computed(() => {
  return (props.task.blocking_dependencies && props.task.blocking_dependencies.length > 0) ||
         (props.task.blocked_by_dependencies && props.task.blocked_by_dependencies.length > 0);
});

// Methods
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

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString();
};

const editTask = () => {
  // TODO: Implement task editing
  console.log('Edit task:', props.task.id);
};
</script>

<style scoped>
.task-details {
  max-height: 80vh;
  overflow-y: auto;
}

.task-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.task-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-title-section h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.task-details-content {
  padding: 24px;
}

.task-info-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-section h4 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.task-description {
  margin: 0;
  line-height: 1.6;
  color: #666;
  white-space: pre-wrap;
}

.property-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.property-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.property-label {
  font-weight: 500;
  min-width: 100px;
  color: #666;
}

.labels-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.dependency-group {
  margin-bottom: 16px;
}

.dependency-group h5 {
  margin: 0 0 8px 0;
  font-size: 0.95rem;
  font-weight: 500;
  color: #666;
}

.dependency-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .task-details-header {
    padding: 12px 16px;
  }
  
  .task-details-content {
    padding: 16px;
  }
  
  .task-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .property-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .property-label {
    min-width: auto;
  }
}
</style>