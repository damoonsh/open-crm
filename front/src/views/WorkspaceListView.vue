<template>
  <div class="workspace-list-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Workspaces</h1>
        <p class="header-subtitle">Manage your projects and collaborate with your team</p>
      </div>
      
      <div class="header-actions">
        <v-btn
          color="primary"
          @click="showCreateDialog = true"
        >
          <v-icon left>mdi-plus</v-icon>
          Create Workspace
        </v-btn>
      </div>
    </div>

    <!-- Error Messages -->
    <div v-if="routeError" class="error-section">
      <v-alert
        :type="getErrorType(routeError)"
        dismissible
        @click:close="clearRouteError"
      >
        {{ getErrorMessage(routeError) }}
      </v-alert>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p>Loading workspaces...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <v-alert type="error" dismissible @click:close="clearError">
        {{ error }}
      </v-alert>
      <v-btn color="primary" @click="loadWorkspaces">Retry</v-btn>
    </div>

    <!-- Empty State -->
    <div v-else-if="workspaces.length === 0" class="empty-state">
      <v-icon size="96" color="grey-lighten-2">mdi-folder-multiple</v-icon>
      <h2>No Workspaces Yet</h2>
      <p>Create your first workspace to start organizing your projects and collaborating with your team.</p>
      <v-btn
        color="primary"
        size="large"
        @click="showCreateDialog = true"
      >
        <v-icon left>mdi-plus</v-icon>
        Create Your First Workspace
      </v-btn>
    </div>

    <!-- Workspaces Grid -->
    <div v-else class="workspaces-content">
      <!-- Filters and Search -->
      <div class="workspace-filters">
        <v-text-field
          v-model="searchQuery"
          placeholder="Search workspaces..."
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 300px;"
        >
          <template #prepend-inner>
            <v-icon>mdi-magnify</v-icon>
          </template>
        </v-text-field>
        
        <v-select
          v-model="roleFilter"
          :items="roleFilterOptions"
          label="Filter by role"
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 200px;"
        />
      </div>

      <!-- Workspaces Grid -->
      <div class="workspaces-grid">
        <WorkspaceCard
          v-for="workspace in filteredWorkspaces"
          :key="workspace.id"
          :workspace="workspace"
          :user-role="getUserRole(workspace.id)"
          @click="openWorkspace(workspace.id)"
          @edit="editWorkspace(workspace)"
          @delete="confirmDelete(workspace)"
          @settings="openSettings(workspace.id)"
        />
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination-section">
        <v-pagination
          v-model="currentPage"
          :length="totalPages"
          :total-visible="7"
        />
      </div>
    </div>

    <!-- Create Workspace Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="500">
      <v-card>
        <v-card-title>Create New Workspace</v-card-title>
        <v-card-text>
          <v-form ref="createFormRef" v-model="createFormValid">
            <v-text-field
              v-model="createForm.name"
              label="Workspace Name"
              :rules="nameRules"
              variant="outlined"
              class="mb-4"
            />
            
            <v-textarea
              v-model="createForm.description"
              label="Description (Optional)"
              variant="outlined"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showCreateDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="creating"
            :disabled="!createFormValid"
            @click="createWorkspace"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Edit Workspace Dialog -->
    <v-dialog v-model="showEditDialog" max-width="500">
      <v-card>
        <v-card-title>Edit Workspace</v-card-title>
        <v-card-text>
          <v-form ref="editFormRef" v-model="editFormValid">
            <v-text-field
              v-model="editForm.name"
              label="Workspace Name"
              :rules="nameRules"
              variant="outlined"
              class="mb-4"
            />
            
            <v-textarea
              v-model="editForm.description"
              label="Description"
              variant="outlined"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showEditDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="updating"
            :disabled="!editFormValid"
            @click="updateWorkspace"
          >
            Update
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Workspace</v-card-title>
        <v-card-text>
          <v-alert type="warning" class="mb-4">
            This action cannot be undone!
          </v-alert>
          Are you sure you want to delete "{{ workspaceToDelete?.name }}"?
          This will permanently delete all tasks, categories, and data in this workspace.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn
            color="error"
            :loading="deleting"
            @click="deleteWorkspace"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Success/Error Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useWorkspaceStore } from '@/stores/workspace';
import { useAuthStore } from '@/stores/auth';
import WorkspaceCard from '@/components/workspace/WorkspaceCard.vue';
import type { Workspace } from '@/stores/workspace';

const router = useRouter();
const route = useRoute();
const workspaceStore = useWorkspaceStore();
const authStore = useAuthStore();

// Component state
const showCreateDialog = ref(false);
const showEditDialog = ref(false);
const showDeleteDialog = ref(false);
const createFormRef = ref();
const editFormRef = ref();
const createFormValid = ref(false);
const editFormValid = ref(false);
const creating = ref(false);
const updating = ref(false);
const deleting = ref(false);
const currentPage = ref(1);
const itemsPerPage = 12;

// Search and filters
const searchQuery = ref('');
const roleFilter = ref('all');

// Forms
const createForm = ref({
  name: '',
  description: ''
});

const editForm = ref({
  name: '',
  description: ''
});

const workspaceToEdit = ref<Workspace | null>(null);
const workspaceToDelete = ref<Workspace | null>(null);

// Snackbar
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
});

// Computed properties
const workspaces = computed(() => workspaceStore.workspaces);
const loading = computed(() => workspaceStore.loading);
const error = computed(() => workspaceStore.error);

const routeError = computed(() => route.query.error as string);

const filteredWorkspaces = computed(() => {
  let filtered = workspaces.value;

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(workspace =>
      workspace.name.toLowerCase().includes(query) ||
      (workspace.description && workspace.description.toLowerCase().includes(query))
    );
  }

  // Apply role filter
  if (roleFilter.value !== 'all') {
    filtered = filtered.filter(workspace => {
      const userRole = getUserRole(workspace.id);
      return userRole === roleFilter.value;
    });
  }

  return filtered;
});

const paginatedWorkspaces = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredWorkspaces.value.slice(start, end);
});

const totalPages = computed(() => {
  return Math.ceil(filteredWorkspaces.value.length / itemsPerPage);
});

// Validation rules
const nameRules = [
  (v: string) => !!v || 'Workspace name is required',
  (v: string) => v.length <= 100 || 'Name must be less than 100 characters'
];

const roleFilterOptions = [
  { title: 'All Workspaces', value: 'all' },
  { title: 'Admin', value: 'admin' },
  { title: 'Member', value: 'member' },
  { title: 'Viewer', value: 'viewer' }
];

// Methods
const loadWorkspaces = async () => {
  await workspaceStore.fetchUserWorkspaces();
  await authStore.fetchWorkspacePermissions();
};

const getUserRole = (workspaceId: number): string => {
  return authStore.getWorkspaceRole(workspaceId) || 'viewer';
};

const openWorkspace = (workspaceId: number) => {
  router.push(`/workspace/${workspaceId}`);
};

const editWorkspace = (workspace: Workspace) => {
  workspaceToEdit.value = workspace;
  editForm.value = {
    name: workspace.name,
    description: workspace.description || ''
  };
  showEditDialog.value = true;
};

const openSettings = (workspaceId: number) => {
  router.push(`/workspace/${workspaceId}/settings`);
};

const confirmDelete = (workspace: Workspace) => {
  workspaceToDelete.value = workspace;
  showDeleteDialog.value = true;
};

const createWorkspace = async () => {
  if (!createFormValid.value) return;

  creating.value = true;
  try {
    const newWorkspace = await workspaceStore.createWorkspace(createForm.value);
    if (newWorkspace) {
      showSnackbar('Workspace created successfully', 'success');
      showCreateDialog.value = false;
      createForm.value = { name: '', description: '' };
      
      // Refresh permissions and redirect to new workspace
      await authStore.fetchWorkspacePermissions();
      router.push(`/workspace/${newWorkspace.id}`);
    }
  } catch (error) {
    console.error('Error creating workspace:', error);
    showSnackbar('Failed to create workspace', 'error');
  } finally {
    creating.value = false;
  }
};

const updateWorkspace = async () => {
  if (!editFormValid.value || !workspaceToEdit.value) return;

  updating.value = true;
  try {
    await workspaceStore.updateWorkspace(workspaceToEdit.value.id, editForm.value);
    showSnackbar('Workspace updated successfully', 'success');
    showEditDialog.value = false;
    workspaceToEdit.value = null;
  } catch (error) {
    console.error('Error updating workspace:', error);
    showSnackbar('Failed to update workspace', 'error');
  } finally {
    updating.value = false;
  }
};

const deleteWorkspace = async () => {
  if (!workspaceToDelete.value) return;

  deleting.value = true;
  try {
    await workspaceStore.deleteWorkspace(workspaceToDelete.value.id);
    showSnackbar('Workspace deleted successfully', 'success');
    showDeleteDialog.value = false;
    workspaceToDelete.value = null;
    
    // Refresh permissions
    await authStore.fetchWorkspacePermissions();
  } catch (error) {
    console.error('Error deleting workspace:', error);
    showSnackbar('Failed to delete workspace', 'error');
  } finally {
    deleting.value = false;
  }
};

const clearError = () => {
  workspaceStore.clearError();
};

const clearRouteError = () => {
  router.replace({ query: {} });
};

const getErrorType = (errorCode: string): string => {
  switch (errorCode) {
    case 'access_denied':
      return 'warning';
    case 'admin_required':
      return 'info';
    default:
      return 'error';
  }
};

const getErrorMessage = (errorCode: string): string => {
  switch (errorCode) {
    case 'access_denied':
      return 'You don\'t have permission to access that workspace.';
    case 'admin_required':
      return 'Admin privileges are required for that action.';
    default:
      return 'An error occurred.';
  }
};

const showSnackbar = (text: string, color: string) => {
  snackbar.value = { show: true, text, color };
};

// Lifecycle
onMounted(() => {
  loadWorkspaces();
});

// Watch for search changes to reset pagination
watch([searchQuery, roleFilter], () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.workspace-list-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 32px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: 600;
}

.header-subtitle {
  margin: 0;
  color: #666;
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  align-items: center;
}

.error-section {
  padding: 16px 24px;
}

.loading-container,
.error-container,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  text-align: center;
}

.loading-container p {
  margin-top: 16px;
  color: #666;
}

.empty-state h2 {
  margin: 16px 0 8px 0;
  color: #666;
}

.empty-state p {
  margin: 0 0 32px 0;
  color: #999;
  max-width: 400px;
}

.workspaces-content {
  padding: 24px;
}

.workspace-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
}

.workspaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 24px;
    align-items: stretch;
    text-align: center;
  }

  .workspace-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .workspaces-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>