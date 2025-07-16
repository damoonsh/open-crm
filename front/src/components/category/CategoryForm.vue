<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="600">
    <v-card>
      <v-card-title>
        {{ isEditing ? 'Edit Category' : 'Create Category' }}
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="formValid" @submit.prevent="save">
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="form.name"
                label="Category Name"
                :rules="nameRules"
                required
                variant="outlined"
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="form.description"
                label="Description"
                rows="3"
                variant="outlined"
              />
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="form.color"
                label="Color"
                :rules="colorRules"
                variant="outlined"
              >
                <template #prepend-inner>
                  <div
                    class="color-preview"
                    :style="{ backgroundColor: form.color }"
                    @click="showColorPicker = true"
                  ></div>
                </template>
              </v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model.number="form.position"
                label="Position"
                type="number"
                :rules="positionRules"
                variant="outlined"
              />
            </v-col>

            <v-col cols="12">
              <v-select
                v-model="form.default_status"
                :items="statusOptions"
                label="Default Status"
                variant="outlined"
                required
              />
            </v-col>

            <v-col cols="12">
              <v-select
                v-model="form.allowed_statuses"
                :items="statusOptions"
                label="Allowed Statuses"
                multiple
                chips
                variant="outlined"
                :rules="allowedStatusRules"
              />
            </v-col>

            <v-col v-if="isEditing" cols="12">
              <v-switch
                v-model="form.is_archived"
                label="Archived"
                color="warning"
              />
            </v-col>
          </v-row>
        </v-form>

        <!-- Color Picker Dialog -->
        <v-dialog v-model="showColorPicker" max-width="300">
          <v-card>
            <v-card-title>Choose Color</v-card-title>
            <v-card-text>
              <div class="color-grid">
                <div
                  v-for="color in predefinedColors"
                  :key="color"
                  class="color-option"
                  :style="{ backgroundColor: color }"
                  :class="{ active: form.color === color }"
                  @click="selectColor(color)"
                ></div>
              </div>
              <v-text-field
                v-model="form.color"
                label="Custom Color (Hex)"
                :rules="colorRules"
                variant="outlined"
                class="mt-4"
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn @click="showColorPicker = false">Done</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
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
import { useCategoryStore } from '@/stores/categories';
import type { Category, CategoryCreate, CategoryUpdate } from '@/stores/categories';

interface Props {
  modelValue: boolean;
  category?: Category | null;
  workspaceId: number;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'saved'): void;
  (e: 'cancelled'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const categoryStore = useCategoryStore();
const formRef = ref();
const formValid = ref(false);
const showColorPicker = ref(false);

const isEditing = computed(() => !!props.category);
const loading = computed(() => categoryStore.loading);

const statusOptions = [
  { title: 'Open', value: 'open' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Review', value: 'review' },
  { title: 'Closed', value: 'closed' },
  { title: 'Blocked', value: 'blocked' }
];

const predefinedColors = [
  '#6366f1', '#8b5cf6', '#ec4899', '#ef4444', '#f97316',
  '#f59e0b', '#eab308', '#84cc16', '#22c55e', '#10b981',
  '#06b6d4', '#0ea5e9', '#3b82f6', '#6366f1', '#8b5cf6'
];

const form = ref<CategoryCreate & { is_archived?: boolean }>({
  name: '',
  description: '',
  color: '#6366f1',
  position: 0,
  default_status: 'open',
  allowed_statuses: ['open', 'in_progress', 'review', 'closed'],
  is_archived: false
});

// Validation rules
const nameRules = [
  (v: string) => !!v || 'Category name is required',
  (v: string) => v.length <= 100 || 'Name must be less than 100 characters'
];

const colorRules = [
  (v: string) => !!v || 'Color is required',
  (v: string) => /^#[0-9A-Fa-f]{6}$/.test(v) || 'Color must be a valid hex code (e.g., #6366f1)'
];

const positionRules = [
  (v: number) => v >= 0 || 'Position must be 0 or greater'
];

const allowedStatusRules = [
  (v: string[]) => v.length > 0 || 'At least one status must be allowed'
];

// Methods
const selectColor = (color: string) => {
  form.value.color = color;
};

const resetForm = () => {
  if (props.category) {
    form.value = {
      name: props.category.name,
      description: props.category.description || '',
      color: props.category.color,
      position: props.category.position,
      default_status: props.category.default_status,
      allowed_statuses: [...props.category.allowed_statuses],
      is_archived: props.category.is_archived
    };
  } else {
    form.value = {
      name: '',
      description: '',
      color: '#6366f1',
      position: categoryStore.categories.length,
      default_status: 'open',
      allowed_statuses: ['open', 'in_progress', 'review', 'closed'],
      is_archived: false
    };
  }
};

const save = async () => {
  if (!formValid.value) return;

  try {
    if (isEditing.value && props.category) {
      const updateData: CategoryUpdate = {
        name: form.value.name,
        description: form.value.description,
        color: form.value.color,
        position: form.value.position,
        default_status: form.value.default_status,
        allowed_statuses: form.value.allowed_statuses,
        is_archived: form.value.is_archived
      };
      await categoryStore.updateCategory(props.category.id, updateData);
    } else {
      const createData: CategoryCreate = {
        name: form.value.name,
        description: form.value.description,
        color: form.value.color,
        position: form.value.position,
        default_status: form.value.default_status,
        allowed_statuses: form.value.allowed_statuses
      };
      await categoryStore.createCategory(props.workspaceId, createData);
    }
    
    emit('saved');
  } catch (error) {
    console.error('Error saving category:', error);
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

watch(() => props.category, () => {
  if (props.modelValue) {
    resetForm();
  }
});
</script>

<style scoped>
.color-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid #ddd;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.color-option {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.color-option:hover {
  border-color: #ccc;
}

.color-option.active {
  border-color: #333;
  box-shadow: 0 0 0 2px rgba(51, 51, 51, 0.2);
}
</style>