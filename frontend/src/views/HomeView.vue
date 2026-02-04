<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import CardSystem from '../components/Card_System_v2.vue'

const apps = ref<any[]>([])
const loading = ref(true)
const activeCategory = ref('all')

const categories = [
  { id: 'all', label: '全部' },
  { id: 'web', label: '行政办公' },
  { id: 'desktop', label: '业务系统' },
  { id: 'mobile', label: '资源数据' },
  { id: 'service', label: '开发工具' },
  { id: 'data', label: '监控运维' }, // Mapping might be loose, adjusting to requirement text vs enum
]
// Mapping Enum to UI Tabs:
// The enum is web, desktop, mobile, service, data, other.
// The design image tabs: "All, Admin(Admin Office?), Business Systems, Resource Data, Dev Tools, Monitor Ops".
// I'll map them:
// web -> Admin Office
// desktop -> Business Systems
// data -> Resource Data
// service -> Dev Tools
// other -> Monitor Ops (maybe?)
// Let's stick to Enum for filtering to be safe, or allow mapping.
// "Category ENUM('web','desktop','mobile','service','data','other')"

const tabs = [
  { id: 'all', label: '全部' },
  { id: 'web', label: '行政办公' },
  { id: 'desktop', label: '业务系统' },
  { id: 'data', label: '资源数据' },
  { id: 'service', label: '开发工具' },
  { id: 'other', label: '监控运维' },
]

onMounted(async () => {
  try {
    const res = await fetch('/api/apps')
    if (res.ok) {
      apps.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

const filteredApps = computed(() => {
  if (activeCategory.value === 'all') return apps.value
  return apps.value.filter(app => app.category === activeCategory.value)
})
</script>

<template>
  <div>
    <!-- Tabs -->
    <div class="flex flex-wrap gap-2 mb-8 justify-center sm:justify-start">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeCategory = tab.id"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
        :class="activeCategory === tab.id ? 'bg-primary text-white shadow-lg shadow-primary/30' : 'bg-[var(--card-bg)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-[var(--border-color)]'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Grid -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="i-mdi-loading animate-spin text-4xl text-primary" />
    </div>
    
    <div v-else-if="filteredApps.length === 0" class="text-center py-20 text-[var(--text-secondary)]">
      <div class="i-mdi-rocket-off text-6xl mb-4 opacity-50 mx-auto" />
      <p>暂无相关系统</p>
    </div>
    
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <CardSystem v-for="app in filteredApps" :key="app.id" :app="app" />
    </div>
  </div>
</template>
