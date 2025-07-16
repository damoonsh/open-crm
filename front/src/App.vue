<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useInactivityTimer } from '@/composables/useInactivityTimer';

// Initialize the inactivity timer with a 2-minute timeout
useInactivityTimer(2 * 60 * 1000);
</script>

<template>
  <v-app>
    <header>
      <!-- Your header content -->
    </header>

    <RouterView />

    <footer>
      <!-- Your footer content -->
    </footer>
  </v-app>
</template>

<style scoped>
/* Your styles */
</style>
