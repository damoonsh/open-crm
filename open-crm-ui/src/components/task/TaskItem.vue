<template>
    <v-card width="100%" variant="outlined" :class="[rowBackgroundClass]"
     hover>
        <v-card-title class="d-flex justify-space-between align-center">
            <task-title :task="task" :is-editing="isEditing" v-model:title="editFormData.title" @click="handleCardClick" hover/>

            <div class="d-flex align-center">
                <task-status-badges :status="task.status" :priority="task.priority" />
                <task-edit-buttons :is-editing="isEditing" @save="saveChanges" @cancel="cancelEdit" @edit="startEdit"
                    @delete="handleDelete" />
            </div>
        </v-card-title>

        <v-card-text>
            <task-form v-if="isEditing" v-model:form="editFormData" />
            <template v-else>
                <p class="mb-4">{{ task.description }}</p>
                <v-row>
                    <v-col cols="12" sm="6">
                        <task-tags :tags="task.tags" />
                    </v-col>
                    <v-col cols="12" sm="6" class="d-flex justify-end">
                        <task-category v-if="task.category" :category="task.category" />
                        <task-due-date :date="formattedDueDate" />
                    </v-col>
                </v-row>
            </template>
        </v-card-text>
    </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import { useThemeStore } from '@/stores/theme'
import { useRouter } from 'vue-router' 
import TaskTitle from './TaskTitle.vue'
import TaskStatusBadges from './TaskStatusBadges.vue'
import TaskEditButtons from './TaskEditButtons.vue'
import TaskForm from './TaskForm.vue'
import TaskTags from './TaskTags.vue'
import TaskCategory from './TaskCategory.vue'
import TaskDueDate from './TaskDueDate.vue'
import type { Task, TaskFormData } from '@/types/task'

const props = defineProps<{
    task: Task
    index: number
}>()

const taskStore = useTaskStore()
const themeStore = useThemeStore()
const router = useRouter()

const isEditing = ref(false)
const editFormData = ref<TaskFormData>(initializeEditForm())

const formattedDueDate = computed(() => {
    if (!props.task.dueDate) return ''
    const date = new Date(props.task.dueDate)
    return date.toISOString().split('T')[0] // Returns "yyyy-MM-dd"
})

function initializeEditForm(): TaskFormData {
    return {
        title: props.task.title,
        description: props.task.description,
        status: props.task.status,
        priority: props.task.priority,
        category: props.task.category || '',
        tags: props.task.tags || [],
        dueDate: props.task.dueDate || new Date().toISOString().split('T')[0]
    }
}

const rowBackgroundClass = computed(() => {
    if (themeStore.isDark) {
        return props.index % 2 === 0 ? 'bg-grey-darken-3' : 'bg-grey-darken-4'
    }
    return props.index % 2 === 0 ? 'bg-grey-lighten-4' : 'bg-white'
})

function startEdit() {
    editFormData.value = initializeEditForm()
    isEditing.value = true
}

function cancelEdit() {
    isEditing.value = false
}

function handleCardClick() {  
    isEditing.value = false   
    router.push(`/task/${props.task.id}`)  
}

async function saveChanges() {
    try {
        await taskStore.updateTask(props.task.id, editFormData.value)
        isEditing.value = false
    } catch (error) {
        console.error('Failed to update task:', error)
    }
}

async function handleDelete() {
    console.log('[TaskItem] Deleting task:', props.task.id)
    try {
        await taskStore.deleteTask(props.task.id)
        console.log('[TaskItem] Task deleted successfully')
    } catch (error) {
        console.error('[TaskItem] Failed to delete task:', error)
    }
}
</script>

<style scoped>
.v-card {
    transition: all 0.2s ease;
}

.v-card:hover {
    background-color: v-bind(themeStore.isDark ? '#424242' : '#f5f5f5') !important;
}
</style>