<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import CardSystem from '../components/Card_System_v2.vue'

// 应用列表数据
const apps = ref<any[]>([])
// 加载状态
const loading = ref(true)
// 当前选中的分类
const activeCategory = ref('all')

// 分类 Tabs 定义
// id 对应后端 CategoryEnum，label 对应前端显示名称
const tabs = [
  { id: 'all', label: '全部' },
  { id: 'web', label: '行政办公' },
  { id: 'desktop', label: '业务系统' },
  { id: 'data', label: '资源数据' },
  { id: 'service', label: '开发工具' },
  { id: 'other', label: '监控运维' },
]

// 组件挂载时获取应用列表
onMounted(async () => {
  try {
    const res = await fetch('/api/apps')
    if (res.ok) {
      apps.value = await res.json()
    } else {
      throw new Error('API request failed')
    }
  } catch (e) {
    console.warn('API不可用，使用本地Mock数据')
    // Mock 数据，保证无后端时也能展示
    apps.value = [
      {
        id: 1,
        name: "协同办公系统 (Mock)",
        url: "#",
        description: "提供日常办公协同、文档管理、流程审批等核心功能（演示数据）",
        category: "web",
        scope: "全公司",
        developer: "信息中心",
        deploy_env: "生产环境",
        admin_contact: "张三",
        status: 1
      },
      {
        id: 2,
        name: "项目管理平台 (Mock)",
        url: "#",
        description: "航天项目全生命周期管理，支持任务分配、进度跟踪（演示数据）",
        category: "desktop",
        scope: "研发部",
        developer: "研发部",
        deploy_env: "生产环境",
        admin_contact: "李四",
        status: 1
      },
      {
        id: 3,
        name: "数据资源中心 (Mock)",
        url: "#",
        description: "统一数据资源管理，提供数据查询、分析和可视化服务（演示数据）",
        category: "data",
        scope: "数据部",
        developer: "数据部",
        deploy_env: "生产环境",
        admin_contact: "王五",
        status: 1
      },
      {
        id: 4,
        name: "代码仓库平台 (Mock)",
        url: "#",
        description: "Git代码托管、版本管理、代码审查和CI/CD集成（演示数据）",
        category: "service",
        scope: "技术部",
        developer: "技术部",
        deploy_env: "生产环境",
        admin_contact: "赵六",
        status: 1
      },
      {
        id: 5,
        name: "系统监控中心 (Mock)",
        url: "#",
        description: "实时监控系统运行状态、性能指标和告警信息（演示数据）",
        category: "other",
        scope: "运维部",
        developer: "运维部",
        deploy_env: "生产环境",
        admin_contact: "孙七",
        status: 1
      }
    ]
  } finally {
    loading.value = false
  }
})

// 计算属性：根据当前分类筛选应用
const filteredApps = computed(() => {
  if (activeCategory.value === 'all') return apps.value
  return apps.value.filter(app => app.category === activeCategory.value)
})
</script>

<template>
  <div class="flex flex-col items-center w-full">
    <!-- Hero Section (移除大标题和搜索框，仅保留简单欢迎语或移除) -->
    <!-- 调整为更紧凑的头部，或者完全移除以增加密度 -->
    <div class="w-full mb-8 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-[var(--primary-color)]">
          <div class="i-mdi-apps text-2xl" />
        </div>
        <div>
          <h2 class="text-xl font-bold text-[var(--text-primary)]">应用导航</h2>
          <p class="text-xs text-[var(--text-secondary)]">共收录 {{ filteredApps.length }} 个系统</p>
        </div>
      </div>

      <!-- 分类标签栏 (右对齐或紧凑排列) -->
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeCategory = tab.id"
          class="px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
          :class="activeCategory === tab.id ? 'bg-[var(--primary-color)] text-white shadow-sm' : 'bg-white dark:bg-slate-800 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-gray-50 dark:hover:bg-slate-700 border border-transparent'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 加载中状态 -->
    <div v-if="loading" class="flex justify-center py-20 w-full">
      <div class="i-mdi-loading animate-spin text-3xl text-[var(--primary-color)]" />
    </div>
    
    <!-- 空数据状态 -->
    <div v-else-if="filteredApps.length === 0" class="text-center py-20 text-[var(--text-secondary)] w-full">
      <div class="i-mdi-rocket-off text-5xl mb-4 opacity-50 mx-auto" />
      <p>暂无相关系统</p>
    </div>
    
    <!-- 应用卡片网格 - 增加列数 (xl:grid-cols-5, 2xl:grid-cols-6) 以提升密度 -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 w-full">
      <CardSystem v-for="app in filteredApps" :key="app.id" :app="app" />
    </div>
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
