<template>
    <v-chip :color="getCategoryConfig(category).color" size="small" class="mr-2">
        <template v-slot:prepend>
            <v-icon size="small">
                {{ getCategoryConfig(category).icon }}
            </v-icon>
        </template>
        {{ category }}
    </v-chip>
</template>

<script setup lang="ts">
import { categoryConfigs } from '@/utils/categoryConfig'

defineProps<{
    category: string
}>()

function getCategoryConfig(category: string) {
    return categoryConfigs[category] || { icon: 'mdi-folder', color: 'grey' }
}
</script>