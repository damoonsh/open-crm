<template>
  <div class="workspace-user-list">
    <div class="user-list-header">
      <h3>Workspace Members</h3>
      <v-btn
        v-if="canManage"
        color="primary"
        @click="showInviteDialog = true"
      >
        <v-icon left>mdi-account-plus</v-icon>
        Invite Member
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

    <div v-else>
      <!-- Members List -->
      <div class="members-list">
        <div
          v-for="user in users"
          :key="user.user_id"
          class="member-item"
        >
          <div class="member-info">
            <v-avatar size="40" class="member-avatar">
              <v-icon>mdi-account</v-icon>
            </v-avatar>
            
            <div class="member-details">
              <div class="member-name">{{ user.username }}</div>
              <div class="member-email">{{ user.email }}</div>
              <div class="member-joined">
                Joined {{ formatDate(user.created_at) }}
              </div>
            </div>
          </div>

          <div class="member-role">
            <v-select
              v-if="canManage && user.user_id !== currentUserId"
              v-model="user.role"
              :items="roleOptions"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="updateUserRole(user.user_id, $event)"
            />
            <v-chip
              v-else
              :color="getRoleColor(user.role)"
              size="small"
            >
              {{ formatRole(user.role) }}
              <span v-if="user.user_id === currentUserId"> (You)</span>
            </v-chip>
          </div>

          <div v-if="canManage && user.user_id !== currentUserId" class="member-actions">
            <v-menu>
              <template #activator="{ props: menuProps }">
                <v-btn icon size="small" v-bind="menuProps">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click="confirmRemoveUser(user)">
                  <v-list-item-title>Remove from workspace</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="users.length === 0" class="empty-state">
        <v-icon size="64" color="grey-lighten-2">mdi-account-group</v-icon>
        <h4>No members yet</h4>
        <p>Invite team members to collaborate on this workspace</p>
        <v-btn
          v-if="canManage"
          color="primary"
          @click="showInviteDialog = true"
        >
          Invite First Member
        </v-btn>
      </div>
    </div>

    <!-- Invite Member Dialog -->
    <WorkspaceInvite
      v-model="showInviteDialog"
      :workspace-id="workspaceId"
      @invited="onUserInvited"
      @cancelled="showInviteDialog = false"
    />

    <!-- Remove User Confirmation Dialog -->
    <v-dialog v-model="showRemoveDialog" max-width="400">
      <v-card>
        <v-card-title>Remove Member</v-card-title>
        <v-card-text>
          Are you sure you want to remove {{ userToRemove?.username }} from this workspace?
          They will lose access to all tasks and data in this workspace.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showRemoveDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="removeUser">Remove</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useWorkspaceStore } from '@/stores/workspace';
import { useAuthStore } from '@/stores/auth';
import WorkspaceInvite from './WorkspaceInvite.vue';
import type { WorkspaceUser } from '@/stores/workspace';

interface Props {
  workspaceId: number;
  canManage: boolean;
}

const props = defineProps<Props>();

const workspaceStore = useWorkspaceStore();
const authStore = useAuthStore();

const showInviteDialog = ref(false);
const showRemoveDialog = ref(false);
const userToRemove = ref<WorkspaceUser | null>(null);

// Computed properties
const users = computed(() => workspaceStore.workspaceUsers);
const loading = computed(() => workspaceStore.loading);
const error = computed(() => workspaceStore.error);
const currentUserId = computed(() => authStore.userId);

const roleOptions = [
  { title: 'Admin', value: 'admin' },
  { title: 'Member', value: 'member' },
  { title: 'Viewer', value: 'viewer' }
];

// Methods
const getRoleColor = (role: string): string => {
  const colors: Record<string, string> = {
    admin: 'error',
    member: 'primary',
    viewer: 'secondary'
  };
  return colors[role] || 'default';
};

const formatRole = (role: string): string => {
  return role.charAt(0).toUpperCase() + role.slice(1);
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'today';
  if (diffDays <= 7) return `${diffDays} days ago`;
  if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
  if (diffDays <= 365) return `${Math.ceil(diffDays / 30)} months ago`;
  
  return `${Math.ceil(diffDays / 365)} years ago`;
};

const updateUserRole = async (userId: number, newRole: 'admin' | 'member' | 'viewer') => {
  if (!props.canManage) return;

  try {
    await workspaceStore.updateUserRole(props.workspaceId, userId, { role: newRole });
    
    // Update auth store permissions if it's the current user
    if (userId === currentUserId.value) {
      authStore.updateWorkspacePermission(props.workspaceId, newRole);
    }
  } catch (error) {
    console.error('Error updating user role:', error);
    // Refresh the user list to revert any optimistic updates
    await workspaceStore.fetchWorkspaceUsers(props.workspaceId);
  }
};

const confirmRemoveUser = (user: WorkspaceUser) => {
  userToRemove.value = user;
  showRemoveDialog.value = true;
};

const removeUser = async () => {
  if (!userToRemove.value || !props.canManage) return;

  try {
    await workspaceStore.removeUserFromWorkspace(props.workspaceId, userToRemove.value.user_id);
    showRemoveDialog.value = false;
    userToRemove.value = null;
  } catch (error) {
    console.error('Error removing user:', error);
  }
};

const onUserInvited = () => {
  showInviteDialog.value = false;
  // Refresh the user list
  workspaceStore.fetchWorkspaceUsers(props.workspaceId);
};

const clearError = () => {
  workspaceStore.clearError();
};

// Lifecycle
onMounted(() => {
  workspaceStore.fetchWorkspaceUsers(props.workspaceId);
});
</script>

<style scoped>
.user-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.user-list-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.member-avatar {
  background: #f5f5f5;
}

.member-details {
  flex: 1;
}

.member-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 2px;
}

.member-email {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.member-joined {
  color: #999;
  font-size: 0.8rem;
}

.member-role {
  min-width: 120px;
  margin-right: 12px;
}

.member-actions {
  display: flex;
  align-items: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-state h4 {
  margin: 16px 0 8px 0;
  color: #666;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #999;
}

.error-message {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .user-list-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .member-item {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .member-info {
    justify-content: flex-start;
  }

  .member-role {
    min-width: auto;
    margin-right: 0;
  }
}
</style>