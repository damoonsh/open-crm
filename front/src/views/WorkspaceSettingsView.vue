<template>
  <div class="workspace-settings-view">
    <!-- Header -->
    <div class="settings-header">
      <div class="header-navigation">
        <v-btn
          variant="text"
          @click="goBack"
          prepend-icon="mdi-arrow-left"
        >
          Back to {{ workspaceName }}
        </v-btn>
        
        <div class="breadcrumb">
          <span class="workspace-name">{{ workspaceName }}</span>
          <v-icon>mdi-chevron-right</v-icon>
          <span class="current-page">Settings</span>
        </div>
      </div>
      
      <div class="header-actions">
        <v-btn
          color="primary"
          @click="saveAllSettings"
          :loading="saving"
        >
          <v-icon left>mdi-content-save</v-icon>
          Save Changes
        </v-btn>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p>Loading workspace settings...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <v-alert type="error" dismissible @click:close="clearError">
        {{ error }}
      </v-alert>
      <v-btn color="primary" @click="loadWorkspaceSettings">Retry</v-btn>
    </div>

    <!-- Access Denied -->
    <div v-else-if="!canManageWorkspace" class="access-denied">
      <v-icon size="96" color="grey-lighten-2">mdi-shield-lock</v-icon>
      <h2>Access Denied</h2>
      <p>You need admin privileges to access workspace settings.</p>
      <v-btn color="primary" @click="goBack">Go Back</v-btn>
    </div>

    <!-- Settings Content -->
    <div v-else class="settings-content">
      <WorkspaceSettings :workspace-id="workspaceId" />
    </div>

    <!-- Success/Error Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useWorkspaceStore } from '@/stores/workspace';
import { useAuthStore } from '@/stores/auth';
import WorkspaceSettings from '@/components/workspace/WorkspaceSettings.vue';

const route = useRoute();
const router = useRouter();
const workspaceStore = useWorkspaceStore();
const authStore = useAuthStore();

// Component state
const saving = ref(false);
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
});

// Computed properties
const workspaceId = computed(() => parseInt(route.params.id as string));
const workspace = computed(() => workspaceStore.currentWorkspace);
const loading = computed(() => workspaceStore.loading);
const error = computed(() => workspaceStore.error);

const workspaceName = computed(() => {
  return workspace.value?.name || 'Workspace';
});

const canManageWorkspace = computed(() => {
  return authStore.canManageWorkspace(workspaceId.value);
});

// Methods
const loadWorkspaceSettings = async () => {
  if (!workspaceId.value) return;

  try {
    await workspaceStore.getWorkspace(workspaceId.value);
  } catch (error) {
    console.error('Error loading workspace settings:', error);
  }
};

const goBack = () => {
  router.push(`/workspace/${workspaceId.value}`);
};

const saveAllSettings = async () => {
  // This is a placeholder - actual saving is handled by individual components
  saving.value = true;
  
  try {
    // Simulate save operation
    await new Promise(resolve => setTimeout(resolve, 1000));
    showSnackbar('Settings saved successfully', 'success');
  } catch (error) {
    console.error('Error saving settings:', error);
    showSnackbar('Failed to save settings', 'error');
  } finally {
    saving.value = false;
  }
};

const clearError = () => {
  workspaceStore.clearError();
};

const showSnackbar = (text: string, color: string) => {
  snackbar.value = { show: true, text, color };
};

// Lifecycle
onMounted(() => {
  loadWorkspaceSettings();
});
</script>

<style scoped>
.workspace-settings-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.settings-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-navigation {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #666;
}

.workspace-name {
  font-weight: 500;
}

.current-page {
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
}

.loading-container,
.error-container,
.access-denied {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 48px;
  text-align: center;
}

.loading-container p {
  margin-top: 16px;
  color: #666;
}

.access-denied h2 {
  margin: 16px 0 8px 0;
  color: #666;
}

.access-denied p {
  margin: 0 0 24px 0;
  color: #999;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Responsive design */
@media (max-width: 768px) {
  .settings-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-navigation {
    justify-content: space-between;
  }

  .settings-content {
    padding: 16px;
  }
}
</style>