import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(localStorage.getItem('starbase_theme') || 'dark')

  const applyTheme = (val: string) => {
    document.documentElement.setAttribute('data-theme', val)
  }

  // Init
  applyTheme(theme.value)

  const toggle = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  watch(theme, (val) => {
    localStorage.setItem('starbase_theme', val)
    applyTheme(val)
  })

  return { theme, toggle }
})
