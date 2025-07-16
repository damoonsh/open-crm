<template>
  <v-card>
    <v-card-title>
      <div class="settings-header">
        <v-icon left>mdi-cog</v-icon>
        Category Settings
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
        <!-- Category Order Management -->
        <div class="settings-section">
          <h4 class="section-title">Category Order</h4>
          <p class="section-description">
            Drag and drop to reorder categories. This affects the order they appear in the kanban board.
          </p>
          
          <div class="category-order-list">
            <draggable
              v-model="orderedCategories"
              item-key="id"
              @end="onReorder"
              :disabled="!canManageCategories"
            >
              <template #item="{ element: category, index }">
                <div class="category-order-item">
                  <div class="drag-handle">
                    <v-icon>mdi-drag</v-icon>
                  </div>
                  <div class="category-info">
                    <div class="category-color" :style="{ backgroundColor: category.color }"></div>
                    <span class="category-name">{{ category.name }}</span>
                  </div>
                  <div class="position-info">
                    Position: {{ index + 1 }}
                  </div>
                </div>
              </template>
            </draggable>
          </div>
        </div>

        <!-- Archived Categories -->
        <div v-if="archivedCategories.length > 0" class="settings-section">
          <h4 class="section-title">Archived Categories</h4>
          <p class="section-description">
            These categories are archived and won't appear in the kanban board.
          </p>
          
          <div class="archived-categories">
            <div
              v-for="category in archivedCategories"
              :key="category.id"
              class="archived-category-item"
            >
              <div class="category-info">
                <div class="category-color" :style="{ backgroundColor: category.color }"></div>
                <span class="category-name">{{ category.name }}</span>
                <v-chip size="small" variant="outlined">
                  {{ getTaskCount(category.id) }} tasks
                </v-chip>
              </div>
              
              <div v-if="canManageCategories" class="category-actions">
                <v-btn
                  size="small"
                  variant="outlined"
                  @click="unarchiveCategory(category)"
                >
                  Restore
                </v-btn>
                <v-btn
                  size="small"
                  color="error"
                  variant="outlined"
                  @click="confirmDelete(category)"
                >
                  Delete
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <!-- Category Statistics -->
        <div class="settings-section">
          <h4 class="section-title">Category Statistics</h4>
          
          <div class="stats-grid">
            <div
              v-for="category in activeCategories"
              :key="category.id"
              class="stat-card"
            >
              <div class="stat-header">
                <div class="category-color" :style="{ backgroundColor: category.color }"></div>
                <span class="category-name">{{ category.name }}</span>
              </div>
              
              <div class="stat-content">
                <div class="stat-item">
                  <span class="stat-label">Total Tasks:</span>
                  <span class="stat-value">{{ getTaskCount(category.id) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Default Status:</span>
                  <v-chip size="small" :color="getStatusColor(category.default_status)">
                    {{ formatStatus(category.default_status) }}
                  </v-chip>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Allowed Statuses:</span>
                  <span class="stat-value">{{ category.allowed_statuses.length }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bulk Actions -->
        <div v-if="canManageCategories" class="settings-section">
          <h4 class="section-title">Bulk Actions</h4>
          
          <div class="bulk-actions">
            <v-btn
              color="warning"
              variant="outlined"
              @click="confirmArchiveAll"
            >
              Archive All Categories
            </v-btn>
            
            <v-btn
              color="success"
              variant="outlined"
              @click="resetCategoryOrder"
            >
              Reset Order
            </v-btn>
          </div>
        </div>
      </div>
    </v-card-text>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Category</v-card-title>
        <v-card-text>
          Are you sure you want to permanently delete "{{ categoryToDelete?.name }}"?
          This will also delete all {{ getTaskCount(categoryToDelete?.id || 0) }} tasks in this category.
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteCategory">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Archive All Confirmation Dialog -->
    <v-dialog v-model="showArchiveAllDialog" max-width="400">
      <v-card>
        <v-card-title>Archive All Categories</v-card-title>
        <v-card-text>
          Are you sure you want to archive all categories? This will hide them from the kanban board
          but preserve all tasks and data.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showArchiveAllDialog = false">Cancel</v-btn>
          <v-btn color="warning" @click="archiveAllCategories">Archive All</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useCategoryStore } from '@/stores/categories';
import { useTaskStore } from '@/stores/tasks';
import { useAuthStore } from '@/stores/auth';
import draggable from 'vuedraggable';
import type { Category } from '@/stores/categories';

interface Props {
  workspaceId: number;
}

const props = defineProps<Props>();

const categoryStore = useCategoryStore();
const taskStore = useTaskStore();
const authStore = useAuthStore();

const showDeleteDialog = ref(false);
const showArchiveAllDialog = ref(false);
const categoryToDelete = ref<Category | null>(null);
const orderedCategories = ref<Category[]>([]);

// Computed properties
const categories = computed(() => categoryStore.categories);
const loading = computed(() => categoryStore.loading);
const error = computed(() => categoryStore.error);

const activeCategories = computed(() => {
  return categories.value.filter(cat => !cat.is_archived);
});

const archivedCategories = computed(() => {
  return categories.value.filter(cat => cat.is_archived);
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

const onReorder = async () => {
  if (!canManageCategories.value) return;

  try {
    // Update positions for all categories
    const updates = orderedCategories.value.map((category, index) => ({
      id: category.id,
      position: index
    }));

    for (const update of updates) {
      await categoryStore.updateCategoryPosition(update.id, update.position);
    }
  } catch (error) {
    console.error('Error reordering categories:', error);
    // Revert order on error
    loadCategoryOrder();
  }
};

const unarchiveCategory = async (category: Category) => {
  try {
    await categoryStore.updateCategory(category.id, { is_archived: false });
  } catch (error) {
    console.error('Error unarchiving category:', error);
  }
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

const confirmArchiveAll = () => {
  showArchiveAllDialog.value = true;
};

const archiveAllCategories = async () => {
  try {
    for (const category of activeCategories.value) {
      await categoryStore.updateCategory(category.id, { is_archived: true });
    }
    showArchiveAllDialog.value = false;
  } catch (error) {
    console.error('Error archiving all categories:', error);
  }
};

const resetCategoryOrder = async () => {
  try {
    const sortedCategories = [...activeCategories.value].sort((a, b) => 
      a.name.localeCompare(b.name)
    );

    for (let i = 0; i < sortedCategories.length; i++) {
      await categoryStore.updateCategoryPosition(sortedCategories[i].id, i);
    }

    loadCategoryOrder();
  } catch (error) {
    console.error('Error resetting category order:', error);
  }
};

const loadCategoryOrder = () => {
  orderedCategories.value = [...activeCategories.value].sort((a, b) => 
    a.position - b.position
  );
};

const clearError = () => {
  categoryStore.clearError();
};

// Lifecycle
onMounted(async () => {
  await categoryStore.fetchCategories(props.workspaceId);
  await taskStore.fetchTasks(props.workspaceId);
  loadCategoryOrder();
});

// Watch for category changes
watch(activeCategories, () => {
  loadCategoryOrder();
});
</script>

<style scoped>
.settings-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-section {
  margin-bottom: 32px;
}

.section-title {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.section-description {
  margin: 0 0 16px 0;
  color: #666;
  font-size: 0.9rem;
}

.category-order-list {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.category-order-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  background: white;
  cursor: move;
}

.category-order-item:last-child {
  border-bottom: none;
}

.category-order-item:hover {
  background: #f5f5f5;
}

.drag-handle {
  margin-right: 12px;
  color: #999;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.category-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.category-name {
  font-weight: 500;
}

.position-info {
  color: #666;
  font-size: 0.85rem;
}

.archived-categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.archived-category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f9f9f9;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.stat-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: white;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.stat-value {
  font-weight: 500;
}

.bulk-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.error-message {
  margin-bottom: 16px;
}
</style>