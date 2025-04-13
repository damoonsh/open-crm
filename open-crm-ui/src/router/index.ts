import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import TaskView from "@/views/TaskView.vue";
import { useAuthStore } from "@/stores/auth"; // Import the auth store

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Home",
      component: HomeView,
      meta: { requiresAuth: true }, // Mark route as requiring authentication
      // beforeEnter removed
    },
    {
      path: "/login",
      name: "Login",
      component: LoginView,
      // Keep this guard to redirect logged-in users away from login
      beforeEnter: (to, from, next) => {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
          console.log(
            "[Router Guard] User already authenticated, redirecting to home."
          );
          next({ name: "Home" }); // Already logged in, go home
        } else {
          next(); // Not logged in, show login page
        }
      },
    },
    {
      path: "/task/:id",
      name: "TaskView",
      component: TaskView,
      props: true,
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);

  if (requiresAuth) {
    // This route requires auth, check if logged in
    if (authStore.isAuthenticated) {
      // User is authenticated, proceed to the route
      next();
    } else {
      // User not authenticated, redirect to login page
      console.log(
        "[Global Guard] User not authenticated, redirecting to login."
      );
      next({ name: "Login" }); // Redirect to the login route
    }
  } else {
    // This route does not require auth, allow access
    next();
  }
});

export default router;
