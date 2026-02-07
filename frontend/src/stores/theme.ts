import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// 主题状态管理 Store
export const useThemeStore = defineStore('theme', () => {
  // 从 localStorage 获取主题，默认为 light (浅色模式)
  const theme = ref(localStorage.getItem('starbase_theme') || 'light')

  // 应用主题到 DOM
  const applyTheme = (val: string) => {
    // 设置 html 标签的 data-theme 属性，配合 CSS 变量实现主题切换
    document.documentElement.setAttribute('data-theme', val)
    // 同时切换 class="dark"，以支持 UnoCSS 的 dark: 前缀
    if (val === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 初始化时应用主题
  applyTheme(theme.value)

  // 切换主题函数
  const toggle = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  // 监听主题变化，持久化到 localStorage
  watch(theme, (val) => {
    localStorage.setItem('starbase_theme', val)
    applyTheme(val)
  })

  return { theme, toggle }
})
