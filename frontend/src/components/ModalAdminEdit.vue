<script setup lang="ts">
import { ref, watch } from 'vue'
import { useUserStore } from '../stores/user'

const props = defineProps<{
  show: boolean
  app: any
}>()

const emit = defineEmits(['update:show', 'close', 'refresh'])

const userStore = useUserStore()
const loadingEdit = ref(false)
const editForm = ref<any>({})
const categories = ref<any[]>([])
const scopes = ref<any[]>([])

watch(() => props.show, async (newVal) => {
  if (newVal && props.app) {
    editForm.value = { ...props.app }
    await loadOptions()
  }
})

const loadOptions = async () => {
  if (categories.value.length === 0) {
    try {
      const [catRes, scopeRes] = await Promise.all([
        fetch('/api/categories'),
        fetch('/api/scopes')
      ])
      if (catRes.ok) categories.value = await catRes.json()
      if (scopeRes.ok) scopes.value = await scopeRes.json()
    } catch(e) {}
  }
}

const submitEdit = async () => {
  // Validation
  if (!/^1[3-9]\d{9}$/.test(editForm.value.contact_info)) {
    alert('请输入有效的11位手机号码')
    return
  }
  if (/[\u4e00-\u9fa5]/.test(editForm.value.url)) {
    alert('系统URL不能包含中文字符')
    return
  }

  loadingEdit.value = true
  try {
    const headers: any = { 
      'Authorization': `Bearer ${userStore.token}`,
      'Content-Type': 'application/json'
    }
    // Only send necessary fields
    const payload = {
      name: editForm.value.name,
      url: editForm.value.url,
      description: editForm.value.description,
      developer: editForm.value.developer,
      server_location: editForm.value.server_location || editForm.value.deploy_env, // Handle backward compatibility
      admin_contact: editForm.value.admin_contact,
      contact_info: editForm.value.contact_info,
      category_id: editForm.value.category_id,
      scope_id: editForm.value.scope_id
    }
    
    const res = await fetch(`/api/admin/apps/${props.app.id}/update`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      alert('修改成功')
      emit('refresh')
      closeModal()
    } else {
      alert('修改失败')
    }
  } catch(e) {
    alert('网络错误')
  } finally {
    loadingEdit.value = false
  }
}

const closeModal = () => {
  emit('update:show', false)
  emit('close')
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]" @click="closeModal">
    <div class="card p-6 w-full max-w-2xl shadow-2xl max-h-[90vh] overflow-y-auto custom-scrollbar bg-white dark:bg-[#1e293b]" @click.stop>
      <div class="flex justify-between items-center mb-4 sticky top-0 bg-white dark:bg-[#1e293b] z-10 py-2 border-b border-[var(--border-color)]">
        <h3 class="font-bold text-lg flex items-center gap-2 text-slate-800 dark:text-white">
          <div class="i-mdi-pencil text-purple-600" /> 快速编辑
        </h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><div class="i-mdi-close" /></button>
      </div>
      
      <div v-if="loadingEdit" class="py-20 text-center"><div class="i-mdi-loading animate-spin text-3xl text-purple-600" /></div>
      
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Basic Info -->
        <div class="md:col-span-2">
          <label class="block text-xs text-[var(--text-secondary)] mb-1">系统名称</label>
          <input v-model="editForm.name" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
        </div>
        <div class="md:col-span-2">
          <label class="block text-xs text-[var(--text-secondary)] mb-1">系统URL</label>
          <input v-model="editForm.url" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm font-mono text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
        </div>
        
        <!-- Classification -->
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">系统分类</label>
          <select v-model="editForm.category_id" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.label }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">适用范围</label>
          <select v-model="editForm.scope_id" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
            <option v-for="scope in scopes" :key="scope.id" :value="scope.id">{{ scope.label }}</option>
          </select>
        </div>

        <!-- Description -->
        <div class="md:col-span-2">
          <label class="block text-xs text-[var(--text-secondary)] mb-1">系统简介</label>
          <textarea v-model="editForm.description" rows="3" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500"></textarea>
        </div>

        <!-- Meta Info -->
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">开发单位</label>
          <input v-model="editForm.developer" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
        </div>
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">服务器位置</label>
          <input v-model="editForm.server_location" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
        </div>
        
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">管理员姓名</label>
          <input v-model="editForm.admin_contact" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
        </div>
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">联系方式</label>
          <input v-model="editForm.contact_info" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-purple-500">
        </div>

        <div class="md:col-span-2 mt-4 pt-4 border-t border-[var(--border-color)] flex justify-end gap-3">
           <button @click="closeModal" class="btn px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600 rounded transition-colors">取消</button>
           <button @click="submitEdit" class="btn px-4 py-2 text-sm bg-purple-600 hover:bg-purple-700 text-white rounded flex items-center gap-2 transition-colors">
             <div class="i-mdi-content-save" /> 保存修改
           </button>
        </div>
      </div>
    </div>
  </div>
</template>
