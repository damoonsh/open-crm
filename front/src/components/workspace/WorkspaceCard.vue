<template>
  <v-card
    class="workspace-card"
    :class="{ 'workspace-card--admin': userRole === 'admin' }"
    @click="$emit('click')"
  >
    <v-card-text class="workspace-content">
      <div class="workspace-header">
        <div class="workspace-info">
          <h3 class="workspace-name">{{ workspace.name }}</h3>
          <v-chip
            :color="getRoleColor(userRole)"
            size="small"
            class="role-chip"
          >
            {{ formatRole(userRole) }}
          </v-chip>
        </div>
        
        <div class="workspace-actions">
          <v-menu v-if="canManage">
            <template #activator="{ props: menuProps }">
              <v-btn
                icon
                size="small"
                variant="text"
                v-bind="menuProps"
                @click.stop
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item @click="$emit('edit', workspace)">
                <v-list-item-title>Edit Workspace</v-list-item-title>
              </v-list-item>
              <v-list-item @click="$emit('settings', workspace.id)">
                <v-list-item-title>Settings</v-list-item-title>
              </v-list-item>
              <v-divider />
              <v-list-item @click="$emit('delete', workspace)" class="text-error">
                <v-list-item-title>Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </div>

      <p v-if="workspace.description" class="workspace-description">
        {{ truncatedDescription }}
      </p>
      <p v-else class="workspace-description no-description">
        No description provided
      </p>

      <div class="workspace-stats">
        <div class="stat-item">
          <v-icon size="small">mdi-account-group</v-icon>
          <span>{{ memberCount }} members</span>
        </div>
        
        <div class="stat-item">
          <v-icon size="small">mdi-clipboard-list</v-icon>
          <span>{{ taskCount }} tasks</span>
        </div>
        
        <div class="stat-item">
          <v-icon size="small">mdi-folder</v-icon>
          <span>{{ categoryCount }} categories</span>
        </div>
      </div>

      <div class="workspace-footer">
        <div class="workspace-date">
          <v-icon size="small">mdi-calendar</v-icon>
          <span>Created {{ formatDate(workspace.created_at) }}</span>
        </div>
        
        <div class="workspace-status">
          <div class="status-indicator" :class="`status-${getActivityStatus()}`"></div>
          <span class="status-text">{{ getActivityText() }}</span>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Workspace } from '@/stores/workspace';

interface Props {
  workspace: Workspace;
  userRole: 'admin' | 'member' | 'viewer';
}

interface Emits {
  (e: 'click'): void;
  (e: 'edit', workspace: Workspace): void;
  (e: 'delete', workspace: Workspace): void;
  (e: 'settings', workspaceId: number): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Computed properties
const canManage = computed(() => {
  return props.userRole === 'admin';
});

const truncatedDescription = computed(() => {
  if (!props.workspace.description) return '';
  return props.workspace.description.length > 120
    ? props.workspace.description.substring(0, 120) + '...'
    : props.workspace.description;
});

const memberCount = computed(() => {
  return props.workspace.users?.length || 0;
});

const taskCount = computed(() => {
  // TODO: Get actual task count from workspace data
  return Math.floor(Math.random() * 50); // Placeholder
});

const categoryCount = computed(() => {
  // TODO: Get actual category count from workspace data
  return Math.floor(Math.random() * 10) + 1; // Placeholder
});

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

const getActivityStatus = (): string => {
  // TODO: Implement actual activity detection based on recent tasks/updates
  const lastUpdate = new Date(props.workspace.updated_at);
  const now = new Date();
  const diffHours = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60);
  
  if (diffHours < 24) return 'active';
  if (diffHours < 168) return 'recent'; // 1 week
  return 'inactive';
};

const getActivityText = (): string => {
  const status = getActivityStatus();
  switch (status) {
    case 'active':
      return 'Active';
    case 'recent':
      return 'Recent activity';
    case 'inactive':
      return 'Quiet';
    default:
      return 'Unknown';
  }
};
</script>

<style scoped>
.workspace-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid transparent;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.workspace-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.workspace-card--admin {
  border-left-color: #f44336;
}

.workspace-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px !important;
}

.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.workspace-info {
  flex: 1;
}

.workspace-name {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: 600;
  line-height: 1.3;
  color: #333;
}

.role-chip {
  font-size: 0.75rem !important;
  height: 20px !important;
}

.workspace-actions {
  flex-shrink: 0;
  margin-left: 12px;
}

.workspace-description {
  margin: 0 0 16px 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  flex: 1;
}

.workspace-description.no-description {
  font-style: italic;
  color: #999;
}

.workspace-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #666;
}

.workspace-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.workspace-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #999;
}

.workspace-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.status-active {
  background-color: #4caf50;
}

.status-indicator.status-recent {
  background-color: #ff9800;
}

.status-indicator.status-inactive {
  background-color: #9e9e9e;
}

.status-text {
  font-size: 0.8rem;
  color: #666;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .workspace-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .workspace-actions {
    margin-left: 0;
    align-self: flex-end;
  }

  .workspace-footer {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>