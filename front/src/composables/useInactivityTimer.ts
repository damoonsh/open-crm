// filepath: /Users/dshah/Downloads/TaskManagementApi/open-crm-ui/src/composables/useInactivityTimer.ts
import { ref, onMounted, onUnmounted } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useInactivityTimer(timeoutDuration = 2 * 60 * 1000) {
  // Default 2 minutes
  const authStore = useAuthStore();
  let inactivityTimer = ref<number | null>(null);

  const resetTimer = () => {
    if (inactivityTimer.value) {
      clearTimeout(inactivityTimer.value);
    }
    // Only set the timer if the user is actually authenticated
    if (authStore.isAuthenticated) {
      inactivityTimer.value = window.setTimeout(() => {
        // Check again before logging out, in case state changed rapidly
        if (authStore.isAuthenticated) {
          authStore.logout();
        }
      }, timeoutDuration);
    }
  };

  const activityHandler = () => {
    // Reset timer only if authenticated, otherwise no need to track inactivity
    if (authStore.isAuthenticated) {
      resetTimer();
    } else if (inactivityTimer.value) {
      // If user logs out manually, clear any existing timer
      clearTimeout(inactivityTimer.value);
      inactivityTimer.value = null;
    }
  };

  // Events that indicate user activity
  const activityEvents = [
    "mousemove",
    "keydown",
    "click",
    "scroll",
    "touchstart",
  ];

  onMounted(() => {
    activityEvents.forEach((event) => {
      window.addEventListener(event, activityHandler, true); // Use capture phase
    });
    resetTimer(); // Start the timer initially when component mounts
  });

  onUnmounted(() => {
    activityEvents.forEach((event) => {
      window.removeEventListener(event, activityHandler, true);
    });
    if (inactivityTimer.value) {
      clearTimeout(inactivityTimer.value); // Clean up timer on component unmount
    }
  });

  // Expose resetTimer in case you need to manually reset it from elsewhere (optional)
  return { resetTimer };
}
