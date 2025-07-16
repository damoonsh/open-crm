<template>
    <v-app :theme="themeStore.isDark ? 'dark' : 'light'">
        <v-app-bar color="primary" elevation="2">
            <v-container class="d-flex align-center">
                <v-toolbar-title class="text-h6 font-weight-bold">Dashboard</v-toolbar-title>
                <v-spacer></v-spacer>

                <v-btn icon class="mr-4" @click="themeStore.toggleTheme">
                    <v-icon>{{ themeStore.isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
                </v-btn>

                <v-btn color="logout" variant="tonal" class="font-weight-medium text-white" prepend-icon="mdi-logout"
                    @click="$emit('logout')">
                    Logout
                </v-btn>
            </v-container>
        </v-app-bar>

        <v-main :class="themeStore.isDark ? 'bg-grey-darken-3' : 'bg-grey-lighten-4'">
            <v-container>
                <slot></slot>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

defineEmits(['logout'])
const themeStore = useThemeStore()
</script>

<style scoped>
.text-white {
    color: white !important;
}
</style>