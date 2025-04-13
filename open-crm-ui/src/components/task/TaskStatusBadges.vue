<template>
    <div class="d-flex align-center">
        <v-chip v-if="status" :color="getStatusColor(status)" class="mr-2" small>
            {{ getStatusText(status) }}
        </v-chip>
        <v-chip v-if="priority" :color="getPriorityColor(priority)" small>
            {{ getPriorityText(priority) }}
        </v-chip>
    </div>
</template>

<script setup lang="ts">
// Keep the enum import if needed for mapping, or remove if directly using strings
import { Status, Priority } from '@/types/task'

const props = defineProps<{
    status: string | null // Accept string or null
    priority: string | null // Accept string or null
}>()

// Helper function to normalize API string (e.g., "IN_PROGRESS" -> "InProgress")
// Adjust this based on the exact format your API returns
function normalizeEnumString(str: string | null): string | null {
    if (!str) return null;
    // Example: Converts "IN_PROGRESS" to "InProgress" or "PENDING" to "Pending"
    return str.toLowerCase().replace(/_([a-z])/g, (match, letter) => letter.toUpperCase())
        .replace(/^\w/, c => c.toUpperCase());
}


function getStatusColor(statusStr: string | null): string {
    if (!statusStr) return 'grey';
    // Use string keys matching the enum *names* or the API response strings
    const colors: { [key: string]: string } = {
        // Assuming API returns uppercase strings like "PENDING"
        'PENDING': 'warning',
        'IN_PROGRESS': 'info', // Adjust key based on actual API response
        'COMPLETED': 'success',
        'ON_HOLD': 'grey',
        'CANCELLED': 'error',
        // Add lowercase/normalized versions if API format varies
        'Pending': 'warning',
        'InProgress': 'info',
        'Completed': 'success',
        'OnHold': 'grey',
        'Cancelled': 'error'
    }
    return colors[statusStr] || 'grey'
}

function getPriorityColor(priorityStr: string | null): string {
    if (!priorityStr) return 'grey';
    // Use string keys matching the enum *names* or the API response strings
    const colors: { [key: string]: string } = {
        // Assuming API returns uppercase strings like "LOW"
        'LOW': 'success',
        'MEDIUM': 'blue',
        'HIGH': 'warning',
        'URGENT': 'error',
        // Add lowercase/normalized versions if API format varies
        'Low': 'success',
        'Medium': 'blue',
        'High': 'warning',
        'Urgent': 'error'
    }
    return colors[priorityStr] || 'grey'
}

function getStatusText(statusStr: string | null): string {
    // Return the string directly, potentially formatting it (e.g., replace underscores)
    return statusStr ? statusStr.replace('_', ' ') : '';
}

function getPriorityText(priorityStr: string | null): string {
    // Return the string directly, potentially formatting it
    return priorityStr ? priorityStr.replace('_', ' ') : '';
}
</script>