<script setup lang="ts">
import { computed, ref } from 'vue'
import BadgeCategory from './Badge_Category.vue'
import { useUserStore } from '../stores/user'

const props = defineProps<{
  app: any
}>()

const userStore = useUserStore()
const showCreds = ref(false)
const decryptedPass = ref('')
const username = ref('') // Needs to be stored too?
// Requirement says "Manage personal credentials (add/delete/auto-fill)".
// So for each app, user can store {username, password}.
// Where is it stored? "Frontend: AES-GCM encrypted credentials -> localStorage".
// Key: `starbase_credentials`. content: `{ appId: {u, p} }` encrypted? 
// Or `starbase_credentials` is the big blob.

// I need to fetch the credential for this app from the store.
// But the store needs to handle the big blob.
// Let's assume the store has a method `getCredential(appId)`.

const hasCredential = computed(() => {
  // Check if credential exists for this app
  // Implementation detail: Load all creds once decrypted
  return false // TODO: Implement
})

const openApp = () => {
  window.open(props.app.url, '_blank')
}

const handleKey = async () => {
  // Logic to decrypt
  // For demo, just alert or copy
  if (!userStore.checkSession()) {
    const pwd = prompt("请输入您的主密码以解密凭据：")
    if (pwd) {
      // Verify by trying to decrypt check
      // For now just set it
      userStore.setSessionPassword(pwd)
    } else {
      return
    }
  }
  // Decrypt
  alert("凭据自动填充功能受限于浏览器安全策略，请使用'复制'功能。\n(模拟：已解密凭据)")
}
</script>

<template>
  <div class="card p-4 flex flex-col h-full relative group">
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded bg-gray-200 overflow-hidden flex-shrink-0">
          <img v-if="app.thumbnail_base64" :src="app.thumbnail_base64" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            <div class="i-mdi-image-off text-2xl" />
          </div>
        </div>
        <div>
          <h3 class="font-bold text-lg leading-tight group-hover:text-primary transition-colors cursor-pointer" @click="openApp">{{ app.name }}</h3>
          <div class="flex items-center gap-2 mt-1">
            <BadgeCategory :category="app.category" />
            <span class="text-xs text-[var(--text-secondary)] border border-[var(--border-color)] px-1 rounded">{{ app.deploy_env }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <p class="text-sm text-[var(--text-secondary)] line-clamp-2 mb-4 flex-grow" :title="app.description">
      {{ app.description }}
    </p>
    
    <div class="flex items-center justify-between text-xs text-[var(--text-secondary)] mt-auto pt-3 border-t border-[var(--border-color)]">
      <div class="flex items-center gap-1" title="开发部门">
        <div class="i-mdi-account-group" />
        <span>{{ app.developer }}</span>
      </div>
      <div class="flex items-center gap-2">
        <button v-if="hasCredential" @click.stop="handleKey" class="icon-btn text-yellow-500" title="一键登录">
          <div class="i-mdi-key-variant" />
        </button>
        <button @click="openApp" class="btn text-xs py-1 px-3">
          进入系统
        </button>
      </div>
    </div>
  </div>
</template>
