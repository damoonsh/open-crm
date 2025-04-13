<template>
    <v-container class="d-flex justify-center align-center" style="min-height: 200px">
        <v-progress-circular indeterminate color="primary" size="64">
            <template v-slot:default>
                <v-icon>mdi-refresh</v-icon>
            </template>
        </v-progress-circular>
    </v-container>
</template>