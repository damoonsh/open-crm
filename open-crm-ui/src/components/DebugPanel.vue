<template>
    <v-expansion-panels v-if="isDev" class="mb-4">
        <v-expansion-panel>
            <v-expansion-panel-title>
                <div class="d-flex align-center">
                    <v-icon start color="warning">mdi-bug</v-icon>
                    Debug Panel
                    <v-chip v-if="taskStore.error" color="error" size="small" class="ml-2">Error</v-chip>
                </div>
            </v-expansion-panel-title>

            <v-expansion-panel-text>
                <div class="d-flex align-center mb-2">
                    <v-spacer></v-spacer>
                    <v-btn density="compact" icon="mdi-refresh" variant="text" @click="taskStore.fetchTasks"
                        :loading="taskStore.loading"></v-btn>
                </div>
                <pre class="debug-info">
Auth Status: {{ authStore.isAuthenticated }}
Token: {{ truncatedToken }}
Loading: {{ taskStore.loading }}
Error: {{ taskStore.error }}
Tasks Count: {{ taskStore.tasks.length }}
Tasks: {{ JSON.stringify(taskStore.tasks, null, 2) }}
                </pre>
            </v-expansion-panel-text>
        </v-expansion-panel>
    </v-expansion-panels>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTaskStore } from '@/stores/tasks'

const isDev = ref(process.env.NODE_ENV === 'development')
const authStore = useAuthStore()
const taskStore = useTaskStore()

const truncatedToken = computed(() => {
    if (!authStore.token) return 'No token'
    return `${authStore.token.substring(0, 20)}...`
})
</script>

<style scoped>
.debug-info {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: monospace;
    font-size: 12px;
    line-height: 1.5;
    background-color: rgba(0, 0, 0, 0.03);
    padding: 8px;
    border-radius: 4px;
}

.v-theme--dark .debug-info {
    background-color: rgba(255, 255, 255, 0.05);
}
</style>