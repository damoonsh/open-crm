<template>
    <v-row>
        <v-col cols="12">
            <v-textarea v-model="localForm.description" density="compact" variant="outlined" hide-details class="mb-4"
                label="Description" @input="emitUpdate"></v-textarea>
        </v-col>

        <v-col cols="12" sm="6">
            <v-select v-model="localForm.status" :items="statusOptions" label="Status" density="compact" class="mb-2"
                @update:model-value="emitUpdate"></v-select>
        </v-col>

        <v-col cols="12" sm="6">
            <v-select v-model="localForm.priority" :items="priorityOptions" label="Priority" density="compact"
                class="mb-2" @update:model-value="emitUpdate"></v-select>
        </v-col>

        <v-col cols="12" sm="6">
            <v-select v-model="localForm.category" :items="categoryOptions" label="Category" density="compact"
                class="mb-2" @update:model-value="emitUpdate">
                <template v-slot:selection="{ item }">
                    <v-icon :color="getCategoryConfig(item.title).color" class="mr-2">
                        {{ getCategoryConfig(item.title).icon }}
                    </v-icon>
                    {{ item.title }}
                </template>
            </v-select>
        </v-col>

        <v-col cols="12" sm="6">
            <v-text-field v-model="localForm.dueDate" type="date" label="Due Date" density="compact" class="mb-2"
                @update:model-value="emitUpdate"></v-text-field>
        </v-col>

        <v-col cols="12">
            <v-combobox v-model="localForm.tags" :items="availableTags" label="Tags" multiple chips closable-chips
                density="compact" @update:model-value="emitUpdate">
                <template v-slot:chip="{ props, item }">
                    <v-chip v-bind="props" :prepend-icon="getTagIcon(item.raw)" closable>
                        {{ item.raw }}
                    </v-chip>
                </template>
            </v-combobox>
        </v-col>
    </v-row>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Status, Priority } from '@/types/task'
import { categoryConfigs } from '@/utils/categoryConfig'
import { getTagIcon } from '@/utils/tagIcons'
import type { TaskEditForm } from '@/types/task'

const props = defineProps<{
    form: TaskEditForm
}>()

const emit = defineEmits<{
    (e: 'update:form', value: TaskEditForm): void
}>()

const localForm = ref<TaskEditForm>({ ...props.form })

const statusOptions = Object.entries(Status)
    .filter(([key]) => !isNaN(Number(key)))
    .map(([value, label]) => ({
        title: label,
        value: Number(value)
    }))

const priorityOptions = Object.entries(Priority)
    .filter(([key]) => !isNaN(Number(key)))
    .map(([value, label]) => ({
        title: label,
        value: Number(value)
    }))

const categoryOptions = Object.keys(categoryConfigs)

const availableTags = [
    'frontend', 'backend', 'urgent', 'api', 'database',
    'ui', 'ux', 'testing', 'security', 'feature', 'bug'
]

function getCategoryConfig(category: string) {
    return categoryConfigs[category] || { icon: 'mdi-folder', color: 'grey' }
}

function emitUpdate() {
    emit('update:form', { ...localForm.value })
}

watch(() => props.form, (newForm) => {
    localForm.value = { ...newForm }
}, { deep: true })
</script>