<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="700">
    <v-card>
      <v-card-title>
        {{ isEditing ? 'Edit Task' : 'Create Task' }}
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="formValid" @submit.prevent="save">
          <v-row>
            <!-- Title Field -->
            <v-col cols="12">
              <v-text-field
                v-model="form.title"
                label="Task Title"
                :rules="titleRules"
                required
                variant="outlined"
                density="compact"
              />
            </v-col>

            <!-- Description Field -->
            <v-col cols="12">
              <v-textarea
                v-model="form.description"
                label="Description"
                :rules="descriptionRules"
                required
                variant="outlined"
                rows="4"
              />
            </v-col>

            <!-- Category Selection -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.category_id"
                :items="categoryOptions"
                label="Category"
                variant="outlined"
                density="compact"
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
            </v-col>

            <!-- Priority Selection -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.priority"
                :items="priorityOptions"
                label="Priority"
                variant="outlined"
                density="compact"
              />
            </v-col>

            <!-- Status Selection -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.status"
                :items="statusOptions"
                label="Status"
                variant="outlined"
                density="compact"
              />
            </v-col>

            <!-- Story Points -->
            <v-col cols="12" sm="6">
              <v-text-field
                v-model.number="form.story_points"
                label="Story Points"
                type="number"
                :rules="storyPointsRules"
                variant="outlined"
                density="compact"
              />
            </v-col>

            <!-- Assignee Selection -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.assignee_id"
                :items="assigneeOptions"
                label="Assignee"
                clearable
                variant="outlined"
                density="compact"
              />
            </v-col>

            <!-- Labels -->
            <v-col cols="12">
              <v-combobox
                v-model="form.labels"
                :items="availableLabels"
                label="Labels"
                multiple
                chips
                closable-chips
                variant="outlined"
                density="compact"
              >
                <template #chip="{ props: chipProps, item }">
                  <v-chip v-bind="chipProps" :prepend-icon="getTagIcon(item.raw)" closable>
                    {{ item.raw }}
                  </v-chip>
                </template>
              </v-combobox>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn @click="cancel">Cancel</v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!formValid"
          @click="save"
        >
          {{ isEditing ? 'Update' : 'Create' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { useTaskStore } from '@/stores/tasks';
import { useCategoryStore } from '@/stores/categories';
import { getTagIcon } from '@/utils/tagIcons';
import type { Task, TaskCreate, TaskUpdate } from '@/stores/tasks';

interface Props {
  modelValue: boolean;
  task?: Task | null;
  workspaceId: number;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'saved'): void;
  (e: 'cancelled'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const taskStore = useTaskStore();
const categoryStore = useCategoryStore();
const formRef = ref();
const formValid = ref(false);

const isEditing = computed(() => !!props.task);
const loading = computed(() => taskStore.loading);

const form = ref<TaskCreate & { id?: number }>({
  title: '',
  description: '',
  category_id: null,
  priority: 'medium',
  status: 'open',
  assignee_id: null,
  story_points: null,
  labels: []
});

// Validation rules
const titleRules = [
  (v: string) => !!v || 'Task title is required',
  (v: string) => v.length <= 200 || 'Title must be less than 200 characters'
];

const descriptionRules = [
  (v: string) => !!v || 'Description is required',
  (v: string) => v.length <= 2000 || 'Description must be less than 2000 characters'
];

const storyPointsRules = [
  (v: number | null) => v === null || (v >= 1 && v <= 100) || 'Story points must be between 1 and 100'
];

// Options
const statusOptions = [
  { title: 'Open', value: 'open' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Review', value: 'review' },
  { title: 'Closed', value: 'closed' },
  { title: 'Blocked', value: 'blocked' }
];

const priorityOptions = [
  { title: 'High', value: 'high' },
  { title: 'Medium', value: 'medium' },
  { title: 'Low', value: 'low' }
];

const categoryOptions = computed(() => {
  return categoryStore.categories.map(category => ({
    title: category.name,
    value: category.id
  }));
});

const assigneeOptions = computed(() => {
  // TODO: Get actual users from workspace
  return [
    { title: 'Unassigned', value: null },
    { title: 'User 1', value: 1 },
    { title: 'User 2', value: 2 }
  ];
});

const availableLabels = [
  'frontend', 'backend', 'urgent', 'api', 'database',
  'ui', 'ux', 'testing', 'security', 'feature', 'bug'
];

// Methods
const getCategoryColor = (categoryId: number): string => {
  const category = categoryStore.categories.find(cat => cat.id === categoryId);
  return category?.color || '#6366f1';
};

const getCategoryName = (categoryId: number): string => {
  const category = categoryStore.categories.find(cat => cat.id === categoryId);
  return category?.name || 'Unknown';
};

const resetForm = () => {
  if (props.task) {
    form.value = {
      id: props.task.id,
      title: props.task.title,
      description: props.task.description,
      category_id: props.task.category_id,
      priority: props.task.priority,
      status: props.task.status,
      assignee_id: props.task.assignee_id,
      story_points: props.task.story_points,
      labels: props.task.labels ? [...props.task.labels] : []
    };
  } else {
    form.value = {
      title: '',
      description: '',
      category_id: null,
      priority: 'medium',
      status: 'open',
      assignee_id: null,
      story_points: null,
      labels: []
    };
  }
};

const save = async () => {
  if (!formValid.value) return;

  try {
    if (isEditing.value && props.task) {
      const updateData: TaskUpdate = {
        title: form.value.title,
        description: form.value.description,
        category_id: form.value.category_id,
        priority: form.value.priority,
        assignee_id: form.value.assignee_id,
        story_points: form.value.story_points,
        labels: form.value.labels
      };
      await taskStore.updateTask(props.task.id, updateData);
    } else {
      const createData: TaskCreate = {
        title: form.value.title,
        description: form.value.description,
        category_id: form.value.category_id,
        priority: form.value.priority,
        assignee_id: form.value.assignee_id,
        story_points: form.value.story_points,
        labels: form.value.labels
      };
      await taskStore.createTask(props.workspaceId, createData);
    }
    
    emit('saved');
  } catch (error) {
    console.error('Error saving task:', error);
  }
};

const cancel = () => {
  emit('cancelled');
};

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    resetForm();
    nextTick(() => {
      formRef.value?.resetValidation();
    });
  }
});

watch(() => props.task, () => {
  if (props.modelValue) {
    resetForm();
  }
});
</script>

<style scoped>
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
</style>