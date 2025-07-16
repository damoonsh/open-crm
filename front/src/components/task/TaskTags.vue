<template>
    <v-chip-group v-if="tags?.length">
        <v-chip v-for="tag in tags" :key="tag" :prepend-icon="getTagIcon(tag)" color="grey-lighten-3" small>
            {{ tag }}
        </v-chip>
    </v-chip-group>
</template>

<script setup lang="ts">
import { getTagIcon } from '@/utils/tagIcons'

defineProps<{
    tags?: string[]
}>()
</script>