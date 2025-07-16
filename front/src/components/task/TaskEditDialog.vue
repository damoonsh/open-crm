<!-- src/components/task/TaskEditDialog.vue -->
<template>
    <v-dialog v-model="internalShowDialog" max-width="600" persistent>
      <v-card class="task-dialog">
        <v-card-title class="dialog-title">
          <span class="text-h5">{{ isEditMode ? 'Edit Task' : 'Create New Task' }}</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialog"></v-btn>
        </v-card-title>
  
        <v-divider></v-divider>
  
        <v-card-text class="dialog-content">
          <v-text-field v-model="internalForm.title" label="Title" variant="outlined" density="comfortable"
            placeholder="Enter task title" class="mb-4" :rules="[v => !!v || 'Title is required']" required></v-text-field>
          <task-form v-model:form="internalForm" />
        </v-card-text>
  
        <v-divider></v-divider>
  
        <v-card-actions class="dialog-actions">
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="closeDialog">
            Cancel
          </v-btn>
          <v-btn color="primary" :loading="isSaving" @click="saveTask">
            {{ isEditMode ? 'Save' : 'Create Task' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup lang="ts">
  import { ref, watch, computed } from 'vue'
  import { useTaskStore } from '@/stores/tasks'
  import TaskForm from './TaskForm.vue'
  import { Status, Priority } from '@/types/task'
  
  const props = defineProps<{
    showDialog: boolean
    task?: any // Optional task object for editing
    isEditMode?: boolean // Determines if it's edit or create mode
  }>()
  
  const emit = defineEmits<{
    (e: 'update:showDialog', value: boolean): void
    (e: 'taskSaved', task: any): void
    (e: 'error', message: string): void
  }>()
  
  const taskStore = useTaskStore()
  
  const internalShowDialog = ref(props.showDialog)
  const isSaving = ref(false)
  const internalForm = ref({
    title: '',
    description: '',
    status: Status.Pending,
    priority: Priority.Medium,
    category: '',
    tags: [],
    dueDate: new Date().toISOString().split('T')[0]
  })
  
  // Sync internal dialog state with prop
  watch(() => props.showDialog, (newVal) => {
    internalShowDialog.value = newVal
    if (newVal && props.isEditMode && props.task) {
      internalForm.value = { ...props.task } // Populate form with task data for editing
    } else if (newVal && !props.isEditMode) {
      resetForm() // Reset form for creating
    }
  })
  
  // Sync internal dialog state back to parent
  watch(internalShowDialog, (newVal) => {
    emit('update:showDialog', newVal)
  })
  
  function resetForm() {
    internalForm.value = {
      title: '',
      description: '',
      status: Status.Pending,
      priority: Priority.Medium,
      category: '',
      tags: [],
      dueDate: new Date().toISOString().split('T')[0]
    }
  }
  
  async function saveTask() {
    try {
      isSaving.value = true
      let savedTask
      if (props.isEditMode && props.task?.id) {
        savedTask = await taskStore.updateTask(props.task.id, internalForm.value)
      } else {
        savedTask = await taskStore.createTask(internalForm.value)
      }
      internalShowDialog.value = false
      emit('taskSaved', savedTask)
    } catch (error) {
      console.error('[TaskEditDialog] Save task failed:', error)
      emit('error', 'Failed to save task')
    } finally {
      isSaving.value = false
    }
  }
  
  function closeDialog() {
    internalShowDialog.value = false
    if (!props.isEditMode) resetForm() // Only reset on create mode
  }
  </script>
  
  <style scoped>
  .task-dialog {
    background-color: rgb(var(--v-theme-surface)) !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  }
  
  .v-theme--dark .task-dialog {
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
  
  .task-dialog {
    background-color: rgb(var(--v-theme-background)) !important;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .v-theme--dark .task-dialog {
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