import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import TaskView from "../views/TaskView.vue";
import RegisterView from "../views/RegisterView.vue";
import WorkspaceView from "../views/WorkspaceView.vue";
import WorkspaceListView from "../views/WorkspaceListView.vue";
import WorkspaceSettingsView from "../views/WorkspaceSettingsView.vue";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Home",
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: "/login",
      name: "Login",
      component: LoginView,
    },
    {
      path: "/register",
      name: "Register",
      component: RegisterView,
    },
    
    // Workspace Routes
    {
      path: "/workspaces",
      name: "WorkspaceList",
      component: WorkspaceListView,
      meta: { requiresAuth: true },
    },
    {
      path: "/workspace/:id",
      name: "Workspace",
      component: WorkspaceView,
      props: true,
      meta: { 
        requiresAuth: true,
        requiresWorkspaceAccess: true 
      },
    },
    {
      path: "/workspace/:id/settings",
      name: "WorkspaceSettings",
      component: WorkspaceSettingsView,
      props: true,
      meta: { 
        requiresAuth: true,
        requiresWorkspaceAdmin: true 
      },
    },
    
    // Task Routes
    {
      path: "/task/:id",
      name: "TaskView",
      component: TaskView,
      props: true,
      meta: { requiresAuth: true },
    },
    
    // Redirect root to workspaces
    {
      path: "/",
      redirect: "/workspaces"
    }
  ],
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const requiresWorkspaceAccess = to.matched.some((record) => record.meta.requiresWorkspaceAccess);
  const requiresWorkspaceAdmin = to.matched.some((record) => record.meta.requiresWorkspaceAdmin);
  
  console.log(`[Router Guard] Navigating to: ${to.name}`);
  
  const isAuthenticated = authStore.isAuthenticated;
  const isLoginPage = to.name === "Login";
  const isRegisterPage = to.name === "Register";

  // Check authentication first
  if (requiresAuth && !isAuthenticated) {
    console.log("[Router Guard] Authentication required, redirecting to login");
    next({ name: "Login" });
    return;
  }

  // Redirect authenticated users away from auth pages
  if ((isLoginPage || isRegisterPage) && isAuthenticated) {
    console.log("[Router Guard] Already authenticated, redirecting to workspaces");
    next({ name: "WorkspaceList" });
    return;
  }

  // Check workspace-specific permissions
  if (isAuthenticated && (requiresWorkspaceAccess || requiresWorkspaceAdmin)) {
    const workspaceId = parseInt(to.params.id as string);
    
    if (isNaN(workspaceId)) {
      console.log("[Router Guard] Invalid workspace ID");
      next({ name: "WorkspaceList" });
      return;
    }

    // Ensure workspace permissions are loaded
    if (authStore.workspacePermissions.length === 0) {
      try {
        await authStore.fetchWorkspacePermissions();
      } catch (error) {
        console.error("[Router Guard] Failed to fetch workspace permissions:", error);
      }
    }

    // Check workspace access
    if (requiresWorkspaceAccess && !authStore.canViewWorkspace(workspaceId)) {
      console.log(`[Router Guard] No access to workspace ${workspaceId}`);
      next({ 
        name: "WorkspaceList",
        query: { error: "access_denied" }
      });
      return;
    }

    // Check admin permissions
    if (requiresWorkspaceAdmin && !authStore.canManageWorkspace(workspaceId)) {
      console.log(`[Router Guard] No admin access to workspace ${workspaceId}`);
      next({ 
        name: "Workspace", 
        params: { id: workspaceId.toString() },
        query: { error: "admin_required" }
      });
      return;
    }
  }

  next();
});

export default router;
