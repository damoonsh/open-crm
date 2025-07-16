<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="500">
    <v-card>
      <v-card-title>
        <div class="invite-header">
          <v-icon left>mdi-account-plus</v-icon>
          Invite Member
        </div>
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="formValid" @submit.prevent="inviteUser">
          <div class="invite-methods">
            <v-tabs v-model="inviteMethod" class="mb-4">
              <v-tab value="email">By Email</v-tab>
              <v-tab value="username">By Username</v-tab>
            </v-tabs>

            <v-window v-model="inviteMethod">
              <!-- Email Invitation -->
              <v-window-item value="email">
                <v-text-field
                  v-model="form.email"
                  label="Email Address"
                  type="email"
                  :rules="emailRules"
                  variant="outlined"
                  class="mb-4"
                />
                
                <p class="invite-description">
                  An invitation email will be sent to this address with instructions to join the workspace.
                </p>
              </v-window-item>

              <!-- Username Invitation -->
              <v-window-item value="username">
                <v-text-field
                  v-model="form.username"
                  label="Username"
                  :rules="usernameRules"
                  variant="outlined"
                  class="mb-4"
                />
                
                <p class="invite-description">
                  The user will be added directly to the workspace if they exist in the system.
                </p>
              </v-window-item>
            </v-window>
          </div>

          <!-- Role Selection -->
          <v-select
            v-model="form.role"
            :items="roleOptions"
            label="Role"
            variant="outlined"
            class="mb-4"
          >
            <template #item="{ props: itemProps, item }">
              <v-list-item v-bind="itemProps">
                <template #prepend>
                  <v-icon :color="getRoleColor(item.raw)">{{ getRoleIcon(item.raw) }}</v-icon>
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ getRoleDescription(item.raw) }}</v-list-item-subtitle>
              </v-list-item>
            </template>
          </v-select>

          <!-- Personal Message -->
          <v-textarea
            v-model="form.message"
            label="Personal Message (Optional)"
            placeholder="Add a personal message to the invitation..."
            variant="outlined"
            rows="3"
            class="mb-4"
          />

          <!-- Bulk Invite -->
          <v-expansion-panels v-if="inviteMethod === 'email'" class="mb-4">
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-email-multiple</v-icon>
                Bulk Invite
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-textarea
                  v-model="bulkEmails"
                  label="Multiple Email Addresses"
                  placeholder="Enter multiple email addresses, separated by commas or new lines"
                  variant="outlined"
                  rows="4"
                />
                <p class="bulk-invite-help">
                  You can paste multiple email addresses separated by commas, spaces, or new lines.
                </p>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-form>

        <!-- Invitation Preview -->
        <div v-if="form.email || form.username" class="invitation-preview">
          <h4>Invitation Preview</h4>
          <div class="preview-card">
            <div class="preview-header">
              <v-icon left>mdi-email</v-icon>
              Workspace Invitation
            </div>
            <div class="preview-content">
              <p><strong>{{ getRecipientDisplay() }}</strong> has been invited to join:</p>
              <p class="workspace-name">{{ workspaceName }}</p>
              <p>Role: <v-chip size="small" :color="getRoleColor(form.role)">{{ formatRole(form.role) }}</v-chip></p>
              <p v-if="form.message" class="personal-message">
                "{{ form.message }}"
              </p>
            </div>
          </div>
        </div>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn @click="cancel">Cancel</v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!formValid || (!form.email && !form.username && !bulkEmails)"
          @click="inviteUser"
        >
          {{ getBulkEmailList().length > 1 ? `Send ${getBulkEmailList().length} Invitations` : 'Send Invitation' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { useWorkspaceStore } from '@/stores/workspace';

interface Props {
  modelValue: boolean;
  workspaceId: number;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'invited'): void;
  (e: 'cancelled'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const workspaceStore = useWorkspaceStore();
const formRef = ref();
const formValid = ref(false);
const inviteMethod = ref<'email' | 'username'>('email');
const bulkEmails = ref('');

const form = ref({
  email: '',
  username: '',
  role: 'member' as 'admin' | 'member' | 'viewer',
  message: ''
});

// Computed properties
const loading = computed(() => workspaceStore.loading);
const workspaceName = computed(() => workspaceStore.currentWorkspace?.name || 'Workspace');

const roleOptions = [
  { title: 'Admin', value: 'admin' },
  { title: 'Member', value: 'member' },
  { title: 'Viewer', value: 'viewer' }
];

// Validation rules
const emailRules = [
  (v: string) => {
    if (inviteMethod.value === 'email' && !bulkEmails.value) {
      return !!v || 'Email is required';
    }
    return true;
  },
  (v: string) => {
    if (v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) {
      return 'Please enter a valid email address';
    }
    return true;
  }
];

const usernameRules = [
  (v: string) => {
    if (inviteMethod.value === 'username') {
      return !!v || 'Username is required';
    }
    return true;
  },
  (v: string) => {
    if (v && v.length < 3) {
      return 'Username must be at least 3 characters';
    }
    return true;
  }
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

const getRoleIcon = (role: string): string => {
  const icons: Record<string, string> = {
    admin: 'mdi-crown',
    member: 'mdi-account',
    viewer: 'mdi-eye'
  };
  return icons[role] || 'mdi-account';
};

const getRoleDescription = (role: string): string => {
  const descriptions: Record<string, string> = {
    admin: 'Full access to workspace settings and members',
    member: 'Can create and edit tasks, manage categories',
    viewer: 'Read-only access to workspace content'
  };
  return descriptions[role] || '';
};

const formatRole = (role: string): string => {
  return role.charAt(0).toUpperCase() + role.slice(1);
};

const getRecipientDisplay = (): string => {
  if (inviteMethod.value === 'email') {
    return form.value.email || 'Email recipient';
  } else {
    return form.value.username || 'Username';
  }
};

const getBulkEmailList = (): string[] => {
  if (!bulkEmails.value) {
    return form.value.email ? [form.value.email] : [];
  }
  
  return bulkEmails.value
    .split(/[,\n\r\s]+/)
    .map(email => email.trim())
    .filter(email => email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
};

const inviteUser = async () => {
  if (!formValid.value) return;

  try {
    if (inviteMethod.value === 'email') {
      const emails = getBulkEmailList();
      
      for (const email of emails) {
        await workspaceStore.addUserToWorkspace(props.workspaceId, {
          user_email: email,
          role: form.value.role
        });
      }
    } else {
      // For username invitation, we'd need to look up the user first
      // This is a simplified implementation
      await workspaceStore.addUserToWorkspace(props.workspaceId, {
        user_email: `${form.value.username}@example.com`, // This would be resolved server-side
        role: form.value.role
      });
    }
    
    emit('invited');
  } catch (error) {
    console.error('Error inviting user:', error);
  }
};

const cancel = () => {
  emit('cancelled');
};

const resetForm = () => {
  form.value = {
    email: '',
    username: '',
    role: 'member',
    message: ''
  };
  bulkEmails.value = '';
  inviteMethod.value = 'email';
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

watch(inviteMethod, () => {
  // Clear form when switching methods
  form.value.email = '';
  form.value.username = '';
  bulkEmails.value = '';
});
</script>

<style scoped>
.invite-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.invite-methods {
  margin-bottom: 24px;
}

.invite-description {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.bulk-invite-help {
  margin: 8px 0 0 0;
  color: #666;
  font-size: 0.85rem;
}

.invitation-preview {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.invitation-preview h4 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
}

.preview-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.preview-header {
  background: #f5f5f5;
  padding: 12px 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-content {
  padding: 16px;
}

.preview-content p {
  margin: 0 0 8px 0;
}

.workspace-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.personal-message {
  font-style: italic;
  color: #666;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-top: 12px !important;
}
</style>