<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import BadgeCategory from '../components/Badge_Category.vue'

const router = useRouter()
const activeTab = ref('pending')
const pendingApps = ref<any[]>([])
const onlineApps = ref<any[]>([])
const rejectedApps = ref<any[]>([])
const categories = ref<any[]>([])
const scopes = ref<any[]>([])
const users = ref<any[]>([])

const config = reactive({ 
  title: '', 
  slogan: '',
  home_nav_title: '',
  footer_copyright: '',
  nav_publish_text: '',
  submit_page_title: '',
  submit_page_desc: '',
  placeholder_name: '',
  placeholder_url: '',
  placeholder_desc: '',
  placeholder_developer: '',
  placeholder_admin_name: '',
  placeholder_contact_info: '',
  placeholder_server_location: ''
})
const newCategory = ref({ name: '', label: '' })
const newScope = ref({ name: '', label: '' })
const showRejectModal = ref(false)
const rejectReason = ref('')
const rejectAppId = ref<number | null>(null)

// 封装带认证的 Fetch 请求
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/admin-login')
    throw new Error('No token')
  }
  
  const headers = { ...options.headers, 'Authorization': `Bearer ${token}` }
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401 || res.status === 403) {
    localStorage.removeItem('token')
    router.push('/admin-login')
    throw new Error('Unauthorized')
  }
  return res
}

// Data Loaders
const loadApps = async () => {
  try {
    const res = await fetchWithAuth('/api/admin/apps')
    if (res.ok) {
      const allApps = await res.json()
      pendingApps.value = allApps.filter((a: any) => a.status === 0)
      onlineApps.value = allApps.filter((a: any) => a.status === 1)
      rejectedApps.value = allApps.filter((a: any) => a.status === 2 || a.status === 3)
    }
  } catch (e) {}
}

const loadConfig = async () => {
  try {
    const res = await fetch('/api/config')
    if (res.ok) {
      const data = await res.json()
      config.title = data.title
      config.slogan = data.slogan
      config.home_nav_title = data.home_nav_title
      config.footer_copyright = data.footer_copyright
      config.nav_publish_text = data.nav_publish_text
      config.submit_page_title = data.submit_page_title
      config.submit_page_desc = data.submit_page_desc
      config.placeholder_name = data.placeholder_name
      config.placeholder_url = data.placeholder_url
      config.placeholder_desc = data.placeholder_desc
      config.placeholder_developer = data.placeholder_developer
      config.placeholder_admin_name = data.placeholder_admin_name
      config.placeholder_contact_info = data.placeholder_contact_info
      config.placeholder_server_location = data.placeholder_server_location
    }
  } catch (e) {}
}

const loadOptions = async () => {
  try {
    const [catRes, scopeRes] = await Promise.all([
      fetch('/api/categories'),
      fetch('/api/scopes')
    ])
    if (catRes.ok) categories.value = await catRes.json()
    if (scopeRes.ok) scopes.value = await scopeRes.json()
  } catch (e) {}
}

const loadUsers = async () => {
  try {
    const res = await fetchWithAuth('/api/admin/users')
    if (res.ok) users.value = await res.json()
  } catch (e) {}
}

onMounted(() => {
  loadApps()
  loadConfig()
  loadOptions()
  loadUsers()
})

// App Actions
const updateStatus = async (id: number, status: number, reason?: string) => {
  try {
    const res = await fetchWithAuth(`/api/admin/apps/${id}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, reject_reason: reason })
    })
    if (res.ok) {
      await loadApps()
      return true
    }
  } catch (e) {}
  return false
}

const approve = (id: number) => {
  if (confirm('确认审核通过该系统？')) updateStatus(id, 1)
}

const openRejectModal = (id: number) => {
  rejectAppId.value = id
  rejectReason.value = ''
  showRejectModal.value = true
}

const submitReject = async () => {
  if (rejectAppId.value !== null) {
    if (await updateStatus(rejectAppId.value, 2, rejectReason.value)) {
      showRejectModal.value = false
    }
  }
}

const previewApp = (url: string) => {
  window.open(url, '_blank')
}

const deleteApp = async (id: number) => {
  if (!confirm('确认删除该系统？此操作不可恢复。')) return
  try {
    const res = await fetchWithAuth(`/api/admin/apps/${id}`, { method: 'DELETE' })
    if (res.ok) await loadApps()
  } catch (e) {}
}

// Config Actions
const toggleStatus = async (app: any) => {
  const isOnline = app.status === 1
  const action = isOnline ? '下线' : '上架'
  
  if (confirm(`确定要${action}该应用吗？${isOnline ? '下线后用户将无法在首页看到该应用。' : '上架后应用将重新显示在首页。'}`)) {
    try {
      const res = await fetchWithAuth(`/api/apps/${app.id}/toggle-status`, {
        method: 'POST'
      })
      if (res.ok) {
        await loadApps()
      } else {
        alert("操作失败")
      }
    } catch (e) {
      alert("网络错误")
    }
  }
}

const updateAttributes = async (app: any, attrs: any) => {
  try {
    const res = await fetchWithAuth(`/api/admin/apps/${app.id}/attributes`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(attrs)
    })
    if (res.ok) {
      await loadApps()
    } else {
      alert("更新失败")
    }
  } catch (e) {
    alert("网络错误")
  }
}

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

// Option Management
const addCategory = async () => {
  if (!newCategory.value.name || !newCategory.value.label) return
  try {
    const res = await fetchWithAuth('/api/admin/categories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newCategory.value)
    })
    if (res.ok) {
      newCategory.value = { name: '', label: '' }
      loadOptions()
    } else {
      const errorText = await res.text()
      try {
          const json = JSON.parse(errorText)
          alert(`添加失败: ${json.detail || '未知错误'}`)
      } catch(e) {
          alert(`添加失败: ${errorText}`)
      }
    }
  } catch (e) {
      alert("网络错误")
  }
}

const deleteCategory = async (id: number) => {
  if(!confirm('确定删除该分类？')) return
  try {
    const res = await fetchWithAuth(`/api/admin/categories/${id}`, { method: 'DELETE' })
    if(res.ok) loadOptions()
  } catch(e) {}
}

const addScope = async () => {
  if (!newScope.value.name || !newScope.value.label) return
  try {
    const res = await fetchWithAuth('/api/admin/scopes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newScope.value)
    })
    if (res.ok) {
      newScope.value = { name: '', label: '' }
      loadOptions()
    } else {
      const errorText = await res.text()
      try {
          const json = JSON.parse(errorText)
          alert(`添加失败: ${json.detail || '未知错误'}`)
      } catch(e) {
          alert(`添加失败: ${errorText}`)
      }
    }
  } catch (e) {
      alert("网络错误")
  }
}

const deleteScope = async (id: number) => {
  if(!confirm('确定删除该范围？')) return
  try {
    const res = await fetchWithAuth(`/api/admin/scopes/${id}`, { method: 'DELETE' })
    if(res.ok) loadOptions()
  } catch(e) {}
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/admin-login')
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold mb-2">管理员后台</h1>
        <p class="text-[var(--text-secondary)]">系统审核、配置管理和卡片维护</p>
      </div>
      <button @click="logout" class="btn bg-red-600 hover:bg-red-700">退出登录</button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-4 mb-6 border-b border-[var(--border-color)] overflow-x-auto">
      <button @click="activeTab = 'pending'" class="tab-btn" :class="{ 'active': activeTab === 'pending' }">
        <div class="i-mdi-clock-outline" /> 审核看板 ({{ pendingApps.length }})
      </button>
      <button @click="activeTab = 'apps'" class="tab-btn" :class="{ 'active': activeTab === 'apps' }">
        <div class="i-mdi-view-grid-outline" /> 卡片管理
      </button>
      <button @click="activeTab = 'config'" class="tab-btn" :class="{ 'active': activeTab === 'config' }">
        <div class="i-mdi-cog-outline" /> 网站配置
      </button>
      <button @click="activeTab = 'options'" class="tab-btn" :class="{ 'active': activeTab === 'options' }">
        <div class="i-mdi-format-list-bulleted" /> 选项管理
      </button>
      <button @click="activeTab = 'users'" class="tab-btn" :class="{ 'active': activeTab === 'users' }">
        <div class="i-mdi-account-group" /> 用户管理
      </button>
    </div>

    <!-- Content -->
    
    <!-- 1. Audit Board -->
    <div v-if="activeTab === 'pending'">
      <div v-if="pendingApps.length === 0" class="text-center py-20 card">
        <div class="i-mdi-check-all text-5xl text-gray-400 mx-auto mb-4" />
        <p>暂无待审核系统</p>
      </div>
      <div v-else class="space-y-4">
        <div v-for="app in pendingApps" :key="app.id" class="card p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div class="flex items-center gap-4 w-full md:w-auto">
            <div class="w-16 h-16 rounded bg-gray-200 overflow-hidden flex-shrink-0">
               <img v-if="app.thumbnail_base64" :src="app.thumbnail_base64" class="w-full h-full object-cover" />
               <div v-else class="w-full h-full flex items-center justify-center"><div class="i-mdi-image-off" /></div>
            </div>
            <div>
              <h3 class="font-bold text-lg">{{ app.name }}</h3>
              <div class="flex flex-wrap items-center gap-2 text-sm text-[var(--text-secondary)]">
                <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{{ app.category_label || app.category_id }}</span>
                <span>{{ app.deploy_env }}</span>
                <span>•</span>
                <span>{{ app.developer }}</span>
              </div>
              <div class="text-xs text-[var(--text-secondary)] mt-1 truncate max-w-md">URL: {{ app.url }}</div>
            </div>
          </div>
          
          <div class="flex items-center gap-2 w-full md:w-auto justify-end">
             <button @click="previewApp(app.url)" class="btn bg-blue-600 hover:bg-blue-700 flex items-center gap-1 text-sm">
               <div class="i-mdi-eye" /> 预览
             </button>
             <button @click="openRejectModal(app.id)" class="btn bg-orange-600 hover:bg-orange-700 flex items-center gap-1 text-sm">
               <div class="i-mdi-close" /> 拒绝
             </button>
             <button @click="approve(app.id)" class="btn bg-green-600 hover:bg-green-700 flex items-center gap-1 text-sm">
               <div class="i-mdi-check" /> 通过
             </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. Apps Management (Online & Rejected) -->
    <div v-if="activeTab === 'apps'">
      <div class="grid md:grid-cols-2 gap-6">
        <!-- Online Apps -->
        <div>
          <h3 class="font-bold mb-4 flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-green-500"></div> 已上线 ({{ onlineApps.length }})
          </h3>
          <div class="space-y-3">
            <div v-for="app in onlineApps" :key="app.id" class="card p-3 flex items-center justify-between group">
              <div class="flex items-center gap-3">
                <div class="flex flex-col items-center gap-1">
                   <!-- Sort Order Input -->
                   <input 
                     type="number" 
                     :value="app.sort_order" 
                     @change="(e) => updateAttributes(app, { sort_order: parseInt((e.target as HTMLInputElement).value) })"
                     class="w-12 px-1 py-0.5 text-center text-xs bg-gray-50 border border-gray-200 rounded" 
                     title="排序权重 (越大越靠前)"
                   />
                </div>
                
                <div class="w-10 h-10 rounded bg-gray-100 flex-shrink-0 overflow-hidden">
                   <img v-if="app.thumbnail_base64" :src="app.thumbnail_base64" class="w-full h-full object-cover" />
                </div>
                
                <div>
                  <div class="font-medium flex items-center gap-1">
                    {{ app.name }}
                    <div v-if="app.is_pinned" class="i-mdi-pin text-xs text-red-500" title="已置顶" />
                    <div v-if="app.is_starred" class="i-mdi-star text-xs text-yellow-500" title="已标星" />
                  </div>
                  <div class="text-xs text-[var(--text-secondary)]">{{ app.category_label }}</div>
                </div>
              </div>
              
              <div class="flex gap-2">
                 <button @click="updateAttributes(app, { is_pinned: !app.is_pinned })" class="icon-btn" :class="app.is_pinned ? 'text-red-500' : 'text-gray-300 hover:text-red-400'" title="置顶">
                   <div class="i-mdi-pin" />
                 </button>
                 <button @click="updateAttributes(app, { is_starred: !app.is_starred })" class="icon-btn" :class="app.is_starred ? 'text-yellow-500' : 'text-gray-300 hover:text-yellow-400'" title="标星">
                   <div class="i-mdi-star" />
                 </button>
                 <div class="w-px h-4 bg-gray-200 mx-1"></div>
                 <button @click="toggleStatus(app)" class="icon-btn text-orange-500" title="下线"><div class="i-mdi-arrow-down-bold-box-outline" /></button>
                 <button @click="deleteApp(app.id)" class="icon-btn text-red-500" title="删除"><div class="i-mdi-delete" /></button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Rejected/Offline Apps -->
        <div>
          <h3 class="font-bold mb-4 flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-red-500"></div> 已拒绝 / 已下线 ({{ rejectedApps.length }})
          </h3>
           <div class="space-y-3">
            <div v-for="app in rejectedApps" :key="app.id" class="card p-3 flex items-center justify-between" :class="{'opacity-75': app.status === 2}">
              <div>
                <div class="font-medium flex items-center gap-2">
                  {{ app.name }}
                  <span v-if="app.status === 3" class="text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded">已下线</span>
                  <span v-if="app.status === 2" class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">已拒绝</span>
                </div>
                <div class="text-xs text-red-500" v-if="app.status === 2 && app.reject_reason">理由: {{ app.reject_reason }}</div>
              </div>
              <div class="flex gap-2">
                 <button v-if="app.status === 3" @click="toggleStatus(app)" class="icon-btn text-green-500" title="上架"><div class="i-mdi-arrow-up-bold-box-outline" /></button>
                 <button v-if="app.status === 2" @click="approve(app.id)" class="icon-btn text-green-500" title="通过"><div class="i-mdi-check" /></button>
                 <button @click="deleteApp(app.id)" class="icon-btn text-red-500" title="删除"><div class="i-mdi-delete" /></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Config -->
    <div v-if="activeTab === 'config'">
      <div class="card p-8 w-full">
        <h2 class="text-xl font-bold mb-6">网站配置</h2>
        <div class="space-y-8">
          <!-- 1-Column Layout as requested -->
          
          <!-- Site Basic -->
          <div class="bg-[var(--bg-primary)]/30 p-6 rounded-2xl border border-[var(--border-color)]">
            <h3 class="font-bold border-b border-[var(--border-color)] pb-3 mb-6 flex items-center gap-2">
               <div class="i-mdi-web text-blue-500" /> 基本信息
            </h3>
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">网站主标题</label>
                <input v-model="config.title" type="text" class="input">
              </div>
              <div>
                <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">网站Slogan</label>
                <input v-model="config.slogan" type="text" class="input">
              </div>
              <div>
                <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">底部版权信息</label>
                <input v-model="config.footer_copyright" type="text" class="input">
              </div>
            </div>
          </div>

          <!-- Home Config -->
          <div class="bg-[var(--bg-primary)]/30 p-6 rounded-2xl border border-[var(--border-color)]">
            <h3 class="font-bold border-b border-[var(--border-color)] pb-3 mb-6 flex items-center gap-2">
               <div class="i-mdi-home-outline text-purple-500" /> 首页配置
            </h3>
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">首页"系统导航"标题</label>
                <input v-model="config.home_nav_title" type="text" class="input">
              </div>
            </div>
          </div>

          <!-- Submit Page Config -->
          <div class="bg-[var(--bg-primary)]/30 p-6 rounded-2xl border border-[var(--border-color)]">
             <h3 class="font-bold border-b border-[var(--border-color)] pb-3 mb-6 flex items-center gap-2">
               <div class="i-mdi-file-document-edit-outline text-green-500" /> 发布页文案配置
             </h3>
             <div class="space-y-6">
               <div>
                 <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">导航栏"发布"按钮文本</label>
                 <input v-model="config.nav_publish_text" type="text" class="input">
               </div>
               <div>
                 <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">发布页主标题</label>
                 <input v-model="config.submit_page_title" type="text" class="input">
               </div>
               <div>
                 <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">发布页描述文本</label>
                 <textarea v-model="config.submit_page_desc" rows="3" class="input resize-y"></textarea>
               </div>
             </div>
          </div>

          <!-- Placeholders Config -->
          <div class="bg-[var(--bg-primary)]/30 p-6 rounded-2xl border border-[var(--border-color)]">
             <h3 class="font-bold border-b border-[var(--border-color)] pb-3 mb-6 flex items-center gap-2">
               <div class="i-mdi-text-box-outline text-orange-500" /> 输入框提示文字配置 (Placeholder)
             </h3>
             <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div>
                  <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">"系统名称" 提示文字</label>
                  <input v-model="config.placeholder_name" type="text" class="input">
               </div>
               <div>
                  <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">"系统URL" 提示文字</label>
                  <input v-model="config.placeholder_url" type="text" class="input">
               </div>
               <div class="md:col-span-2">
                  <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">"系统简介" 提示文字</label>
                  <input v-model="config.placeholder_desc" type="text" class="input">
               </div>
               <div>
                  <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">"开发者" 提示文字</label>
                  <input v-model="config.placeholder_developer" type="text" class="input">
               </div>
               <div>
                  <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">"系统管理员" 提示文字</label>
                  <input v-model="config.placeholder_admin_name" type="text" class="input">
               </div>
               <div>
                  <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">"管理员联系方式" 提示文字</label>
                  <input v-model="config.placeholder_contact_info" type="text" class="input">
               </div>
               <div>
                  <label class="block text-sm font-medium mb-2 text-[var(--text-secondary)]">"服务器部署位置" 提示文字</label>
                  <input v-model="config.placeholder_server_location" type="text" class="input">
               </div>
             </div>
          </div>

          <div class="pt-4 sticky bottom-6 z-10">
            <button @click="saveConfig" class="w-full btn flex justify-center items-center gap-2 py-4 text-lg shadow-xl shadow-blue-500/20 rounded-xl hover:scale-[1.01] active:scale-[0.99] transition-all">
              <div class="i-mdi-content-save" /> 保存所有配置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Options Management -->
    <div v-if="activeTab === 'options'">
       <div class="grid md:grid-cols-2 gap-8">
         <!-- Categories -->
         <div class="card p-6 h-full flex flex-col">
           <h3 class="font-bold mb-4 flex items-center gap-2 text-lg">
             <div class="w-1 h-5 bg-blue-500 rounded-full" /> 系统分类管理
           </h3>
           
           <div class="flex gap-2 mb-6 bg-[var(--bg-primary)] p-3 rounded-lg border border-[var(--border-color)]">
             <input v-model="newCategory.name" placeholder="ID (如 web)" class="input flex-1 text-sm bg-white dark:bg-slate-800" />
             <input v-model="newCategory.label" placeholder="名称 (如 办公)" class="input flex-1 text-sm bg-white dark:bg-slate-800" />
             <button @click="addCategory" class="btn bg-[var(--primary-color)] px-4 flex-shrink-0" :disabled="!newCategory.name || !newCategory.label">
               <div class="i-mdi-plus" /> 添加
             </button>
           </div>

           <div class="space-y-2 overflow-y-auto flex-1 max-h-[500px] pr-2 custom-scrollbar">
             <div v-if="categories.length === 0" class="text-center text-[var(--text-secondary)] py-8">
               暂无分类数据
             </div>
             <div v-for="cat in categories" :key="cat.id" class="flex justify-between items-center p-3 bg-[var(--bg-primary)] hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors group border border-transparent hover:border-[var(--border-color)]">
               <div class="flex items-center gap-3">
                 <span class="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xs font-mono font-bold">{{ cat.id }}</span>
                 <div class="flex flex-col">
                   <span class="font-medium text-sm">{{ cat.label }}</span>
                   <span class="font-mono text-xs text-[var(--text-secondary)]">{{ cat.name }}</span>
                 </div>
               </div>
               <button @click="deleteCategory(cat.id)" class="w-8 h-8 rounded-full hover:bg-red-100 dark:hover:bg-red-900/30 text-[var(--text-secondary)] hover:text-red-500 flex items-center justify-center transition-colors">
                 <div class="i-mdi-delete" />
               </button>
             </div>
           </div>
         </div>

         <!-- Scopes -->
         <div class="card p-6 h-full flex flex-col">
           <h3 class="font-bold mb-4 flex items-center gap-2 text-lg">
             <div class="w-1 h-5 bg-purple-500 rounded-full" /> 系统范围管理
           </h3>
           
           <div class="flex gap-2 mb-6 bg-[var(--bg-primary)] p-3 rounded-lg border border-[var(--border-color)]">
             <input v-model="newScope.name" placeholder="ID (如 dept)" class="input flex-1 text-sm bg-white dark:bg-slate-800" />
             <input v-model="newScope.label" placeholder="名称 (如 部门)" class="input flex-1 text-sm bg-white dark:bg-slate-800" />
             <button @click="addScope" class="btn bg-[var(--primary-color)] px-4 flex-shrink-0" :disabled="!newScope.name || !newScope.label">
               <div class="i-mdi-plus" /> 添加
             </button>
           </div>

           <div class="space-y-2 overflow-y-auto flex-1 max-h-[500px] pr-2 custom-scrollbar">
             <div v-if="scopes.length === 0" class="text-center text-[var(--text-secondary)] py-8">
               暂无范围数据
             </div>
             <div v-for="scope in scopes" :key="scope.id" class="flex justify-between items-center p-3 bg-[var(--bg-primary)] hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors group border border-transparent hover:border-[var(--border-color)]">
               <div class="flex items-center gap-3">
                 <span class="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-xs font-mono font-bold">{{ scope.id }}</span>
                 <div class="flex flex-col">
                   <span class="font-medium text-sm">{{ scope.label }}</span>
                   <span class="font-mono text-xs text-[var(--text-secondary)]">{{ scope.name }}</span>
                 </div>
               </div>
               <button @click="deleteScope(scope.id)" class="w-8 h-8 rounded-full hover:bg-red-100 dark:hover:bg-red-900/30 text-[var(--text-secondary)] hover:text-red-500 flex items-center justify-center transition-colors">
                 <div class="i-mdi-delete" />
               </button>
             </div>
           </div>
         </div>
       </div>
    </div>

    <!-- 5. Users Management -->
    <div v-if="activeTab === 'users'">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold flex items-center gap-2">
            <div class="i-mdi-account-group text-blue-500" /> 用户列表
          </h2>
          <button @click="loadUsers" class="btn bg-gray-100 hover:bg-gray-200 text-gray-700">
            <div class="i-mdi-refresh" /> 刷新
          </button>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-slate-800 text-[var(--text-secondary)] text-sm uppercase">
                <th class="p-3 font-medium rounded-l-lg">ID</th>
                <th class="p-3 font-medium">用户名</th>
                <th class="p-3 font-medium">角色</th>
                <th class="p-3 font-medium">密码 (明文)</th>
                <th class="p-3 font-medium rounded-r-lg">注册时间</th>
              </tr>
            </thead>
            <tbody class="text-sm">
              <tr v-for="user in users" :key="user.id" class="border-b border-[var(--border-color)] last:border-none hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors">
                <td class="p-3 font-mono text-[var(--text-secondary)]">#{{ user.id }}</td>
                <td class="p-3 font-medium">{{ user.username }}</td>
                <td class="p-3">
                  <span class="px-2 py-1 rounded text-xs font-medium" :class="user.role === 'admin' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'">
                    {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                  </span>
                </td>
                <td class="p-3 font-mono text-gray-500 bg-gray-100 dark:bg-slate-900 px-2 py-1 rounded select-all w-fit">
                  {{ user.plain_password || '******' }}
                </td>
                <td class="p-3 text-[var(--text-secondary)]">{{ new Date(user.created_at).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
      <div class="card p-6 w-full max-w-md shadow-xl">
        <h3 class="text-lg font-bold mb-4">拒绝申请</h3>
        <textarea v-model="rejectReason" class="input w-full h-32 mb-4" placeholder="请输入拒绝原因/修改意见..."></textarea>
        <div class="flex justify-end gap-2">
          <button @click="showRejectModal = false" class="btn bg-gray-500 hover:bg-gray-600">取消</button>
          <button @click="submitReject" class="btn bg-orange-600 hover:bg-orange-700">确认拒绝</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.tab-btn {
  @apply relative px-6 py-3 transition-all duration-200 flex items-center gap-2 whitespace-nowrap text-sm font-medium text-[var(--text-secondary)] border-b-2 border-transparent hover:text-[var(--primary-color)] hover:bg-gray-50 dark:hover:bg-slate-800/50;
}
.tab-btn.active {
  @apply border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/50 dark:bg-blue-900/10;
}
.input {
  @apply w-full px-4 py-3 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-xl focus:border-[var(--primary-color)] focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all;
}
</style>
