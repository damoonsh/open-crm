import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: false
  }),

  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
    },

    setTheme(isDark: boolean) {
      this.isDark = isDark
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'theme',
        storage: localStorage
      }
    ]
  }
})