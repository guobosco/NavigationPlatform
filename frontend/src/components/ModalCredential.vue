<script setup lang="ts">
import { ref, watch } from 'vue'
import { useUserStore } from '../stores/user'

const props = defineProps<{
  show: boolean
  app: any
}>()

const emit = defineEmits(['update:show', 'close'])

const userStore = useUserStore()
const cred = ref({ username_text: '', password_text: '', note: '' })
const loadingCred = ref(false)

// Watch for show change to fetch data
watch(() => props.show, async (newVal) => {
  if (newVal && props.app) {
    await fetchCredential()
  }
})

const fetchCredential = async () => {
  loadingCred.value = true
  try {
    const headers: any = { 'Authorization': `Bearer ${userStore.token}` }
    const res = await fetch(`/api/credentials/${props.app.id}`, { headers })
    if (res.ok) {
      const data = await res.json()
      if (data) {
        cred.value = { 
          username_text: data.username_text || '', 
          password_text: data.password_text || '',
          note: data.note || ''
        }
      } else {
         cred.value = { username_text: '', password_text: '', note: '' }
      }
    }
  } catch(e) {} finally {
    loadingCred.value = false
  }
}

const saveCredential = async () => {
  loadingCred.value = true
  try {
    const headers: any = { 
      'Authorization': `Bearer ${userStore.token}`,
      'Content-Type': 'application/json'
    }
    const res = await fetch('/api/credentials', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        app_id: props.app.id,
        ...cred.value
      })
    })
    if (res.ok) {
      closeModal()
      alert('凭据已保存')
    }
  } catch(e) {
    alert('保存失败')
  } finally {
    loadingCred.value = false
  }
}

const closeModal = () => {
  emit('update:show', false)
  emit('close')
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]" @click="closeModal">
    <div class="card p-6 w-full max-w-sm shadow-2xl bg-white dark:bg-[#1e293b]" @click.stop>
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg flex items-center gap-2 text-slate-800 dark:text-white">
          <div class="i-mdi-shield-key text-[var(--primary-color)]" /> 凭据管理
        </h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><div class="i-mdi-close" /></button>
      </div>
      
      <div v-if="loadingCred" class="py-8 text-center"><div class="i-mdi-loading animate-spin text-2xl text-[var(--primary-color)]" /></div>
      
      <div v-else class="space-y-4">
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">用户名/账号</label>
          <input v-model="cred.username_text" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-[var(--primary-color)]">
        </div>
        <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">密码</label>
          <div class="relative">
             <input v-model="cred.password_text" type="text" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm font-mono text-slate-800 dark:text-slate-200 focus:outline-none focus:border-[var(--primary-color)]">
          </div>
        </div>
         <div>
          <label class="block text-xs text-[var(--text-secondary)] mb-1">备注</label>
          <textarea v-model="cred.note" rows="2" class="input w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-sm text-slate-800 dark:text-slate-200 focus:outline-none focus:border-[var(--primary-color)]"></textarea>
        </div>
        
        <div class="text-[10px] text-orange-500 bg-orange-50 dark:bg-orange-900/20 p-2 rounded flex items-start gap-1">
           <div class="i-mdi-lock-outline mt-0.5" />
           本密码只有自己可见，请放心填写。
        </div>

        <button @click="saveCredential" class="w-full btn bg-[var(--primary-color)] text-white py-2 rounded flex justify-center gap-2 mt-2 hover:opacity-90 transition-opacity">
          <div class="i-mdi-content-save" /> 保存
        </button>
      </div>
    </div>
  </div>
</template>
