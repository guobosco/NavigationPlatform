<script setup lang="ts">
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

<template>
  <!-- 主题切换按钮 -->
  <button @click="themeStore.toggle()" class="icon-btn text-xl p-2" title="切换主题">
    <!-- 暗色模式显示月亮图标 -->
    <div v-if="themeStore.theme === 'dark'" class="i-mdi-weather-night" />
    <!-- 亮色模式显示太阳图标 -->
    <div v-else class="i-mdi-white-balance-sunny text-orange-500" />
  </button>
</template>
