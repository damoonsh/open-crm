import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useAuthStore } from "./auth";

// Types for Workspace and Users
export interface WorkspaceUser {
  user_id: number;
  username: string;
  email: string;
  role: 'admin' | 'member' | 'viewer';
  created_at: string;
}

export interface Workspace {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  users?: WorkspaceUser[];
}

export interface WorkspaceCreate {
  name: string;
  description?: string;
}

export interface WorkspaceUpdate {
  name?: string;
  description?: string;
}

export interface WorkspaceUserAdd {
  user_id: number;
  role?: 'admin' | 'member' | 'viewer';
}

export interface WorkspaceUserUpdate {
  role: 'admin' | 'member' | 'viewer';
}

export const useWorkspaceStore = defineStore("workspace", () => {
  // State
  const workspaces = ref<Workspace[]>([]);
  const currentWorkspace = ref<Workspace | null>(null);
  const workspaceUsers = ref<WorkspaceUser[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const getWorkspaceById = computed(() => {
    return (workspaceId: number) => 
      workspaces.value.find(ws => ws.id === workspaceId);
  });

  const currentUserRole = computed(() => {
    const authStore = useAuthStore();
    if (!currentWorkspace.value || !authStore.user) return null;
    
    const userInWorkspace = workspaceUsers.value.find(
      user => user.username === authStore.username
    );
    return userInWorkspace?.role || null;
  });

  const canManageUsers = computed(() => {
    return currentUserRole.value === 'admin';
  });

  const canEditWorkspace = computed(() => {
    return currentUserRole.value === 'admin';
  });

  const canCreateTasks = computed(() => {
    return currentUserRole.value !== 'viewer';
  });

  // Actions
  const fetchUserWorkspaces = async () => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch('/api/workspaces', {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch workspaces: ${response.statusText}`);
      }

      const data = await response.json();
      workspaces.value = data;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch workspaces';
      console.error('Error fetching workspaces:', err);
    } finally {
      loading.value = false;
    }
  };

  const getWorkspace = async (workspaceId: number): Promise<Workspace | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/workspaces/${workspaceId}`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to fetch workspace: ${response.statusText}`);
      }

      const workspace = await response.json();
      currentWorkspace.value = workspace;
      
      // Update workspace in list if it exists
      const index = workspaces.value.findIndex(ws => ws.id === workspaceId);
      if (index !== -1) {
        workspaces.value[index] = workspace;
      } else {
        workspaces.value.push(workspace);
      }
      
      return workspace;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch workspace';
      console.error('Error fetching workspace:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const createWorkspace = async (workspaceData: WorkspaceCreate): Promise<Workspace | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch('/api/workspaces', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workspaceData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to create workspace: ${response.statusText}`);
      }

      const newWorkspace = await response.json();
      workspaces.value.push(newWorkspace);
      
      return newWorkspace;
    } catch (err: any) {
      error.value = err.message || 'Failed to create workspace';
      console.error('Error creating workspace:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const updateWorkspace = async (workspaceId: number, workspaceData: WorkspaceUpdate): Promise<Workspace | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/workspaces/${workspaceId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workspaceData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to update workspace: ${response.statusText}`);
      }

      const updatedWorkspace = await response.json();
      
      // Update workspace in store
      const index = workspaces.value.findIndex(ws => ws.id === workspaceId);
      if (index !== -1) {
        workspaces.value[index] = updatedWorkspace;
      }
      
      if (currentWorkspace.value?.id === workspaceId) {
        currentWorkspace.value = updatedWorkspace;
      }
      
      return updatedWorkspace;
    } catch (err: any) {
      error.value = err.message || 'Failed to update workspace';
      console.error('Error updating workspace:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const deleteWorkspace = async (workspaceId: number): Promise<boolean> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/workspaces/${workspaceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to delete workspace: ${response.statusText}`);
      }

      // Remove workspace from store
      const index = workspaces.value.findIndex(ws => ws.id === workspaceId);
      if (index !== -1) {
        workspaces.value.splice(index, 1);
      }
      
      if (currentWorkspace.value?.id === workspaceId) {
        currentWorkspace.value = null;
      }
      
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to delete workspace';
      console.error('Error deleting workspace:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  // User Management Actions
  const fetchWorkspaceUsers = async (workspaceId: number) => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/workspaces/${workspaceId}/users`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to fetch workspace users: ${response.statusText}`);
      }

      const users = await response.json();
      workspaceUsers.value = users;
      
      return users;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch workspace users';
      console.error('Error fetching workspace users:', err);
      return [];
    } finally {
      loading.value = false;
    }
  };

  const addUserToWorkspace = async (workspaceId: number, userData: WorkspaceUserAdd): Promise<WorkspaceUser | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/workspaces/${workspaceId}/users`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to add user to workspace: ${response.statusText}`);
      }

      const newUser = await response.json();
      workspaceUsers.value.push(newUser);
      
      return newUser;
    } catch (err: any) {
      error.value = err.message || 'Failed to add user to workspace';
      console.error('Error adding user to workspace:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const updateUserRole = async (workspaceId: number, userId: number, roleData: WorkspaceUserUpdate): Promise<WorkspaceUser | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/workspaces/${workspaceId}/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(roleData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to update user role: ${response.statusText}`);
      }

      const updatedUser = await response.json();
      
      // Update user in store
      const index = workspaceUsers.value.findIndex(user => user.user_id === userId);
      if (index !== -1) {
        workspaceUsers.value[index] = updatedUser;
      }
      
      return updatedUser;
    } catch (err: any) {
      error.value = err.message || 'Failed to update user role';
      console.error('Error updating user role:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const removeUserFromWorkspace = async (workspaceId: number, userId: number): Promise<boolean> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/workspaces/${workspaceId}/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to remove user from workspace: ${response.statusText}`);
      }

      // Remove user from store
      const index = workspaceUsers.value.findIndex(user => user.user_id === userId);
      if (index !== -1) {
        workspaceUsers.value.splice(index, 1);
      }
      
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to remove user from workspace';
      console.error('Error removing user from workspace:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  const clearWorkspaces = () => {
    workspaces.value = [];
    currentWorkspace.value = null;
    workspaceUsers.value = [];
  };

  const setCurrentWorkspace = (workspace: Workspace | null) => {
    currentWorkspace.value = workspace;
  };

  return {
    // State
    workspaces,
    currentWorkspace,
    workspaceUsers,
    loading,
    error,
    
    // Getters
    getWorkspaceById,
    currentUserRole,
    canManageUsers,
    canEditWorkspace,
    canCreateTasks,
    
    // Actions
    fetchUserWorkspaces,
    getWorkspace,
    createWorkspace,
    updateWorkspace,
    deleteWorkspace,
    fetchWorkspaceUsers,
    addUserToWorkspace,
    updateUserRole,
    removeUserFromWorkspace,
    clearError,
    clearWorkspaces,
    setCurrentWorkspace,
  };
});