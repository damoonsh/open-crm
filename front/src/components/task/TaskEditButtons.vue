<template>
    <div class="d-flex align-center">
        <template v-if="isEditing">
            <v-btn icon="mdi-check" size="small" color="success" class="ml-2" @click="$emit('save')"></v-btn>
            <v-btn icon="mdi-close" size="small" color="error" class="ml-2" @click="$emit('cancel')"></v-btn>
        </template>
        <template v-else>
            <v-btn icon="mdi-pencil" size="small" variant="text" class="ml-2" @click="$emit('edit')"></v-btn>
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" class="ml-2"
                @click="handleDelete"></v-btn>
        </template>

        <v-dialog v-model="showDeleteDialog" max-width="300">
            <v-card>
                <v-card-title class="text-h6">Delete Task</v-card-title>
                <v-card-text>Are you sure you want to delete this task?</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="grey" variant="text" @click="showDeleteDialog = false">Cancel</v-btn>
                    <v-btn color="error" variant="elevated" @click="$emit('delete')">Delete</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
    isEditing: boolean
}>()

defineEmits<{
    (e: 'save'): void
    (e: 'cancel'): void
    (e: 'edit'): void
    (e: 'delete'): void
}>()

const showDeleteDialog = ref(false)

function handleDelete() {
    showDeleteDialog.value = true
}
</script>