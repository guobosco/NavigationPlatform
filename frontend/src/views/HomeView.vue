<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import CardSystem from '../components/Card_System_v2.vue'
import ModalCredential from '../components/ModalCredential.vue'
import ModalAdminEdit from '../components/ModalAdminEdit.vue'

// 应用列表数据
const apps = ref<any[]>([])
// 加载状态
const loading = ref(true)
// 当前选中的分类 ID (0 代表全部)
const activeCategory = ref(0)
const categories = ref<any[]>([])

// Layout State
const layoutMode = ref<'compact' | 'cozy'>('compact') // Default to compact (5 cols)

const config = reactive({
  home_nav_title: '系统导航'
})

// Modal States
const showCredModal = ref(false)
const showEditModal = ref(false)
const selectedApp = ref<any>(null)

const handleOpenCredential = (app: any) => {
  selectedApp.value = app
  showCredModal.value = true
}

const handleOpenEdit = (app: any) => {
  selectedApp.value = app
  showEditModal.value = true
}

// 计算 Tabs
const tabs = computed(() => {
  return [
    { id: 0, label: '全部' },
    ...categories.value
  ]
})

// 组件挂载时获取应用列表和分类
const loadData = async () => {
  loading.value = true
  try {
    const [appRes, catRes, configRes] = await Promise.all([
      fetch('/api/apps'),
      fetch('/api/categories'),
      fetch('/api/config')
    ])

    if (appRes.ok) apps.value = await appRes.json()
    if (catRes.ok) categories.value = await catRes.json()
    if (configRes.ok) {
      const data = await configRes.json()
      config.home_nav_title = data.home_nav_title
    }
  } catch (e) {
    console.warn('API不可用，使用本地Mock数据')
    // Mock 数据
    categories.value = [
      { id: 1, label: '行政办公' },
      { id: 2, label: '业务系统' },
      { id: 3, label: '资源数据' },
      { id: 4, label: '开发工具' },
      { id: 5, label: '监控运维' }
    ]
    
    apps.value = [
      {
        id: 1,
        name: "协同办公系统 (Mock)",
        url: "#",
        description: "提供日常办公协同、文档管理、流程审批等核心功能（演示数据）",
        category_id: 1,
        category_label: "行政办公",
        scope_label: "全公司",
        developer: "信息中心",
        deploy_env: "生产环境",
        admin_contact: "张三",
        status: 1
      },
      // ... (其他 Mock 数据如果需要可以相应更新 category_id)
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// 计算属性：根据当前分类筛选应用
const filteredApps = computed(() => {
  if (activeCategory.value === 0) return apps.value
  return apps.value.filter(app => app.category_id === activeCategory.value)
})
</script>

<template>
  <div class="flex flex-col items-center w-full min-h-screen bg-slate-50 dark:bg-[#0f172a]">
    <!-- 顶部 Hero 区域 -->
    <div class="w-full bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40 shadow-sm backdrop-blur-xl bg-opacity-80 dark:bg-opacity-80">
      <div class="max-w-[1920px] mx-auto px-6 py-4">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <!-- 左侧：标题与统计 -->
          <div class="flex items-center gap-4">
            <div class="p-2.5 rounded-xl bg-gradient-to-br from-[#0A3A7D] to-[#3D6BAF] text-white shadow-lg shadow-blue-900/20">
              <img src="/satellite-icon-white2.svg" class="w-8 h-8" alt="Icon" />
            </div>
            <div>
              <h2 class="text-xl font-bold text-slate-800 dark:text-white tracking-tight">{{ config.home_nav_title }}</h2>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">已收录 {{ filteredApps.length }} 个系统</p>
              </div>
            </div>
          </div>

          <!-- 右侧：控制栏 -->
          <div class="flex flex-wrap items-center gap-3">
             <!-- 布局切换按钮 -->
             <div class="bg-slate-100 dark:bg-slate-800 p-1 rounded-lg flex items-center">
                <button 
                  @click="layoutMode = 'compact'"
                  class="p-1.5 rounded-md transition-all duration-200"
                  :class="layoutMode === 'compact' ? 'bg-white dark:bg-slate-700 shadow text-[var(--primary-color)]' : 'text-slate-400 hover:text-slate-600'"
                  title="紧凑模式 (5列)"
                >
                  <div class="i-mdi-view-grid text-lg" />
                </button>
                <button 
                  @click="layoutMode = 'cozy'"
                  class="p-1.5 rounded-md transition-all duration-200"
                  :class="layoutMode === 'cozy' ? 'bg-white dark:bg-slate-700 shadow text-[var(--primary-color)]' : 'text-slate-400 hover:text-slate-600'"
                  title="宽敞模式 (4列)"
                >
                  <div class="i-mdi-view-grid-outline text-lg" />
                </button>
             </div>

             <!-- 分类标签栏 (Pills 风格) -->
             <div class="flex flex-wrap gap-2 bg-slate-100 dark:bg-slate-800 p-1.5 rounded-xl">
               <button 
                 v-for="tab in tabs" 
              :key="tab.id"
              @click="activeCategory = tab.id"
              class="px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-300 relative overflow-hidden"
              :class="activeCategory === tab.id ? 'bg-[var(--primary-color)] text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-slate-700/50'"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="w-full max-w-[1920px] px-6 py-8">
      
      <!-- 加载中状态 -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-32 w-full">
        <div class="relative">
          <div class="w-12 h-12 rounded-full border-4 border-slate-200 dark:border-slate-700"></div>
          <div class="absolute top-0 left-0 w-12 h-12 rounded-full border-4 border-[#0A3A7D] border-t-transparent animate-spin"></div>
        </div>
        <p class="mt-4 text-slate-500 text-sm font-medium animate-pulse">正在加载系统资源...</p>
      </div>
      
      <!-- 空数据状态 -->
      <div v-else-if="filteredApps.length === 0" class="flex flex-col items-center justify-center py-32 text-slate-400 dark:text-slate-600 w-full">
        <div class="p-6 rounded-full bg-slate-100 dark:bg-slate-800/50 mb-4">
          <div class="i-mdi-rocket-off text-4xl opacity-50" />
        </div>
        <p class="font-medium">暂无相关系统</p>
        <p class="text-xs mt-1 opacity-70">请尝试切换其他分类</p>
      </div>
      
      <!-- 应用卡片网格 -->
      <div 
        v-else 
        class="grid gap-6 w-full animate-fade-in-up pb-12 transition-all duration-500 ease-in-out"
        :class="layoutMode === 'compact' 
          ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5' 
          : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-4'"
      >
        <CardSystem 
          v-for="app in filteredApps" 
          :key="app.id" 
          :app="app" 
          @refresh="loadData"
          @open-credential="handleOpenCredential"
          @open-edit="handleOpenEdit"
        />
      </div>
    </div>

    <!-- Modals -->
    <ModalCredential v-model:show="showCredModal" :app="selectedApp" />
    <ModalAdminEdit v-model:show="showEditModal" :app="selectedApp" @refresh="loadData" />
  </div>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
