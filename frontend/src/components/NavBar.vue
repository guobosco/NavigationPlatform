<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ThemeToggle from './ThemeToggle.vue'

const title = ref('办公网网信系统融合应用平台')
const slogan = ref('')

// 挂载时获取系统配置（标题和标语）
onMounted(async () => {
  try {
    const res = await fetch('/api/config')
    if (res.ok) {
      const data = await res.json()
      title.value = data.title
      slogan.value = data.slogan
    } else {
       throw new Error('API request failed')
    }
  } catch (e) {
    console.warn('API不可用，使用默认配置')
    // 默认 Mock 配置
    title.value = '办公网网信系统融合应用平台'
    slogan.value = '打造网信系统开发、发布、推广应用的开放平台 (离线模式)'
  }
})
</script>

<template>
  <!-- 导航栏：透明背景，磨砂效果，底部边框取消或变淡 -->
  <!-- 使用 CSS 变量 var(--bg-primary) 的 RGB 值来实现半透明背景，或者直接使用 dark:bg-slate-900 -->
  <nav class="sticky top-0 z-50 bg-white/80 dark:bg-[#0f172a]/90 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800/50 transition-all duration-300">
    <div class="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-14"> <!-- 减小高度 -->
        <div class="flex items-center gap-4">
          <!-- Logo 和标题 -->
          <router-link to="/" class="flex items-center gap-2 group">
            <div class="i-mdi-rocket-launch text-xl text-[var(--primary-color)]" />
            <span class="font-bold text-base tracking-wide text-[var(--text-primary)]">{{ title }}</span>
          </router-link>
        </div>
        
        <!-- 右侧操作栏 -->
        <div class="flex items-center gap-3">
          <router-link to="/submit" class="text-xs font-medium text-[var(--text-secondary)] hover:text-[var(--primary-color)] transition-colors flex items-center gap-1">
            <div class="i-mdi-plus" /> 发布
          </router-link>
          <div class="h-3 w-px bg-gray-300 dark:bg-gray-700 mx-1"></div>
          <ThemeToggle />
          <router-link to="/admin" class="icon-btn text-lg text-[var(--text-secondary)] hover:text-[var(--primary-color)]" title="管理员后台">
            <div class="i-mdi-shield-account-outline" />
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>
