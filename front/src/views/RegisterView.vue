<template>
    <v-app>
        <v-main class="auth-background">
            <v-container class="fill-height" fluid>
                <v-row align="center" justify="center">
                    <v-col cols="12" sm="8" md="4">
                        <v-card class="elevation-6 pa-6" rounded="lg">
                            <v-card-title class="text-h5 font-weight-bold primary--text text-center">
                                Register
                            </v-card-title>

                            <v-card-text>
                                <v-alert v-if="error" type="error" dense text class="mb-4">
                                    {{ error }}
                                </v-alert>

                                <v-form @submit.prevent="handleRegister" ref="form">
                                    <v-text-field v-model="username" label="Username" prepend-inner-icon="mdi-account"
                                        outlined dense required :disabled="loading" class="mb-4"
                                        :rules="[v => !!v || 'Username is required']"></v-text-field>

                                    <v-text-field v-model="email" label="Email" type="email"
                                        prepend-inner-icon="mdi-email" outlined dense required :disabled="loading"
                                        class="mb-4"
                                        :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'Email must be valid']"></v-text-field>

                                    <v-text-field v-model="password" label="Password" prepend-inner-icon="mdi-lock"
                                        :type="showPassword ? 'text' : 'password'"
                                        :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                                        @click:append="showPassword = !showPassword" outlined dense required
                                        :disabled="loading"
                                        :rules="[v => !!v || 'Password is required']"></v-text-field>

                                    <v-text-field v-model="confirmPassword" label="Confirm Password"
                                        prepend-inner-icon="mdi-lock" :type="showPassword ? 'text' : 'password'"
                                        outlined dense required :disabled="loading" :rules="[
                                            v => !!v || 'Confirm Password is required',
                                            v => v === password || 'Passwords must match'
                                        ]"></v-text-field>

                                    <v-btn type="submit" color="primary" block large :loading="loading"
                                        :disabled="loading" class="mt-6">
                                        {{ loading ? 'Registering...' : 'Register' }}
                                    </v-btn>
                                </v-form>

                                <div class="text-center mt-4">
                                    <router-link to="/login" class="text-decoration-none">
                                        Already have an account? 
                                        <v-btn text color="primary">
                                            Sign In
                                        </v-btn>
                                    </router-link>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const showPassword = ref(false)
const error = computed(() => authStore.error)
const form = ref(null)

async function handleRegister() {
    if (!username.value || !email.value || !password.value || !confirmPassword.value) return
    if (password.value !== confirmPassword.value) {
        authStore.setError('Passwords do not match')
        return
    }

    loading.value = true
    console.log('[Register] Attempting registration with email:', email.value)

    try {
        const success = await authStore.register({
            username: username.value.trim(),
            email: email.value.trim(),
            password: password.value.trim()
        })

        if (success) {
            console.log('[Register] Registration successful, navigating to home...')
            await router.push({ name: 'Home' })
            console.log('[Register] Navigation complete')
        }
    } catch (error: any) {
        console.error('[Register] Exception during registration:', error)
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.auth-background {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e1e1e 100%);
}

.v-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
}
</style>