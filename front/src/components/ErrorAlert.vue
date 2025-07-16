<template>
    <v-alert type="error" variant="tonal" closable class="mb-4">
        <template v-slot:prepend>
            <v-icon icon="mdi-alert-circle" />
        </template>

        <div class="d-flex flex-column">
            <span class="text-h6">Error Loading Tasks</span>
            <span class="text-body-2">{{ error }}</span>
        </div>

        <template v-slot:append>
            <v-btn color="error" variant="text" @click="$emit('retry')">
                Retry
                <v-icon end icon="mdi-refresh" />
            </v-btn>
        </template>
    </v-alert>
</template>

<script setup lang="ts">
defineProps<{
    error: string
}>()

defineEmits<{
    (e: 'retry'): void
}>()
</script>