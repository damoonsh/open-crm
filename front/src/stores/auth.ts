import { defineStore } from "pinia";
import axios from "axios";

const API_URL = "http://localhost:8000/auth";

export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface WorkspacePermission {
  workspace_id: number;
  role: 'admin' | 'member' | 'viewer';
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: JSON.parse(localStorage.getItem("user") || "null") as User | null,
    workspacePermissions: [] as WorkspacePermission[],
    error: null as string | null,
    loading: false,
    isAuthenticated: !!localStorage.getItem("token"),
  }),

  getters: {
    username: (state) => state.user?.username || '',
    userId: (state) => state.user?.id || null,
    userEmail: (state) => state.user?.email || '',
    
    // Permission checking getters
    hasWorkspaceAccess: (state) => {
      return (workspaceId: number) => {
        return state.workspacePermissions.some(
          perm => perm.workspace_id === workspaceId
        );
      };
    },
    
    getWorkspaceRole: (state) => {
      return (workspaceId: number): 'admin' | 'member' | 'viewer' | null => {
        const permission = state.workspacePermissions.find(
          perm => perm.workspace_id === workspaceId
        );
        return permission?.role || null;
      };
    },
    
    canManageWorkspace: (state) => {
      return (workspaceId: number): boolean => {
        const permission = state.workspacePermissions.find(
          perm => perm.workspace_id === workspaceId
        );
        return permission?.role === 'admin';
      };
    },
    
    canEditTasks: (state) => {
      return (workspaceId: number): boolean => {
        const permission = state.workspacePermissions.find(
          perm => perm.workspace_id === workspaceId
        );
        return permission?.role === 'admin' || permission?.role === 'member';
      };
    },
    
    canViewWorkspace: (state) => {
      return (workspaceId: number): boolean => {
        return state.workspacePermissions.some(
          perm => perm.workspace_id === workspaceId
        );
      };
    },
    
    isWorkspaceAdmin: (state) => {
      return (workspaceId: number): boolean => {
        const permission = state.workspacePermissions.find(
          perm => perm.workspace_id === workspaceId
        );
        return permission?.role === 'admin';
      };
    },
    
    isWorkspaceMember: (state) => {
      return (workspaceId: number): boolean => {
        const permission = state.workspacePermissions.find(
          perm => perm.workspace_id === workspaceId
        );
        return permission?.role === 'member';
      };
    },
    
    isWorkspaceViewer: (state) => {
      return (workspaceId: number): boolean => {
        const permission = state.workspacePermissions.find(
          perm => perm.workspace_id === workspaceId
        );
        return permission?.role === 'viewer';
      };
    }
  },

  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      this.error = null;

      try {
        console.log("[Auth] Login attempt:", email);

        const response = await axios.post(`${API_URL}/login`, {
          email,
          password,
        });

        console.log("[Auth] Login response:", response.status);

        if (response.status === 200 && response.data.access_token) {
          const token = response.data.access_token;

          this.token = token;
          this.isAuthenticated = true;

          localStorage.setItem("token", token);

          // Get user info
          const userResponse = await axios.get(`${API_URL}/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          this.user = userResponse.data;
          localStorage.setItem("user", JSON.stringify(userResponse.data));

          return true;
        }
        throw new Error("Invalid response from server");
      } catch (error: any) {
        console.error("[Auth] Login failed:", error);
        this.error =
          error.response?.data?.detail || error.message || "Login failed";
        this.logout();
        return false;
      } finally {
        this.loading = false;
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      this.error = null;
      this.loading = false;
      this.isAuthenticated = false;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },

    async register(userData: {
      username: string;
      email: string;
      password: string;
    }) {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.post(`${API_URL}/register`, userData);
        
        if (response.status === 201) {
          // Auto-login after successful registration
          return await this.login(userData.email, userData.password);
        }
        
        throw new Error("Registration failed");
      } catch (error: any) {
        console.error("[Auth] Registration failed:", error);
        this.error = error.response?.data?.detail || error.message || "Registration failed";
        return false;
      } finally {
        this.loading = false;
      }
    },

    async fetchWorkspacePermissions() {
      if (!this.token || !this.user) return;

      try {
        const response = await axios.get('/api/workspaces', {
          headers: { Authorization: `Bearer ${this.token}` }
        });

        // Extract permissions from workspace data
        const workspaces = response.data;
        this.workspacePermissions = workspaces.map((workspace: any) => {
          // Find current user's role in this workspace
          const userRole = workspace.users?.find((user: any) => 
            user.user_id === this.user?.id
          )?.role || 'viewer';

          return {
            workspace_id: workspace.id,
            role: userRole
          };
        });
      } catch (error: any) {
        console.error("[Auth] Failed to fetch workspace permissions:", error);
      }
    },

    updateWorkspacePermission(workspaceId: number, role: 'admin' | 'member' | 'viewer') {
      const existingIndex = this.workspacePermissions.findIndex(
        perm => perm.workspace_id === workspaceId
      );

      if (existingIndex !== -1) {
        this.workspacePermissions[existingIndex].role = role;
      } else {
        this.workspacePermissions.push({ workspace_id: workspaceId, role });
      }
    },

    removeWorkspacePermission(workspaceId: number) {
      this.workspacePermissions = this.workspacePermissions.filter(
        perm => perm.workspace_id !== workspaceId
      );
    },

    // Permission validation helpers
    requireWorkspaceAccess(workspaceId: number): boolean {
      if (!this.hasWorkspaceAccess(workspaceId)) {
        this.error = "You don't have access to this workspace";
        return false;
      }
      return true;
    },

    requireWorkspaceRole(workspaceId: number, requiredRole: 'admin' | 'member'): boolean {
      const userRole = this.getWorkspaceRole(workspaceId);
      
      if (!userRole) {
        this.error = "You don't have access to this workspace";
        return false;
      }

      if (requiredRole === 'admin' && userRole !== 'admin') {
        this.error = "You need admin privileges for this action";
        return false;
      }

      if (requiredRole === 'member' && userRole === 'viewer') {
        this.error = "You need member or admin privileges for this action";
        return false;
      }

      return true;
    },

    clearError() {
      this.error = null;
    },
  },
});
