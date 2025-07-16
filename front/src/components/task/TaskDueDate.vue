<template>
    <div v-if="date" class="d-flex align-center">
        <v-icon size="small" class="mr-1" :color="getDueDateColor(date)">
            mdi-calendar
        </v-icon>
        <span class="text-caption" :class="getDueDateColor(date)">
            {{ formatDate(date) }}
        </span>
    </div>
</template>

<script setup lang="ts">
import { format, isPast, isToday } from 'date-fns'

const props = defineProps<{
    date: string
}>()

function formatDate(date: string): string {
    return format(new Date(date), 'MMM d, yyyy')
}

function getDueDateColor(date: string): string {
    const dueDate = new Date(date)
    if (isPast(dueDate) && !isToday(dueDate)) return 'error'
    if (isToday(dueDate)) return 'warning'
    return 'success'
}
</script>