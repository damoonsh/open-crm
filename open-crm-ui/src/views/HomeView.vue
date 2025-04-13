<template>
    <dashboard-layout @logout="handleLogout">
        <v-container>
            <debug-panel />
            <v-row justify="center">
                <v-col cols="12" md="10" lg="8">
                    <div class="d-flex justify-space-between align-center mb-6">
                        <h1 class="text-h4 font-weight-bold">Your Tasks</h1>
                        <div class="d-flex align-center">
                            <v-btn color="primary" class="mr-2" prepend-icon="mdi-plus" v-if="taskStore.tasks.length"
                                @click="showCreateDialog = true">
                                Create Task
                            </v-btn>
                            <v-btn :loading="taskStore.loading" @click="taskStore.fetchTasks"
                                icon="mdi-refresh"></v-btn>
                        </div>
                    </div>

                    <v-card v-if="taskStore.loading" flat>
                        <loading-state />
                    </v-card>

                    <v-card v-else-if="taskStore.error" flat>
                        <error-alert :error="taskStore.error" @retry="taskStore.fetchTasks" />
                    </v-card>

                    <v-card v-else>
                        <empty-state v-if="!taskStore.tasks.length" @create-task="openCreateTaskDialog" />
                        <v-list v-else>
                            <v-list-item v-for="(task, index) in taskStore.tasks" :key="task.id" class="mb-4">
                                <task-item :task="task" :index="index" />
                            </v-list-item>
                        </v-list>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Create Task Dialog -->
            <task-edit-dialog 
  :show-dialog="showCreateDialog" 
  @update:show-dialog="showCreateDialog = $event" 
  @task-saved="handleTaskSaved" 
  @error="handleError"
/>
            <!-- <v-dialog v-model="showCreateDialog" max-width="600" persistent>
                <v-card class="create-task-dialog">
                    <v-card-title class="dialog-title">
                        <span class="text-h5">Create New Task</span>
                        <v-btn icon="mdi-close" variant="text" size="small" @click="closeCreateDialog"></v-btn>
                    </v-card-title>

                    <v-divider></v-divider>

                    <v-card-text class="dialog-content">
                        <v-text-field v-model="newTaskForm.title" label="Title" variant="outlined" density="comfortable"
                            placeholder="Enter task title" class="mb-4" :rules="[v => !!v || 'Title is required']"
                            required></v-text-field>
                        <task-form v-model:form="newTaskForm" />
                    </v-card-text>

                    <v-divider></v-divider>

                    <v-card-actions class="dialog-actions">
                        <v-spacer></v-spacer>
                        <v-btn color="grey-darken-1" variant="text" @click="closeCreateDialog">
                            Cancel
                        </v-btn>
                        <v-btn color="primary" :loading="isCreating" @click="handleCreateTask">
                            Create Task
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog> -->
        </v-container>

        <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
            {{ snackbar.text }}
        </v-snackbar>
    </dashboard-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTaskStore } from '@/stores/tasks'
import { useThemeStore } from '@/stores/theme'
import DashboardLayout from '@/components/DashboardLayout.vue'
import TaskItem from '@/components/task/TaskItem.vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorAlert from '@/components/ErrorAlert.vue'
import EmptyState from '@/components/EmptyState.vue'
import DebugPanel from '@/components/DebugPanel.vue'
import TaskForm from '@/components/task/TaskForm.vue'
import TaskEditDialog from '@/components/task/TaskEditDialog.vue'


import { Status, Priority } from '@/types/task'

const router = useRouter()
const authStore = useAuthStore()
const taskStore = useTaskStore()
const themeStore = useThemeStore()

const cardHoverBgColor = computed(() =>
    themeStore.isDark ? '#424242' : '#f5f5f5'
)

const showCreateDialog = ref(false)
const isCreating = ref(false)
const newTaskForm = ref({
    title: '',
    description: '',
    status: Status.Pending,
    priority: Priority.Medium,
    category: '',
    tags: [],
    dueDate: new Date().toISOString().split('T')[0]
})

const snackbar = ref({
    show: false,
    text: '',
    color: 'success'
})

function handleLogout() {
    authStore.logout()
    router.push('/login')
}

function openCreateTaskDialog() {
    showCreateDialog.value = true;
}

async function handleCreateTask() {
    try {
        console.log('[HomeView] Creating task:', newTaskForm.value)
        isCreating.value = true
        await taskStore.createTask(newTaskForm.value)
        showCreateDialog.value = false
        handleSnackbar({ text: 'Task created successfully', color: 'success' })
    } catch (error) {
        console.error('[HomeView] Create task failed:', error)
        handleSnackbar({ text: 'Failed to create task', color: 'error' })
    } finally {
        isCreating.value = false
    }
}

function closeCreateDialog() {
    showCreateDialog.value = false
    newTaskForm.value = {
        title: '',
        description: '',
        status: Status.Pending,
        priority: Priority.Medium,
        category: '',
        tags: [],
        dueDate: new Date().toISOString().split('T')[0]
    }
}

function handleSnackbar(data: { text: string; color: string }) {
    snackbar.value.text = data.text
    snackbar.value.color = data.color
    snackbar.value.show = true
}

function handleTaskSaved(task: any) {
  handleSnackbar({ text: 'Task created successfully', color: 'success' })
}

function handleError(message: string) {
  handleSnackbar({ text: message, color: 'error' })
}

onMounted(async () => {
    try {
        await taskStore.fetchTasks()
    } catch (error) {
        console.error('Error in HomeView:', error)
    }
})
</script>

<style scoped>
/* Remove the general card hover effect */
.v-card {
    transition: all 0.2s ease;
}

/* Only apply hover effect to task list items */
.v-list .v-list-item .v-card:hover {
    background-color: v-bind(cardHoverBgColor) !important;
}

/* Dialog styling */
.create-task-dialog {
    background-color: rgb(var(--v-theme-surface)) !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
}

.v-theme--dark .create-task-dialog {
    background-color: rgb(var(--v-theme-surface-dark)) !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

:deep(.v-dialog__content) {
    backdrop-filter: blur(4px);
    background-color: rgba(0, 0, 0, 0.3);
}

:deep(.v-overlay__scrim) {
    background: rgba(0, 0, 0, 0.3) !important;
    opacity: 1 !important;
}

/* Enhanced dialog styling */
.create-task-dialog {
    background-color: rgb(var(--v-theme-background)) !important;
    border-radius: 8px;
    overflow: hidden;
}

.v-theme--dark .create-task-dialog {
    background-color: rgb(var(--v-theme-surface)) !important;
}

.dialog-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background-color: rgb(var(--v-theme-surface));
}

.dialog-content {
    padding: 24px;
    background-color: rgb(var(--v-theme-background));
}

.dialog-actions {
    padding: 16px 24px;
    background-color: rgb(var(--v-theme-surface));
}

:deep(.v-overlay__content) {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
    border: 1px solid rgba(var(--v-theme-on-surface), 0.05);
}

:deep(.v-overlay__scrim) {
    backdrop-filter: blur(8px);
    background-color: rgba(0, 0, 0, 0.25) !important;
    opacity: 1 !important;
}

.v-theme--dark :deep(.v-overlay__scrim) {
    background-color: rgba(0, 0, 0, 0.45) !important;
}
</style>