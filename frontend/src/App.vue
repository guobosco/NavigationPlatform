<script setup lang="ts">
import NavBar from './components/NavBar.vue'
import { useThemeStore } from './stores/theme'
import { ref, onMounted } from 'vue'

// 获取主题状态，用于动态调整 SVG 背景颜色
const themeStore = useThemeStore()
const footerCopyright = ref('© 2024 StarBase. All rights reserved.')

onMounted(async () => {
  try {
    const res = await fetch('/api/config')
    if (res.ok) {
      const data = await res.json()
      if (data.footer_copyright) {
        footerCopyright.value = data.footer_copyright
      }
    }
  } catch (e) {
    console.error('Failed to load config', e)
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col relative overflow-hidden bg-[var(--bg-primary)]">
    <!-- SVG 动态背景 - 简化版，去除复杂的星空，保留极简的几何装饰或渐变 -->
    <div class="fixed inset-0 z-0 pointer-events-none opacity-40">
      <!-- 极简的渐变光晕 -->
      <div class="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full bg-[var(--primary-light)] blur-[100px] opacity-20 animate-pulse"></div>
      <div class="absolute bottom-[-10%] left-[-5%] w-[400px] h-[400px] rounded-full bg-purple-300 blur-[80px] opacity-20 dark:opacity-10"></div>
    </div>

    <!-- 顶部导航栏 -->
    <NavBar />
    
    <!-- 主要内容区域 -->
    <main class="flex-grow container mx-auto px-4 py-8 relative z-10">
      <!-- 路由视图，包含过渡动画 -->
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <!-- 页脚 -->
    <footer class="text-center py-6 text-xs text-[var(--text-secondary)] border-t border-[var(--border-color)] mt-8">
      <p>{{ footerCopyright }}</p>
    </footer>
  </div>
</template>
