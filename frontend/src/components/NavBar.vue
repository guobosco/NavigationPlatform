<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ThemeToggle from './ThemeToggle.vue'

const title = ref('办公网网信系统融合应用平台')
const slogan = ref('')

onMounted(async () => {
  try {
    const res = await fetch('/api/config')
    if (res.ok) {
      const data = await res.json()
      title.value = data.title
      slogan.value = data.slogan
    }
  } catch (e) {
    console.error(e)
  }
})
</script>

<template>
  <nav class="border-b border-[var(--border-color)] bg-[var(--bg-primary)]/80 backdrop-blur-md sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center gap-4">
          <router-link to="/" class="flex items-center gap-2">
            <div class="i-mdi-rocket-launch text-2xl text-primary" />
            <span class="font-bold text-lg tracking-wide">{{ title }}</span>
          </router-link>
          <span v-if="slogan" class="hidden md:block text-xs text-[var(--text-secondary)] border-l border-[var(--border-color)] pl-4">{{ slogan }}</span>
        </div>
        <div class="flex items-center gap-4">
          <router-link to="/submit" class="text-sm hover:text-primary transition-colors">我要发布新系统</router-link>
          <ThemeToggle />
          <router-link to="/admin" class="icon-btn text-xl" title="管理员后台">
            <div class="i-mdi-shield-account" />
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>
