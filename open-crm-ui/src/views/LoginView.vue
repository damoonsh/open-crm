<template>
  <v-app>
    <v-main class="auth-background">
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="4">
            <v-card class="elevation-6 pa-6" rounded="lg">
              <v-card-title class="text-h5 font-weight-bold primary--text text-center">
                Sign In
              </v-card-title>

              <v-card-text>
                <v-alert v-if="error" type="error" dense text class="mb-4">
                  {{ error }}
                </v-alert>

                <v-form @submit.prevent="handleLogin" ref="form">
                  <v-text-field v-model="username" label="Username" prepend-inner-icon="mdi-account" outlined dense
                    required :disabled="loading" class="mb-4"
                    :rules="[v => !!v || 'Username is required']"></v-text-field>

                  <v-text-field v-model="password" label="Password" prepend-inner-icon="mdi-lock"
                    :type="showPassword ? 'text' : 'password'" :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append="showPassword = !showPassword" outlined dense required :disabled="loading"
                    :rules="[v => !!v || 'Password is required']"></v-text-field>

                  <v-btn type="submit" color="primary" block large :loading="loading" :disabled="loading" class="mt-6">
                    {{ loading ? 'Signing in...' : 'Sign In' }}
                  </v-btn>
                </v-form>
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
const password = ref('')
const loading = ref(false)
const showPassword = ref(false)
const error = computed(() => authStore.error)
const form = ref(null)

async function handleLogin() {
  if (!username.value || !password.value) return

  loading.value = true
  console.log('[Login] Attempting login with username:', username.value)

  try {
    // Display the username/password being used (for debugging)
    console.log(`[Login Debug] Using credentials - Username: ${username.value.trim()}, Password: ${password.value.trim()}`)

    const success = await authStore.login(
      username.value.trim(),
      password.value.trim()
    )

    console.log('[Login] Login response result:', success)

    if (success) {
      console.log('[Login] Authentication successful, navigating to home...')
      await router.push({ name: 'home' })
      console.log('[Login] Navigation complete')
    } else {
      // If login failed but no error was set, set a generic one
      if (!authStore.error) {
        authStore.error = "Login failed. Please check your credentials and try again."
      }
      console.error('[Login] Authentication failed:', authStore.error)
    }
  } catch (error: any) {
    console.error('[Login] Exception during login:', error)
    authStore.error = error.message || "An unexpected error occurred"
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