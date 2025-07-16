<template>
  <div class="category-list">
    <div class="category-list-header">
      <h3 class="category-list-title">Categories</h3>
      <v-btn
        v-if="canManageCategories"
        color="primary"
        size="small"
        @click="showCreateDialog = true"
      >
        <v-icon left>mdi-plus</v-icon>
        Add Category
      </v-btn>
    </div>

    <div v-if="loading" class="text-center pa-4">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="error" class="error-message">
      <v-alert type="error" dismissible @click:close="clearError">
        {{ error }}
      </v-alert>
    </div>

    <div v-else class="categories-grid">
      <div
        v-for="category in sortedCategories"
        :key="category.id"
        class="category-item"
        :style="{ borderColor: category.color }"
      >
        <div class="category-header">
          <div class="category-info">
            <div class="category-color" :style="{ backgroundColor: category.color }"></div>
            <div>
              <h4 class="category-name">{{ category.name }}</h4>
              <p v-if="category.description" class="category-description">
                {{ category.description }}
              </p>
            </div>
          </div>
          
          <div v-if="canManageCategories" class="category-actions">
            <v-btn
              icon
              size="small"
              @click="editCategory(category)"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn
              icon
              size="small"
              @click="confirmDelete(category)"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </div>
        </div>

        <div class="category-stats">
          <v-chip size="small" variant="outlined">
            {{ getTaskCount(category.id) }} tasks
          </v-chip>
          <v-chip size="small" variant="outlined">
            Position: {{ category.position }}
          </v-chip>
        </div>

        <div class="category-status-info">
          <div class="default-status">
            <span class="label">Default Status:</span>
            <v-chip size="small" :color="getStatusColor(category.default_status)">
              {{ formatStatus(category.default_status) }}
            </v-chip>
          </div>
          <div class="allowed-statuses">
            <span class="label">Allowed Statuses:</span>
            <div class="status-chips">
              <v-chip
                v-for="status in category.allowed_statuses"
                :key="status"
                size="x-small"
                :color="getStatusColor(status)"
              >
                {{ formatStatus(status) }}
              </v-chip>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Category Dialog -->
    <CategoryForm
      v-model="showCreateDialog"
      :category="selectedCategory"
      :workspace-id="workspaceId"
      @saved="onCategorySaved"
      @cancelled="onCancelEdit"
    />

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Category</v-card-title>
        <v-card-text>
          Are you sure you want to delete "{{ categoryToDelete?.name }}"?
          This action cannot be undone and will affect all tasks in this category.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteCategory">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useCategoryStore } from '@/stores/categories';
import { useTaskStore } from '@/stores/tasks';
import { useAuthStore } from '@/stores/auth';
import CategoryForm from './CategoryForm.vue';
import type { Category } from '@/stores/categories';

interface Props {
  workspaceId: number;
}

const props = defineProps<Props>();

const categoryStore = useCategoryStore();
const taskStore = useTaskStore();
const authStore = useAuthStore();

const showCreateDialog = ref(false);
const showDeleteDialog = ref(false);
const selectedCategory = ref<Category | null>(null);
const categoryToDelete = ref<Category | null>(null);

// Computed properties
const categories = computed(() => categoryStore.categories);
const loading = computed(() => categoryStore.loading);
const error = computed(() => categoryStore.error);

const sortedCategories = computed(() => {
  return [...categories.value].sort((a, b) => a.position - b.position);
});

const canManageCategories = computed(() => {
  return authStore.canManageWorkspace(props.workspaceId);
});

// Methods
const getTaskCount = (categoryId: number): number => {
  return taskStore.tasks.filter(task => task.category_id === categoryId).length;
};

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

const editCategory = (category: Category) => {
  selectedCategory.value = category;
  showCreateDialog.value = true;
};

const confirmDelete = (category: Category) => {
  categoryToDelete.value = category;
  showDeleteDialog.value = true;
};

const deleteCategory = async () => {
  if (categoryToDelete.value) {
    await categoryStore.deleteCategory(categoryToDelete.value.id);
    showDeleteDialog.value = false;
    categoryToDelete.value = null;
  }
};

const onCategorySaved = () => {
  showCreateDialog.value = false;
  selectedCategory.value = null;
};

const onCancelEdit = () => {
  showCreateDialog.value = false;
  selectedCategory.value = null;
};

const clearError = () => {
  categoryStore.clearError();
};

// Lifecycle
onMounted(() => {
  categoryStore.fetchCategories(props.workspaceId);
  taskStore.fetchTasks(props.workspaceId);
});

watch(() => props.workspaceId, (newWorkspaceId) => {
  if (newWorkspaceId) {
    categoryStore.fetchCategories(newWorkspaceId);
    taskStore.fetchTasks(newWorkspaceId);
  }
});
</script>

<style scoped>
.category-list {
  padding: 16px;
}

.category-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.category-list-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.category-item {
  border: 2px solid;
  border-radius: 8px;
  padding: 16px;
  background: white;
  transition: box-shadow 0.2s;
}

.category-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.category-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
}

.category-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  flex-shrink: 0;
}

.category-name {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.category-description {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.category-actions {
  display: flex;
  gap: 4px;
}

.category-stats {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.category-status-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.default-status,
.allowed-statuses {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #666;
  min-width: 100px;
}

.status-chips {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.error-message {
  margin-bottom: 16px;
}
</style>