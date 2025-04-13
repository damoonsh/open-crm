<template>
    <dashboard-layout>
        <v-container>
            <v-row justify="center">
                <v-col cols="12" md="10" lg="8">
                    <v-btn class="mb-4" @click="router.back()" variant="text" prepend-icon="mdi-arrow-left">
                        Back to Tasks
                    </v-btn>

                    <!-- Use taskStore loading/error states -->
                    <v-card v-if="taskStore.loading" flat>
                        <loading-state />
                    </v-card>

                    <v-card v-else-if="taskStore.error && !taskToDisplay" flat>
                        <!-- Show error only if task isn't loaded -->
                        <error-alert :error="taskStore.error" @retry="loadTask" />
                    </v-card>

                    <!-- Use taskToDisplay computed property -->
                    <v-card v-else-if="taskToDisplay" class="pa-6">
                        <!-- Top row: Title and Icon Buttons -->
                        <v-card-title class="d-flex justify-space-between align-center">
                            <span class="text-h5 font-weight-bold">{{ taskToDisplay.title }}</span>
                            <div>
                                <v-btn icon color="primary" @click="editTask">
                                    <v-icon>mdi-pencil</v-icon>
                                </v-btn>
                                <v-btn icon color="error" @click="deleteTask">
                                    <v-icon>mdi-delete</v-icon>
                                </v-btn>
                            </div>
                        </v-card-title>

                        <!-- Due Date and metadata row -->
                        <v-card-subtitle v-if="taskToDisplay.dueDate" class="mt-2">
                            Due: {{ formatDate(taskToDisplay.dueDate) }}
                        </v-card-subtitle>
                        <v-row class="mt-2" align="center">
                            <v-col cols="auto">
                                <task-status-badges :status="taskToDisplay.status" :priority="taskToDisplay.priority" />
                            </v-col>
                            <v-col cols="auto" v-if="taskToDisplay.category">
                                <task-category :category="taskToDisplay.category" />
                            </v-col>
                            <v-col cols="auto">
                                <task-tags :tags="taskToDisplay.tags" />
                            </v-col>
                        </v-row>

                        <!-- Description below -->
                        <v-card-text class="mt-4">
                            <div><strong>Description:</strong></div>
                            <div>{{ taskToDisplay.description || 'No description' }}</div>
                        </v-card-text>
                    </v-card>
                    <div v-else>
                        Task not found.
                    </div>

                    <!-- Comments Component - Pass taskId -->
                    <comments v-if="taskId" :task-id="taskId" :comments="comments" class="mt-6" />
                </v-col>
            </v-row>
        </v-container>

        <!-- Pass taskToDisplay to the edit dialog -->
        <task-edit-dialog :show-dialog="showEditDialog" :task="taskToDisplay" :is-edit-mode="true"
            @update:show-dialog="showEditDialog = $event" @task-saved="handleTaskSaved" @error="handleError" />

        <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
            {{ snackbar.text }}
        </v-snackbar>
    </dashboard-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/tasks'
import type { Task } from '@/types/task'; // Import Task type if not already
import DashboardLayout from '@/components/DashboardLayout.vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorAlert from '@/components/ErrorAlert.vue'
import TaskEditDialog from '@/components/task/TaskEditDialog.vue'
import TaskTags from '@/components/task/TaskTags.vue'
import TaskCategory from '@/components/task/TaskCategory.vue'
import TaskStatusBadges from '@/components/task/TaskStatusBadges.vue'
import Comments from '@/components/task/Comments.vue'

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();

// --- Remove local task ref ---
// const task = ref(null)

const showEditDialog = ref(false);
const snackbar = ref({
    show: false,
    text: '',
    color: 'success'
});

const comments = ref([]); // Keep local comments ref for now

// --- Define props with only id ---
const props = defineProps<{
    id: string
}>();

// --- Computed property for the task ID (as number) ---
const taskId = computed(() => {
    // Ensure props.id is treated correctly
    const idParam = props.id || route.params.id; // Fallback to route param if prop isn't reliable yet
    const parsedId = typeof idParam === 'string' ? parseInt(idParam, 10) : Number(idParam);
    return isNaN(parsedId) ? null : parsedId; // Return null if invalid
});

// --- Computed property to get the task data from the store ---
const taskToDisplay = computed(() => taskStore.currentTask);

// --- Function to load task data ---
async function loadTask() {
    if (taskId.value === null) { // Check if taskId is valid
        console.error("TaskView: Invalid or missing Task ID.");
        taskStore.error = "Invalid Task ID.";
        taskStore.loading = false; // Ensure loading is stopped
        return;
    }

    // Check if the task in the store matches the route ID
    if (!taskStore.currentTask || taskStore.currentTask.id !== taskId.value) {
        console.log(`TaskView: currentTask mismatch or missing. Fetching task ${taskId.value}...`);
        await taskStore.getTask(taskId.value); // Pass number ID
    } else {
        console.log(`TaskView: Using pre-loaded currentTask for ID ${taskId.value}`);
        if (taskStore.loading) taskStore.loading = false; // Ensure loading is false
    }

    // Fetch comments after task is loaded (if getTaskComments exists)
    // if (taskId.value && typeof taskStore.getTaskComments === 'function') {
    //   try {
    //     comments.value = await taskStore.getTaskComments(taskId.value);
    //   } catch (error) {
    //     console.error('Error fetching comments:', error);
    //   }
    // }
}

function formatDate(date: string | null | undefined): string {
    if (!date) return 'N/A';
    try {
        return new Date(date).toLocaleDateString();
    } catch (e) {
        return 'Invalid Date';
    }
}

function editTask() {
    showEditDialog.value = true;
}

async function deleteTask() {
    if (taskToDisplay.value && confirm('Are you sure you want to delete this task?')) {
        try {
            // Ensure taskToDisplay.value.id is a number if deleteTask expects number
            const idToDelete = typeof taskToDisplay.value.id === 'string'
                ? parseInt(taskToDisplay.value.id, 10)
                : taskToDisplay.value.id;
            if (isNaN(idToDelete)) {
                handleError('Invalid task ID for deletion.');
                return;
            }
            await taskStore.deleteTask(idToDelete); // Assuming deleteTask exists and takes number ID
            handleSnackbar({ text: 'Task deleted successfully', color: 'success' });
            router.push('/');
        } catch (error: any) {
            console.error('Error deleting task:', error);
            handleError(error.message || 'Failed to delete task.');
        }
    }
}

// Use taskStore.currentTask after it's updated by getTask or edit dialog
function handleTaskSaved(updatedTask: Task) {
    // The store should ideally update currentTask itself,
    // but we can force it here if needed, or just rely on store reactivity
    // taskStore.currentTask = updatedTask; // Or let the store handle it
    handleSnackbar({ text: 'Task updated successfully', color: 'success' });
    showEditDialog.value = false; // Close dialog on save
}

function handleError(message: string) {
    handleSnackbar({ text: message, color: 'error' });
}

function handleSnackbar(data: { text: string; color: string }) {
    snackbar.value.text = data.text;
    snackbar.value.color = data.color;
    snackbar.value.show = true;
}

// Load data when component mounts
onMounted(loadTask);

// Watch for changes in taskId (if user navigates between tasks)
watch(taskId, (newId, oldId) => {
    if (newId !== null && newId !== oldId) {
        loadTask();
    }
});

// Optional: Clear currentTask when leaving the view
// import { onUnmounted } from 'vue';
// onUnmounted(() => {
//   taskStore.currentTask = null;
// });
</script>