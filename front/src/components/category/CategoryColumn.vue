<template>
  <div
    class="category-column"
    :style="{ borderTopColor: category.color }"
    @drop="onDrop"
    @dragover.prevent
    @dragenter.prevent
  >
    <div class="column-header">
      <div class="column-title">
        <div class="category-color" :style="{ backgroundColor: category.color }"></div>
        <h3>{{ category.name }}</h3>
        <v-chip size="small" variant="outlined">{{ tasks.length }}</v-chip>
      </div>
      
      <div class="column-actions">
        <v-btn
          v-if="canCreateTasks"
          icon
          size="small"
          @click="showQuickAdd = !showQuickAdd"
        >
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        
        <v-menu v-if="canManageCategories">
          <template #activator="{ props: menuProps }">
            <v-btn icon size="small" v-bind="menuProps">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="$emit('edit-category', category)">
              <v-list-item-title>Edit Category</v-list-item-title>
            </v-list-item>
            <v-list-item @click="$emit('delete-category', category)">
              <v-list-item-title>Delete Category</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </div>

    <!-- Quick Add Task Form -->
    <div v-if="showQuickAdd" class="quick-add-form">
      <v-text-field
        v-model="quickTaskTitle"
        label="Task title"
        variant="outlined"
        density="compact"
        @keyup.enter="createQuickTask"
        @keyup.escape="cancelQuickAdd"
      />
      <div class="quick-add-actions">
        <v-btn size="small" @click="cancelQuickAdd">Cancel</v-btn>
        <v-btn
          size="small"
          color="primary"
          :disabled="!quickTaskTitle.trim()"
          @click="createQuickTask"
        >
          Add
        </v-btn>
      </div>
    </div>

    <!-- Task Cards -->
    <div class="task-list">
      <TaskCard
        v-for="task in sortedTasks"
        :key="task.id"
        :task="task"
        :draggable="canEditTasks"
        @click="$emit('task-click', task)"
        @dragstart="onDragStart($event, task)"
      />
    </div>

    <!-- Empty State -->
    <div v-if="tasks.length === 0" class="empty-state">
      <v-icon size="48" color="grey-lighten-2">mdi-clipboard-outline</v-icon>
      <p class="empty-text">No tasks in this category</p>
      <v-btn
        v-if="canCreateTasks"
        size="small"
        variant="outlined"
        @click="showQuickAdd = true"
      >
        Add first task
      </v-btn>
    </div>

    <!-- Drop Zone Indicator -->
    <div v-if="isDragOver" class="drop-zone-indicator">
      <v-icon>mdi-plus</v-icon>
      Drop task here
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useTaskStore } from '@/stores/tasks';
import { useAuthStore } from '@/stores/auth';
import TaskCard from '@/components/task/TaskCard.vue';
import type { Category } from '@/stores/categories';
import type { Task } from '@/stores/tasks';

interface Props {
  category: Category;
  tasks: Task[];
  workspaceId: number;
}

interface Emits {
  (e: 'edit-category', category: Category): void;
  (e: 'delete-category', category: Category): void;
  (e: 'task-click', task: Task): void;
  (e: 'task-moved', task: Task, targetCategoryId: number): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const taskStore = useTaskStore();
const authStore = useAuthStore();

const showQuickAdd = ref(false);
const quickTaskTitle = ref('');
const isDragOver = ref(false);

// Computed properties
const sortedTasks = computed(() => {
  return [...props.tasks].sort((a, b) => {
    // Sort by priority (high -> medium -> low) then by created date
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    const aPriority = priorityOrder[a.priority] || 0;
    const bPriority = priorityOrder[b.priority] || 0;
    
    if (aPriority !== bPriority) {
      return bPriority - aPriority;
    }
    
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
});

const canCreateTasks = computed(() => {
  return authStore.canEditTasks(props.workspaceId);
});

const canEditTasks = computed(() => {
  return authStore.canEditTasks(props.workspaceId);
});

const canManageCategories = computed(() => {
  return authStore.canManageWorkspace(props.workspaceId);
});

// Methods
const createQuickTask = async () => {
  if (!quickTaskTitle.value.trim()) return;

  try {
    await taskStore.createTask(props.workspaceId, {
      title: quickTaskTitle.value.trim(),
      description: '',
      category_id: props.category.id,
      priority: 'medium',
      status: props.category.default_status
    });
    
    quickTaskTitle.value = '';
    showQuickAdd.value = false;
  } catch (error) {
    console.error('Error creating quick task:', error);
  }
};

const cancelQuickAdd = () => {
  quickTaskTitle.value = '';
  showQuickAdd.value = false;
};

const onDragStart = (event: DragEvent, task: Task) => {
  if (!canEditTasks.value) {
    event.preventDefault();
    return;
  }
  
  event.dataTransfer?.setData('application/json', JSON.stringify({
    taskId: task.id,
    sourceCategoryId: task.category_id
  }));
};

const onDrop = async (event: DragEvent) => {
  event.preventDefault();
  isDragOver.value = false;
  
  if (!canEditTasks.value) return;
  
  try {
    const data = event.dataTransfer?.getData('application/json');
    if (!data) return;
    
    const { taskId, sourceCategoryId } = JSON.parse(data);
    
    if (sourceCategoryId === props.category.id) return; // Same category
    
    const task = taskStore.getTaskById(taskId);
    if (!task) return;
    
    // Update task category
    await taskStore.updateTaskCategory(taskId, props.category.id);
    
    emit('task-moved', task, props.category.id);
  } catch (error) {
    console.error('Error handling drop:', error);
  }
};

const onDragEnter = () => {
  if (canEditTasks.value) {
    isDragOver.value = true;
  }
};

const onDragLeave = (event: DragEvent) => {
  // Only hide indicator if leaving the column entirely
  if (!event.currentTarget?.contains(event.relatedTarget as Node)) {
    isDragOver.value = false;
  }
};
</script>

<style scoped>
.category-column {
  background: #f8f9fa;
  border-radius: 8px;
  border-top: 4px solid;
  min-height: 400px;
  width: 300px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.column-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
}

.column-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.column-title h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.column-actions {
  display: flex;
  gap: 4px;
}

.quick-add-form {
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
}

.quick-add-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.task-list {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 200px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  text-align: center;
  flex: 1;
}

.empty-text {
  margin: 8px 0 16px 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.drop-zone-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(99, 102, 241, 0.1);
  border: 2px dashed #6366f1;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  font-weight: 600;
  z-index: 10;
}

.category-column:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .category-column {
    width: 280px;
  }
}
</style>