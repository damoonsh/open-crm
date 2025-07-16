<template>
    <div class="d-flex align-center" style="flex-grow: 1">
        <template v-if="isEditing">
            <v-text-field v-model="localTitle" density="compact" variant="outlined" hide-details class="mr-2"
                label="Title" @update:model-value="$emit('update:title', $event)"></v-text-field>
        </template>
        <template v-else>
            <span class="text-h6">{{ task.title }}</span>
        </template>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Task } from '@/types/task'

const props = defineProps<{
    task: Task
    isEditing: boolean
    title: string
}>()

defineEmits<{
    (e: 'update:title', value: string): void
}>()

const localTitle = ref(props.title)

watch(() => props.title, (newTitle) => {
    localTitle.value = newTitle
})
</script>

<style scoped>
.text-h6 {
    word-break: break-word;
    line-height: 1.4;
}
</style>