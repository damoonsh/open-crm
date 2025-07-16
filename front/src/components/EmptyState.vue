<template>
    <v-container class="d-flex flex-column align-center py-12">
        <v-icon icon="mdi-clipboard-text-outline" size="64" color="grey-lighten-1" class="mb-4" />

        <h3 class="text-h5 text-grey-darken-1 mb-2">
            No Tasks Found
        </h3>

        <p class="text-body-1 text-grey-darken-1 text-center mb-6">
            You don't have any tasks yet. Create your first task to get started.
        </p>

        <v-btn color="primary" prepend-icon="mdi-plus" @click="$emit('create-task')">
            Create New Task
        </v-btn>
    </v-container>
</template>

<script setup lang="ts">
defineEmits<{
    (e: 'create-task'): void
}>()
</script>

<style scoped>
.v-container {
    max-width: 400px;
    margin: 0 auto;
}
</style>