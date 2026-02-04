<script setup lang="ts">
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

<template>
  <button @click="themeStore.toggle()" class="icon-btn text-xl p-2" title="切换主题">
    <div v-if="themeStore.theme === 'dark'" class="i-mdi-weather-night" />
    <div v-else class="i-mdi-white-balance-sunny text-orange-500" />
  </button>
</template>
