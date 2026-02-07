<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const myApps = ref<any[]>([])
const loading = ref(true)

const fetchWithAuth = async (url: string) => {
  const token = localStorage.getItem('token')
  if (!token) return
  
  const res = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.status === 401) {
    // 认证失效，清除 Token 并跳转登录
    localStorage.removeItem('token')
    userStore.token = null
    userStore.user = null
    router.push('/admin-login')
    return
  }
  if (res.ok) return res.json()
}

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/admin-login')
    return
  }
  
  try {
    const apps = await fetchWithAuth('/api/my-apps')
    if (apps) myApps.value = apps
  } finally {
    loading.value = false
  }
})

const getStatusColor = (status: number) => {
  switch(status) {
    case 0: return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    case 1: return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    case 2: return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status: number) => {
  switch(status) {
    case 0: return '审核中'
    case 1: return '已发布'
    case 2: return '已拒绝'
    case 3: return '已下线'
    default: return '未知'
  }
}

const handleEdit = (app: any) => {
  if (app.status === 1) {
    if (confirm('重新编辑已发布的系统将导致其暂时下线，直到审核再次通过。确认要继续吗？')) {
      router.push(`/submit?edit=${app.id}`)
    }
  } else {
    router.push(`/submit?edit=${app.id}`)
  }
}

const toggleStatus = async (app: any) => {
  const isOnline = app.status === 1
  const action = isOnline ? '下线' : '上架'
  
  if (confirm(`确定要${action}该系统吗？${isOnline ? '下线后用户将无法在首页看到该系统。' : '上架后系统将重新显示在首页。'}`)) {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/apps/${app.id}/toggle-status`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        // Refresh list
        const apps = await fetchWithAuth('/api/my-apps')
        if (apps) myApps.value = apps
      } else {
        alert("操作失败")
      }
    } catch (e) {
      alert("网络错误")
    }
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-8 px-4">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold mb-2">用户中心</h1>
        <p class="text-[var(--text-secondary)]">欢迎回来，{{ userStore.user?.username }}</p>
      </div>
      <router-link to="/submit" class="btn bg-[var(--primary-color)] flex items-center gap-2">
        <div class="i-mdi-plus" /> 发布新系统
      </router-link>
    </div>

    <div class="card p-6 min-h-[400px]">
      <h2 class="text-xl font-bold mb-6 flex items-center gap-2">
        <div class="i-mdi-folder-outline" /> 我的发布 ({{ myApps.length }})
      </h2>

      <div v-if="loading" class="flex justify-center py-10">
        <div class="i-mdi-loading animate-spin text-2xl" />
      </div>

      <div v-else-if="myApps.length === 0" class="text-center py-20 text-[var(--text-secondary)]">
        <div class="i-mdi-file-document-outline text-5xl mb-4 opacity-50 mx-auto" />
        <p>您还没有发布任何系统</p>
      </div>

      <div v-else class="space-y-4">
        <div v-for="app in myApps" :key="app.id" class="border border-[var(--border-color)] rounded-lg p-4 hover:shadow-md transition-shadow">
          <div class="flex justify-between items-start">
            <div class="flex gap-4">
              <!-- Thumb -->
              <div class="w-12 h-12 rounded bg-gray-200 overflow-hidden flex-shrink-0">
                 <img v-if="app.thumbnail_base64" :src="app.thumbnail_base64" class="w-full h-full object-cover" />
                 <div v-else class="w-full h-full flex items-center justify-center"><div class="i-mdi-image-off" /></div>
              </div>
              
              <!-- Info -->
              <div>
                <h3 class="font-bold text-lg flex items-center gap-2">
                  {{ app.name }}
                  <span class="text-xs px-2 py-0.5 rounded-full" :class="getStatusColor(app.status)">
                    {{ getStatusText(app.status) }}
                  </span>
                </h3>
                <div class="text-sm text-[var(--text-secondary)] mt-1">{{ app.category_label }} • {{ app.created_at.split('T')[0] }}</div>
                
                <!-- Reject Reason -->
                <div v-if="app.status === 2 && app.reject_reason" class="mt-2 bg-red-50 dark:bg-red-900/20 p-2 rounded text-sm text-red-600 dark:text-red-400">
                  <span class="font-bold">审核意见：</span> {{ app.reject_reason }}
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex gap-2">
              <a v-if="app.status === 1" :href="app.url" target="_blank" class="icon-btn text-blue-500" title="访问">
                <div class="i-mdi-open-in-new" />
              </a>
              <button @click="handleEdit(app)" class="icon-btn text-gray-500 hover:text-primary" title="编辑/重新提交">
                <div class="i-mdi-pencil" />
              </button>
              
              <!-- Toggle Status (Only for Online/Offline) -->
              <button v-if="app.status === 1 || app.status === 3" @click="toggleStatus(app)" class="icon-btn" :class="app.status === 1 ? 'text-orange-500 hover:text-orange-600' : 'text-green-500 hover:text-green-600'" :title="app.status === 1 ? '下线系统' : '上架系统'">
                <div :class="app.status === 1 ? 'i-mdi-arrow-down-bold-box-outline' : 'i-mdi-arrow-up-bold-box-outline'" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
