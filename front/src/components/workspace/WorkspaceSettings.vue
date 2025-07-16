<template>
  <v-card class="workspace-settings">
    <v-card-title>
      <div class="settings-header">
        <v-icon left>mdi-cog</v-icon>
        Workspace Settings
      </div>
    </v-card-title>

    <v-card-text>
      <v-tabs v-model="activeTab" class="mb-6">
        <v-tab value="general">General</v-tab>
        <v-tab value="members">Members</v-tab>
        <v-tab value="categories">Categories</v-tab>
        <v-tab value="advanced">Advanced</v-tab>
      </v-tabs>

      <v-window v-model="activeTab">
        <!-- General Settings Tab -->
        <v-window-item value="general">
          <div class="settings-section">
            <h3>General Information</h3>
            
            <v-form ref="generalFormRef" v-model="generalFormValid">
              <v-text-field
                v-model="workspaceForm.name"
                label="Workspace Name"
                :rules="nameRules"
                :disabled="!canEditWorkspace"
                variant="outlined"
                class="mb-4"
              />
              
              <v-textarea
                v-model="workspaceForm.description"
                label="Description"
                :disabled="!canEditWorkspace"
                variant="outlined"
                rows="3"
                class="mb-4"
              />
              
              <div v-if="canEditWorkspace" class="form-actions">
                <v-btn
                  color="primary"
                  :loading="loading"
                  :disabled="!generalFormValid"
                  @click="saveGeneralSettings"
                >
                  Save Changes
                </v-btn>
              </div>
            </v-form>

            <!-- Workspace Statistics -->
            <div class="workspace-stats">
              <h4>Workspace Statistics</h4>
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ memberCount }}</div>
                  <div class="stat-label">Members</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ categoryCount }}</div>
                  <div class="stat-label">Categories</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ taskCount }}</div>
                  <div class="stat-label">Tasks</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ formatDate(workspace?.created_at) }}</div>
                  <div class="stat-label">Created</div>
                </div>
              </div>
            </div>
          </div>
        </v-window-item>

        <!-- Members Tab -->
        <v-window-item value="members">
          <WorkspaceUserList
            :workspace-id="workspaceId"
            :can-manage="canManageUsers"
          />
        </v-window-item>

        <!-- Categories Tab -->
        <v-window-item value="categories">
          <CategorySettings :workspace-id="workspaceId" />
        </v-window-item>

        <!-- Advanced Settings Tab -->
        <v-window-item value="advanced">
          <div class="settings-section">
            <h3>Advanced Settings</h3>
            
            <!-- Workspace Permissions -->
            <div class="permission-settings">
              <h4>Default Permissions</h4>
              <p class="setting-description">
                Set default permissions for new members joining this workspace.
              </p>
              
              <v-select
                v-model="defaultRole"
                :items="roleOptions"
                label="Default Role for New Members"
                :disabled="!canManageUsers"
                variant="outlined"
                class="mb-4"
              />
            </div>

            <!-- Workspace Visibility -->
            <div class="visibility-settings">
              <h4>Workspace Visibility</h4>
              <p class="setting-description">
                Control who can discover and request access to this workspace.
              </p>
              
              <v-radio-group
                v-model="workspaceVisibility"
                :disabled="!canManageUsers"
              >
                <v-radio
                  label="Private - Only invited members can access"
                  value="private"
                />
                <v-radio
                  label="Internal - Organization members can request access"
                  value="internal"
                />
              </v-radio-group>
            </div>

            <!-- Danger Zone -->
            <div v-if="canDeleteWorkspace" class="danger-zone">
              <h4>Danger Zone</h4>
              <p class="setting-description">
                These actions are irreversible. Please be careful.
              </p>
              
              <div class="danger-actions">
                <v-btn
                  color="error"
                  variant="outlined"
                  @click="showArchiveDialog = true"
                >
                  Archive Workspace
                </v-btn>
                
                <v-btn
                  color="error"
                  @click="showDeleteDialog = true"
                >
                  Delete Workspace
                </v-btn>
              </div>
            </div>
          </div>
        </v-window-item>
      </v-window>
    </v-card-text>

    <!-- Archive Confirmation Dialog -->
    <v-dialog v-model="showArchiveDialog" max-width="400">
      <v-card>
        <v-card-title>Archive Workspace</v-card-title>
        <v-card-text>
          Are you sure you want to archive "{{ workspace?.name }}"?
          This will hide the workspace from the main view but preserve all data.
          You can restore it later if needed.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showArchiveDialog = false">Cancel</v-btn>
          <v-btn color="warning" @click="archiveWorkspace">Archive</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Workspace</v-card-title>
        <v-card-text>
          <v-alert type="error" class="mb-4">
            This action cannot be undone!
          </v-alert>
          Are you sure you want to permanently delete "{{ workspace?.name }}"?
          This will delete all tasks, categories, and data in this workspace.
          
          <v-text-field
            v-model="deleteConfirmation"
            :label="`Type '${workspace?.name}' to confirm`"
            variant="outlined"
            class="mt-4"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn
            color="error"
            :disabled="deleteConfirmation !== workspace?.name"
            @click="deleteWorkspace"
          >
            Delete Forever
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useWorkspaceStore } from '@/stores/workspace';
import { useCategoryStore } from '@/stores/categories';
import { useTaskStore } from '@/stores/tasks';
import { useAuthStore } from '@/stores/auth';
import WorkspaceUserList from './WorkspaceUserList.vue';
import CategorySettings from '@/components/category/CategorySettings.vue';

interface Props {
  workspaceId: number;
}

const props = defineProps<Props>();

const workspaceStore = useWorkspaceStore();
const categoryStore = useCategoryStore();
const taskStore = useTaskStore();
const authStore = useAuthStore();

const activeTab = ref('general');
const generalFormRef = ref();
const generalFormValid = ref(false);
const showArchiveDialog = ref(false);
const showDeleteDialog = ref(false);
const deleteConfirmation = ref('');
const defaultRole = ref<'admin' | 'member' | 'viewer'>('member');
const workspaceVisibility = ref<'private' | 'internal'>('private');

const workspaceForm = ref({
  name: '',
  description: ''
});

// Computed properties
const workspace = computed(() => workspaceStore.currentWorkspace);
const loading = computed(() => workspaceStore.loading);

const canEditWorkspace = computed(() => {
  return authStore.canManageWorkspace(props.workspaceId);
});

const canManageUsers = computed(() => {
  return authStore.canManageWorkspace(props.workspaceId);
});

const canDeleteWorkspace = computed(() => {
  return authStore.isWorkspaceAdmin(props.workspaceId);
});

const memberCount = computed(() => {
  return workspaceStore.workspaceUsers.length;
});

const categoryCount = computed(() => {
  return categoryStore.categories.length;
});

const taskCount = computed(() => {
  return taskStore.tasks.length;
});

// Validation rules
const nameRules = [
  (v: string) => !!v || 'Workspace name is required',
  (v: string) => v.length <= 100 || 'Name must be less than 100 characters'
];

const roleOptions = [
  { title: 'Admin', value: 'admin' },
  { title: 'Member', value: 'member' },
  { title: 'Viewer', value: 'viewer' }
];

// Methods
const loadWorkspaceData = () => {
  if (workspace.value) {
    workspaceForm.value = {
      name: workspace.value.name,
      description: workspace.value.description || ''
    };
  }
};

const saveGeneralSettings = async () => {
  if (!generalFormValid.value || !canEditWorkspace.value) return;

  try {
    await workspaceStore.updateWorkspace(props.workspaceId, {
      name: workspaceForm.value.name,
      description: workspaceForm.value.description
    });
  } catch (error) {
    console.error('Error saving workspace settings:', error);
  }
};

const archiveWorkspace = async () => {
  try {
    // TODO: Implement workspace archiving
    console.log('Archive workspace:', props.workspaceId);
    showArchiveDialog.value = false;
  } catch (error) {
    console.error('Error archiving workspace:', error);
  }
};

const deleteWorkspace = async () => {
  if (deleteConfirmation.value !== workspace.value?.name) return;

  try {
    await workspaceStore.deleteWorkspace(props.workspaceId);
    showDeleteDialog.value = false;
    // Navigate away from deleted workspace
    // TODO: Implement navigation
  } catch (error) {
    console.error('Error deleting workspace:', error);
  }
};

const formatDate = (dateString?: string): string => {
  if (!dateString) return 'Unknown';
  return new Date(dateString).toLocaleDateString();
};

// Lifecycle
onMounted(async () => {
  await Promise.all([
    workspaceStore.getWorkspace(props.workspaceId),
    workspaceStore.fetchWorkspaceUsers(props.workspaceId),
    categoryStore.fetchCategories(props.workspaceId),
    taskStore.fetchTasks(props.workspaceId)
  ]);
  
  loadWorkspaceData();
});

// Watchers
watch(workspace, () => {
  loadWorkspaceData();
});

watch(() => props.workspaceId, async (newWorkspaceId) => {
  if (newWorkspaceId) {
    await Promise.all([
      workspaceStore.getWorkspace(newWorkspaceId),
      workspaceStore.fetchWorkspaceUsers(newWorkspaceId),
      categoryStore.fetchCategories(newWorkspaceId),
      taskStore.fetchTasks(newWorkspaceId)
    ]);
    
    loadWorkspaceData();
  }
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

.settings-section h3 {
  margin: 0 0 16px 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.settings-section h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.setting-description {
  margin: 0 0 16px 0;
  color: #666;
  font-size: 0.9rem;
}

.form-actions {
  margin-top: 16px;
}

.workspace-stats {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f9f9f9;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
  margin-top: 4px;
}

.permission-settings,
.visibility-settings {
  margin-bottom: 32px;
}

.danger-zone {
  margin-top: 48px;
  padding: 24px;
  border: 2px solid #f44336;
  border-radius: 8px;
  background: #ffebee;
}

.danger-zone h4 {
  color: #d32f2f;
}

.danger-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .danger-actions {
    flex-direction: column;
  }
}
</style>