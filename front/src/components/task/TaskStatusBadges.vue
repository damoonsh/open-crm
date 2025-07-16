<template>
  <div class="task-status-badges">
    <!-- Status Badge -->
    <v-chip
      :color="getStatusColor(task.status)"
      :variant="variant"
      :size="size"
      class="status-badge"
    >
      <v-icon v-if="showIcons" left size="small">{{ getStatusIcon(task.status) }}</v-icon>
      {{ formatStatus(task.status) }}
    </v-chip>

    <!-- Priority Badge -->
    <v-chip
      v-if="showPriority"
      :color="getPriorityColor(task.priority)"
      :variant="variant"
      :size="size"
      class="priority-badge"
    >
      <v-icon v-if="showIcons" left size="small">{{ getPriorityIcon(task.priority) }}</v-icon>
      {{ formatPriority(task.priority) }}
    </v-chip>

    <!-- Story Points Badge -->
    <v-chip
      v-if="showStoryPoints && task.story_points"
      color="info"
      :variant="variant"
      :size="size"
      class="story-points-badge"
    >
      <v-icon v-if="showIcons" left size="small">mdi-numeric</v-icon>
      {{ task.story_points }} pts
    </v-chip>

    <!-- Dependencies Badge -->
    <v-chip
      v-if="showDependencies && hasDependencies"
      color="warning"
      :variant="variant"
      :size="size"
      class="dependencies-badge"
    >
      <v-icon v-if="showIcons" left size="small">mdi-link</v-icon>
      {{ dependencyCount }} deps
    </v-chip>

    <!-- Assignee Badge -->
    <v-chip
      v-if="showAssignee && task.assignee_id"
      color="secondary"
      :variant="variant"
      :size="size"
      class="assignee-badge"
    >
      <v-icon v-if="showIcons" left size="small">mdi-account</v-icon>
      {{ getAssigneeName(task.assignee_id) }}
    </v-chip>

    <!-- Overdue Badge -->
    <v-chip
      v-if="showOverdue && isOverdue"
      color="error"
      :variant="variant"
      :size="size"
      class="overdue-badge"
    >
      <v-icon v-if="showIcons" left size="small">mdi-clock-alert</v-icon>
      Overdue
    </v-chip>

    <!-- Labels Count Badge -->
    <v-chip
      v-if="showLabelsCount && task.labels && task.labels.length > 0"
      color="default"
      :variant="variant"
      :size="size"
      class="labels-badge"
    >
      <v-icon v-if="showIcons" left size="small">mdi-tag</v-icon>
      {{ task.labels.length }} labels
    </v-chip>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Task } from '@/stores/tasks';

interface Props {
  task: Task;
  showPriority?: boolean;
  showStoryPoints?: boolean;
  showDependencies?: boolean;
  showAssignee?: boolean;
  showOverdue?: boolean;
  showLabelsCount?: boolean;
  showIcons?: boolean;
  size?: 'x-small' | 'small' | 'default' | 'large' | 'x-large';
  variant?: 'flat' | 'text' | 'elevated' | 'tonal' | 'outlined' | 'plain';
}

const props = withDefaults(defineProps<Props>(), {
  showPriority: true,
  showStoryPoints: true,
  showDependencies: true,
  showAssignee: false,
  showOverdue: true,
  showLabelsCount: false,
  showIcons: true,
  size: 'small',
  variant: 'flat'
});

// Computed properties
const hasDependencies = computed(() => {
  return (props.task.blocking_dependencies && props.task.blocking_dependencies.length > 0) ||
         (props.task.blocked_by_dependencies && props.task.blocked_by_dependencies.length > 0);
});

const dependencyCount = computed(() => {
  const blocking = props.task.blocking_dependencies?.length || 0;
  const blockedBy = props.task.blocked_by_dependencies?.length || 0;
  return blocking + blockedBy;
});

const isOverdue = computed(() => {
  // TODO: Implement due date logic when due_date field is added
  return false;
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

const getStatusIcon = (status: string): string => {
  const icons: Record<string, string> = {
    open: 'mdi-circle-outline',
    in_progress: 'mdi-play-circle',
    review: 'mdi-eye-circle',
    closed: 'mdi-check-circle',
    blocked: 'mdi-block-helper'
  };
  return icons[status] || 'mdi-help-circle';
};

const getPriorityColor = (priority: string): string => {
  const colors: Record<string, string> = {
    high: 'error',
    medium: 'warning',
    low: 'success'
  };
  return colors[priority] || 'grey';
};

const getPriorityIcon = (priority: string): string => {
  const icons: Record<string, string> = {
    high: 'mdi-arrow-up',
    medium: 'mdi-minus',
    low: 'mdi-arrow-down'
  };
  return icons[priority] || 'mdi-minus';
};

const formatStatus = (status: string): string => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatPriority = (priority: string): string => {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
};

const getAssigneeName = (assigneeId: number): string => {
  // TODO: Get actual user name from user store
  return `User ${assigneeId}`;
};
</script>

<style scoped>
.task-status-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.status-badge {
  font-weight: 600;
}

.priority-badge {
  font-weight: 500;
}

.story-points-badge {
  font-family: monospace;
}

.dependencies-badge {
  font-size: 0.8em;
}

.assignee-badge {
  font-size: 0.85em;
}

.overdue-badge {
  font-weight: 600;
  animation: pulse 2s infinite;
}

.labels-badge {
  opacity: 0.8;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .task-status-badges {
    gap: 4px;
  }
}
</style>