<script setup lang="ts">
import NavBar from './components/NavBar.vue'
import { useThemeStore } from './stores/theme'

const themeStore = useThemeStore()
</script>

<template>
  <div class="min-h-screen flex flex-col relative overflow-hidden">
    <!-- SVG Background -->
    <div class="fixed inset-0 z-[-1] pointer-events-none">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="stars" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
            <circle cx="10" cy="10" r="1" :fill="themeStore.theme === 'dark' ? '#4a6fa5' : '#d1d9e6'" opacity="0.5"/>
            <circle cx="50" cy="60" r="1.5" :fill="themeStore.theme === 'dark' ? '#4a6fa5' : '#d1d9e6'" opacity="0.3"/>
            <circle cx="80" cy="30" r="0.8" :fill="themeStore.theme === 'dark' ? '#4a6fa5' : '#d1d9e6'" opacity="0.6"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#stars)" />
        <!-- Orbit Lines -->
        <circle cx="0" cy="100%" r="40%" fill="none" :stroke="themeStore.theme === 'dark' ? 'rgba(74, 111, 165, 0.1)' : 'rgba(209, 217, 230, 0.3)'" stroke-width="1" />
        <circle cx="100%" cy="0" r="30%" fill="none" :stroke="themeStore.theme === 'dark' ? 'rgba(74, 111, 165, 0.1)' : 'rgba(209, 217, 230, 0.3)'" stroke-width="1" />
      </svg>
    </div>

    <NavBar />
    
    <main class="flex-grow container mx-auto px-4 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <footer class="text-center py-6 text-xs text-[var(--text-secondary)] border-t border-[var(--border-color)] mt-8">
      <p>&copy; 2024 航天网信系统. 内部机密，严禁外传.</p>
    </footer>
  </div>
</template>
