<template>
  <v-card
    class="task-list-item"
    :class="{ 'high-priority': task.priority === 'high' }"
    @click="$emit('click')"
  >
    <v-card-text class="task-content">
      <div class="task-main">
        <!-- Priority Indicator -->
        <div class="priority-indicator" :class="`priority-${task.priority}`"></div>
        
        <!-- Task Info -->
        <div class="task-info">
          <div class="task-header">
            <h4 class="task-title">{{ task.title }}</h4>
            <div class="task-meta">
              <v-chip size="x-small" :color="getStatusColor(task.status)">
                {{ formatStatus(task.status) }}
              </v-chip>
              <v-chip size="x-small" :color="getPriorityColor(task.priority)">
                {{ formatPriority(task.priority) }}
              </v-chip>
            </div>
          </div>
          
          <p v-if="task.description" class="task-description">
            {{ truncatedDescription }}
          </p>
          
          <!-- Task Details -->
          <div class="task-details">
            <div class="detail-item">
              <v-icon size="small">mdi-calendar</v-icon>
              <span>{{ formatDate(task.created_at) }}</span>
            </div>
            
            <div v-if="task.story_points" class="detail-item">
              <v-icon size="small">mdi-numeric</v-icon>
              <span>{{ task.story_points }} pts</span>
            </div>
            
            <div v-if="task.assignee_id" class="detail-item">
              <v-icon size="small">mdi-account</v-icon>
              <span>{{ getAssigneeName(task.assignee_id) }}</span>
            </div>
            
            <div v-if="hasDependencies" class="detail-item">
              <v-icon size="small" color="warning">mdi-link</v-icon>
              <span>{{ dependencyCount }} deps</span>
            </div>
          </div>
          
          <!-- Labels -->
          <div v-if="task.labels && task.labels.length > 0" class="task-labels">
            <v-chip
              v-for="label in task.labels.slice(0, 3)"
              :key="label"
              size="x-small"
              variant="outlined"
              class="task-label"
            >
              {{ label }}
            </v-chip>
            <span v-if="task.labels.length > 3" class="more-labels">
              +{{ task.labels.length - 3 }} more
            </span>
          </div>
        </div>
      </div>
      
      <!-- Task Actions -->
      <div class="task-actions">
        <v-btn
          icon
          size="small"
          variant="text"
          @click.stop="$emit('edit', task)"
        >
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
        
        <v-menu>
          <template #activator="{ props: menuProps }">
            <v-btn
              icon
              size="small"
              variant="text"
              v-bind="menuProps"
              @click.stop
            >
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="$emit('duplicate', task)">
              <v-list-item-title>Duplicate</v-list-item-title>
            </v-list-item>
            <v-list-item @click="$emit('move', task)">
              <v-list-item-title>Move to workspace</v-list-item-title>
            </v-list-item>
            <v-divider />
            <v-list-item @click="$emit('delete', task)" class="text-error">
              <v-list-item-title>Delete</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Task } from '@/stores/tasks';

interface Props {
  task: Task;
}

interface Emits {
  (e: 'click'): void;
  (e: 'edit', task: Task): void;
  (e: 'duplicate', task: Task): void;
  (e: 'move', task: Task): void;
  (e: 'delete', task: Task): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Computed properties
const truncatedDescription = computed(() => {
  if (!props.task.description) return '';
  return props.task.description.length > 150
    ? props.task.description.substring(0, 150) + '...'
    : props.task.description;
});

const hasDependencies = computed(() => {
  return (props.task.blocking_dependencies && props.task.blocking_dependencies.length > 0) ||
         (props.task.blocked_by_dependencies && props.task.blocked_by_dependencies.length > 0);
});

const dependencyCount = computed(() => {
  const blocking = props.task.blocking_dependencies?.length || 0;
  const blockedBy = props.task.blocked_by_dependencies?.length || 0;
  return blocking + blockedBy;
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
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'Today';
  if (diffDays === 2) return 'Yesterday';
  if (diffDays <= 7) return `${diffDays} days ago`;
  
  return date.toLocaleDateString();
};

const getAssigneeName = (assigneeId: number): string => {
  // TODO: Get actual user name from user store
  return `User ${assigneeId}`;
};
</script>

<style scoped>
.task-list-item {
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid transparent;
  margin-bottom: 8px;
}

.task-list-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.task-list-item.high-priority {
  border-left-color: #f44336;
}

.task-content {
  padding: 16px !important;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.task-main {
  display: flex;
  flex: 1;
  gap: 12px;
}

.priority-indicator {
  width: 4px;
  height: 60px;
  border-radius: 2px;
  flex-shrink: 0;
}

.priority-high {
  background-color: #f44336;
}

.priority-medium {
  background-color: #ff9800;
}

.priority-low {
  background-color: #4caf50;
}

.task-info {
  flex: 1;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.task-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.3;
  color: #333;
  flex: 1;
  margin-right: 12px;
}

.task-meta {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.task-description {
  margin: 0 0 12px 0;
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

.task-details {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: #666;
}

.task-labels {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.task-label {
  font-size: 0.7rem !important;
}

.more-labels {
  font-size: 0.75rem;
  color: #666;
}

.task-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .task-content {
    flex-direction: column;
    gap: 12px;
  }

  .task-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .task-title {
    margin-right: 0;
  }

  .task-details {
    gap: 12px;
  }

  .task-actions {
    flex-direction: row;
    align-self: flex-end;
  }
}
</style>