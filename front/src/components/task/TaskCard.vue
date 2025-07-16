<template>
  <v-card
    class="task-card"
    :class="{ 'task-card--dragging': isDragging }"
    :draggable="draggable"
    @dragstart="onDragStart"
    @dragend="onDragEnd"
    @click="$emit('click')"
  >
    <v-card-text class="task-card-content">
      <!-- Priority Indicator -->
      <div class="task-priority" :class="`priority-${task.priority}`"></div>
      
      <!-- Task Title -->
      <h4 class="task-title">{{ task.title }}</h4>
      
      <!-- Task Description (truncated) -->
      <p v-if="task.description" class="task-description">
        {{ truncatedDescription }}
      </p>
      
      <!-- Task Meta Information -->
      <div class="task-meta">
        <!-- Status Badge -->
        <v-chip size="x-small" :color="getStatusColor(task.status)">
          {{ formatStatus(task.status) }}
        </v-chip>
        
        <!-- Story Points -->
        <v-chip v-if="task.story_points" size="x-small" variant="outlined">
          {{ task.story_points }} pts
        </v-chip>
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
      
      <!-- Task Footer -->
      <div class="task-footer">
        <!-- Assignee Avatar -->
        <div v-if="task.assignee_id" class="assignee-avatar">
          <v-avatar size="24">
            <v-icon>mdi-account</v-icon>
          </v-avatar>
        </div>
        
        <!-- Dependencies Indicator -->
        <div v-if="hasDependencies" class="dependencies-indicator">
          <v-icon size="16" color="warning">mdi-link</v-icon>
        </div>
        
        <!-- Created Date -->
        <span class="task-date">{{ formatDate(task.created_at) }}</span>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Task } from '@/stores/tasks';

interface Props {
  task: Task;
  draggable?: boolean;
}

interface Emits {
  (e: 'click'): void;
  (e: 'dragstart', event: DragEvent): void;
}

const props = withDefaults(defineProps<Props>(), {
  draggable: true
});

const emit = defineEmits<Emits>();

const isDragging = ref(false);

// Computed properties
const truncatedDescription = computed(() => {
  if (!props.task.description) return '';
  return props.task.description.length > 100
    ? props.task.description.substring(0, 100) + '...'
    : props.task.description;
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

const formatStatus = (status: string): string => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
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

const onDragStart = (event: DragEvent) => {
  if (!props.draggable) {
    event.preventDefault();
    return;
  }
  
  isDragging.value = true;
  emit('dragstart', event);
};

const onDragEnd = () => {
  isDragging.value = false;
};
</script>

<style scoped>
.task-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid transparent;
  margin-bottom: 8px;
}

.task-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.task-card--dragging {
  opacity: 0.5;
  transform: rotate(5deg);
}

.task-card-content {
  padding: 12px !important;
  position: relative;
}

.task-priority {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  border-radius: 0 2px 2px 0;
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

.task-title {
  margin: 0 0 8px 0;
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.3;
  color: #333;
}

.task-description {
  margin: 0 0 12px 0;
  font-size: 0.85rem;
  color: #666;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.task-labels {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.task-label {
  font-size: 0.7rem !important;
}

.more-labels {
  font-size: 0.7rem;
  color: #666;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.assignee-avatar {
  display: flex;
  align-items: center;
}

.dependencies-indicator {
  display: flex;
  align-items: center;
}

.task-date {
  font-size: 0.75rem;
  color: #999;
  margin-left: auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .task-card-content {
    padding: 10px !important;
  }
  
  .task-title {
    font-size: 0.9rem;
  }
  
  .task-description {
    font-size: 0.8rem;
  }
}
</style>