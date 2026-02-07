<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import ThemeToggle from './ThemeToggle.vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const title = ref('办公网网信系统融合应用平台')
const slogan = ref('')
const publishText = ref('发布')

// 计算当前主题
const isDarkMode = computed(() => {
  return document.documentElement.getAttribute('data-theme') === 'dark'
})

// 挂载时获取系统配置（标题和标语）
onMounted(async () => {
  try {
    const res = await fetch('/api/config')
    if (res.ok) {
      const data = await res.json()
      title.value = data.title
      slogan.value = data.slogan
      publishText.value = data.nav_publish_text || '发布'
      // Update document title
      document.title = data.title
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

// Watch title change to update document title
watch(title, (newTitle) => {
  document.title = newTitle
})

const handleLogout = () => {
  userStore.logout()
  router.push('/')
}

const handlePublish = () => {
  if (!userStore.isLoggedIn) {
    if (confirm('发布新系统需要先登录，是否前往登录页面？')) {
      router.push('/admin-login')
    }
    return
  }
  router.push('/submit')
}
</script>

<template>
  <!-- 导航栏：透明背景，磨砂效果，底部边框取消或变淡 -->
  <nav class="sticky top-0 z-50 bg-white/80 dark:bg-[#0f172a]/90 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800/50 transition-all duration-300">
    <div class="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-14"> <!-- 减小高度 -->
        <div class="flex items-center gap-4">
          <!-- Logo 和标题 -->
          <router-link to="/" class="flex items-center gap-2 group">
            <img :src="isDarkMode ? '/satellite-icon-white.svg' : '/satellite-icon.svg'" alt="Logo" class="h-6 w-6" />
            <span class="font-bold text-base tracking-wide text-[var(--text-primary)]">{{ title }}</span>
          </router-link>
          <!-- Slogan Display (Small) -->
          <span v-if="slogan" class="hidden md:block text-xs text-[var(--text-secondary)] border-l border-gray-300 dark:border-gray-700 pl-3 ml-1 truncate max-w-[300px]">
            {{ slogan }}
          </span>
        </div>
        
        <!-- 右侧操作栏 -->
        <div class="flex items-center gap-3">
          <button @click="handlePublish" class="text-xs font-medium text-[var(--text-secondary)] hover:text-[var(--primary-color)] transition-colors flex items-center gap-1">
            <div class="i-mdi-plus" /> {{ publishText }}
          </button>
          
          <div class="h-3 w-px bg-gray-300 dark:bg-gray-700 mx-1"></div>
          
          <ThemeToggle />
          
          <!-- User Menu -->
          <div v-if="userStore.isLoggedIn" class="flex items-center gap-2">
            <div class="text-xs text-[var(--text-secondary)]">
              {{ userStore.user?.username }}
            </div>
            
            <router-link v-if="userStore.isAdmin" to="/admin" class="icon-btn text-lg text-[var(--text-secondary)] hover:text-[var(--primary-color)]" title="管理员后台">
              <div class="i-mdi-shield-account-outline" />
            </router-link>
            
            <router-link v-else to="/user" class="icon-btn text-lg text-[var(--text-secondary)] hover:text-[var(--primary-color)]" title="用户中心">
              <div class="i-mdi-account-outline" />
            </router-link>

            <button @click="handleLogout" class="icon-btn text-lg text-[var(--text-secondary)] hover:text-red-500" title="退出登录">
              <div class="i-mdi-logout" />
            </button>
          </div>

          <div v-else class="flex items-center gap-2">
            <router-link to="/admin-login" class="text-xs font-medium text-[var(--text-secondary)] hover:text-[var(--primary-color)]">
              登录
            </router-link>
          </div>

        </div>
      </div>
    </div>
  </nav>
</template>
