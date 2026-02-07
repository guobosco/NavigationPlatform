<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import BadgeCategory from '../components/Badge_Category.vue'

const router = useRouter()
// 当前激活的标签页
const activeTab = ref('pending')
// 待审核应用列表
const pendingApps = ref<any[]>([])
// 系统配置
const config = reactive({ title: '', slogan: '' })
// 在线应用列表
const onlineApps = ref<any[]>([])

// 封装带认证的 Fetch 请求
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('starbase_admin_token')
  if (!token) {
    router.push('/admin/login')
    throw new Error('No token')
  }
  
  const headers = { ...options.headers, 'Authorization': `Bearer ${token}` }
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem('starbase_admin_token')
    router.push('/admin/login')
    throw new Error('Unauthorized')
  }
  return res
}

// 加载待审核列表
const loadPending = async () => {
  try {
    const res = await fetchWithAuth('/api/admin/pending')
    if (res.ok) pendingApps.value = await res.json()
  } catch (e) {}
}

// 加载在线应用列表
const loadOnline = async () => {
   try {
    const res = await fetch('/api/apps') // 公开 API
    if (res.ok) onlineApps.value = await res.json()
  } catch (e) {}
}

// 加载系统配置
const loadConfig = async () => {
  try {
    const res = await fetch('/api/config')
    if (res.ok) {
      const data = await res.json()
      config.title = data.title
      config.slogan = data.slogan
    }
  } catch (e) {}
}

onMounted(() => {
  loadPending()
  loadOnline()
  loadConfig()
})

// 批准应用
const approve = async (id: number) => {
  if (!confirm('确认审核通过该系统？')) return
  try {
    const res = await fetchWithAuth(`/api/admin/approve/${id}`, { method: 'POST' })
    if (res.ok) {
      await loadPending()
      await loadOnline()
    }
  } catch (e) {}
}

// 删除应用
const deleteApp = async (id: number) => {
  if (!confirm('确认删除该系统？此操作不可恢复。')) return
  try {
    const res = await fetchWithAuth(`/api/admin/apps/${id}`, { method: 'DELETE' })
    if (res.ok) {
      await loadOnline()
    }
  } catch (e) {}
}

// 保存系统配置
const saveConfig = async () => {
  try {
    const res = await fetchWithAuth('/api/admin/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })
    if (res.ok) alert('配置已更新')
  } catch (e) {}
}

// 退出登录
const logout = () => {
  localStorage.removeItem('starbase_admin_token')
  router.push('/admin/login')
}
</script>

<template>
  <div>
    <!-- 头部：标题与退出按钮 -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold mb-2">管理员后台</h1>
        <p class="text-[var(--text-secondary)]">系统审核、配置管理和卡片维护</p>
      </div>
      <button @click="logout" class="btn bg-red-600 hover:bg-red-700">退出登录</button>
    </div>

    <!-- 标签页切换 -->
    <div class="flex gap-4 mb-6 border-b border-[var(--border-color)]">
      <button 
        @click="activeTab = 'pending'" 
        class="pb-2 px-4 border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'pending' ? 'border-primary text-primary' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'"
      >
        <div class="i-mdi-clock-outline" /> 审核看板
      </button>
      <button 
        @click="activeTab = 'config'" 
        class="pb-2 px-4 border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'config' ? 'border-primary text-primary' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'"
      >
        <div class="i-mdi-cog-outline" /> 网站配置
      </button>
       <button 
        @click="activeTab = 'apps'" 
        class="pb-2 px-4 border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'apps' ? 'border-primary text-primary' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'"
      >
        <div class="i-mdi-view-grid-outline" /> 卡片管理
      </button>
    </div>

    <!-- 内容区域 -->
    
    <!-- 审核看板 -->
    <div v-if="activeTab === 'pending'">
      <div v-if="pendingApps.length === 0" class="text-center py-20 card">
        <div class="i-mdi-check-all text-5xl text-gray-400 mx-auto mb-4" />
        <p>暂无待审核系统</p>
      </div>
      <div v-else class="space-y-4">
        <div v-for="app in pendingApps" :key="app.id" class="card p-4 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <!-- 缩略图预览 -->
            <div class="w-16 h-16 rounded bg-gray-200 overflow-hidden">
               <img v-if="app.thumbnail_base64" :src="app.thumbnail_base64" class="w-full h-full object-cover" />
               <div v-else class="w-full h-full flex items-center justify-center"><div class="i-mdi-image-off" /></div>
            </div>
            <!-- 应用详情 -->
            <div>
              <h3 class="font-bold text-lg">{{ app.name }}</h3>
              <div class="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                <BadgeCategory :category="app.category" />
                <span>{{ app.deploy_env }}</span>
                <span>•</span>
                <span>{{ app.developer }}</span>
              </div>
              <div class="text-xs text-[var(--text-secondary)] mt-1">URL: {{ app.url }}</div>
            </div>
          </div>
          <!-- 操作按钮 -->
          <div class="flex items-center gap-4">
             <div class="text-right mr-4">
                <div class="text-xs text-[var(--text-secondary)]">提交时间</div>
                <div class="text-sm font-mono">{{ new Date(app.created_at).toLocaleDateString() }}</div>
             </div>
             <button @click="approve(app.id)" class="btn bg-green-600 hover:bg-green-700 flex items-center gap-1">
               <div class="i-mdi-check" /> 通过
             </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 网站配置 -->
    <div v-if="activeTab === 'config'">
      <div class="card p-8 max-w-2xl">
        <h2 class="text-xl font-bold mb-6">网站配置</h2>
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium mb-1">网站主标题 ({{ config.title.length }}/30)</label>
            <input v-model="config.title" type="text" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">网站Slogan ({{ config.slogan.length }}/60)</label>
            <textarea v-model="config.slogan" rows="3" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none"></textarea>
          </div>
          
          <div class="pt-4 border-t border-[var(--border-color)]">
            <p class="text-xs text-[var(--text-secondary)] mb-4">实例预览</p>
            <div class="text-center p-6 bg-[var(--bg-primary)] rounded border border-dashed border-[var(--border-color)]">
              <h1 class="text-2xl font-bold mb-2">{{ config.title }}</h1>
              <p class="text-sm text-[var(--text-secondary)]">{{ config.slogan }}</p>
            </div>
          </div>

          <button @click="saveConfig" class="w-full btn flex justify-center items-center gap-2">
            <div class="i-mdi-content-save" /> 保存配置
          </button>
        </div>
      </div>
    </div>
    
    <!-- 卡片管理 -->
    <div v-if="activeTab === 'apps'">
      <div class="space-y-4">
        <div v-for="app in onlineApps" :key="app.id" class="card p-4 flex items-center justify-between">
          <div class="flex items-center gap-4">
             <div>
              <h3 class="font-bold">{{ app.name }}</h3>
              <div class="text-xs text-[var(--text-secondary)]">{{ app.scope }} • {{ app.admin_contact }}</div>
             </div>
          </div>
          <button @click="deleteApp(app.id)" class="btn bg-red-900/50 text-red-200 hover:bg-red-900 text-xs px-3 py-1 border border-red-800 flex items-center gap-1">
            <div class="i-mdi-delete" /> 删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
