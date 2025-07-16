<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="500">
    <v-card>
      <v-card-title>
        <div class="move-dialog-header">
          <v-icon left>mdi-folder-move</v-icon>
          Move Task to Workspace
        </div>
      </v-card-title>

      <v-card-text>
        <div class="task-info">
          <h4>{{ task.title }}</h4>
          <p class="current-workspace">
            Current workspace: <strong>{{ currentWorkspaceName }}</strong>
          </p>
        </div>

        <v-form ref="formRef" v-model="formValid">
          <v-select
            v-model="selectedWorkspaceId"
            :items="availableWorkspaces"
            label="Target Workspace"
            :rules="workspaceRules"
            variant="outlined"
            :loading="workspacesLoading"
          >
            <template #item="{ props: itemProps, item }">
              <v-list-item v-bind="itemProps">
                <template #prepend>
                  <v-icon>mdi-folder</v-icon>
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.subtitle }}</v-list-item-subtitle>
              </v-list-item>
            </template>
          </v-select>

          <!-- Category Selection for Target Workspace -->
          <v-select
            v-if="selectedWorkspaceId && targetCategories.length > 0"
            v-model="selectedCategoryId"
            :items="targetCategories"
            label="Target Category (Optional)"
            clearable
            variant="outlined"
            :loading="categoriesLoading"
          >
            <template #selection="{ item }">
              <div class="category-selection">
                <div class="category-color" :style="{ backgroundColor: getCategoryColor(item.raw) }"></div>
                {{ getCategoryName(item.raw) }}
              </div>
            </template>
            <template #item="{ props: itemProps, item }">
              <v-list-item v-bind="itemProps">
                <template #prepend>
                  <div class="category-color" :style="{ backgroundColor: getCategoryColor(item.raw) }"></div>
                </template>
              </v-list-item>
            </template>
          </v-select>

          <!-- Warning Messages -->
          <div v-if="warnings.length > 0" class="warnings-section">
            <v-alert
              v-for="warning in warnings"
              :key="warning"
              type="warning"
              variant="tonal"
              class="mb-2"
            >
              {{ warning }}
            </v-alert>
          </div>

          <!-- Move Impact Information -->
          <div v-if="selectedWorkspaceId" class="move-impact">
            <h5>Move Impact:</h5>
            <ul class="impact-list">
              <li>Task will be moved to the selected workspace</li>
              <li>All comments and history will be preserved</li>
              <li v-if="task.blocked_by_dependencies && task.blocked_by_dependencies.length > 0">
                Dependencies with tasks in other workspaces will be maintained
              </li>
              <li v-if="task.assignee_id">
                Assignee will be preserved if they have access to the target workspace
              </li>
              <li>Task notifications will be sent to workspace members</li>
            </ul>
          </div>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn @click="cancel">Cancel</v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!formValid || !selectedWorkspaceId"
          @click="moveTask"
        >
          Move Task
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useTaskStore } from '@/stores/tasks';
import { useWorkspaceStore } from '@/stores/workspace';
import { useCategoryStore } from '@/stores/categories';
import { useAuthStore } from '@/stores/auth';
import type { Task } from '@/stores/tasks';

interface Props {
  modelValue: boolean;
  task: Task;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'moved', workspaceId: number): void;
  (e: 'cancelled'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const taskStore = useTaskStore();
const workspaceStore = useWorkspaceStore();
const categoryStore = useCategoryStore();
const authStore = useAuthStore();

const formRef = ref();
const formValid = ref(false);
const selectedWorkspaceId = ref<number | null>(null);
const selectedCategoryId = ref<number | null>(null);
const warnings = ref<string[]>([]);
const targetWorkspaceCategories = ref<any[]>([]);

// Computed properties
const loading = computed(() => taskStore.loading);
const workspacesLoading = computed(() => workspaceStore.loading);
const categoriesLoading = computed(() => categoryStore.loading);

const currentWorkspaceName = computed(() => {
  const workspace = workspaceStore.getWorkspaceById(props.task.workspace_id);
  return workspace?.name || 'Unknown Workspace';
});

const availableWorkspaces = computed(() => {
  return workspaceStore.workspaces
    .filter(workspace => 
      workspace.id !== props.task.workspace_id && 
      authStore.canEditTasks(workspace.id)
    )
    .map(workspace => ({
      title: workspace.name,
      subtitle: workspace.description || 'No description',
      value: workspace.id
    }));
});

const targetCategories = computed(() => {
  return targetWorkspaceCategories.value.map(category => ({
    title: category.name,
    value: category.id
  }));
});

// Validation rules
const workspaceRules = [
  (v: number | null) => !!v || 'Please select a target workspace'
];

// Methods
const getCategoryColor = (categoryId: number): string => {
  const category = targetWorkspaceCategories.value.find(cat => cat.id === categoryId);
  return category?.color || '#6366f1';
};

const getCategoryName = (categoryId: number): string => {
  const category = targetWorkspaceCategories.value.find(cat => cat.id === categoryId);
  return category?.name || 'Unknown';
};

const loadTargetWorkspaceCategories = async (workspaceId: number) => {
  try {
    const response = await fetch(`/api/workspaces/${workspaceId}/categories`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      targetWorkspaceCategories.value = await response.json();
    } else {
      targetWorkspaceCategories.value = [];
    }
  } catch (error) {
    console.error('Error loading target workspace categories:', error);
    targetWorkspaceCategories.value = [];
  }
};

const validateMove = () => {
  warnings.value = [];

  if (!selectedWorkspaceId.value) return;

  // Check if user has permission to move to target workspace
  if (!authStore.canEditTasks(selectedWorkspaceId.value)) {
    warnings.value.push('You may not have permission to add tasks to the selected workspace.');
  }

  // Check for cross-workspace dependencies
  if (props.task.blocked_by_dependencies && props.task.blocked_by_dependencies.length > 0) {
    warnings.value.push('This task has dependencies that may span across workspaces after the move.');
  }

  // Check if assignee has access to target workspace
  if (props.task.assignee_id) {
    warnings.value.push('Please verify that the assigned user has access to the target workspace.');
  }
};

const moveTask = async () => {
  if (!formValid.value || !selectedWorkspaceId.value) return;

  try {
    await taskStore.moveTaskToWorkspace(props.task.id, selectedWorkspaceId.value, selectedCategoryId.value);
    emit('moved', selectedWorkspaceId.value);
  } catch (error) {
    console.error('Error moving task:', error);
  }
};

const cancel = () => {
  emit('cancelled');
};

const resetForm = () => {
  selectedWorkspaceId.value = null;
  selectedCategoryId.value = null;
  warnings.value = [];
  targetWorkspaceCategories.value = [];
};

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    resetForm();
    workspaceStore.fetchUserWorkspaces();
  }
});

watch(selectedWorkspaceId, async (newWorkspaceId) => {
  selectedCategoryId.value = null;
  
  if (newWorkspaceId) {
    await loadTargetWorkspaceCategories(newWorkspaceId);
    validateMove();
  } else {
    targetWorkspaceCategories.value = [];
    warnings.value = [];
  }
});
</script>

<style scoped>
.move-dialog-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
}

.task-info h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.current-workspace {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.category-selection {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.warnings-section {
  margin: 16px 0;
}

.move-impact {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.move-impact h5 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
}

.impact-list {
  margin: 0;
  padding-left: 20px;
}

.impact-list li {
  margin-bottom: 4px;
  font-size: 0.9rem;
  color: #666;
}
</style>