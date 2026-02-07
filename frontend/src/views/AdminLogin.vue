<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

// 登录处理函数
const login = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('username', username.value)
    formData.append('password', password.value)
    
    const res = await fetch('/token', {
      method: 'POST',
      body: formData
    })
    
    if (res.ok) {
      const data = await res.json()
      // 存储 JWT Token
      localStorage.setItem('starbase_admin_token', data.access_token)
      // 跳转到后台管理页
      router.push('/admin')
    } else {
      error.value = '用户名或密码错误'
    }
  } catch (e) {
    error.value = '登录失败，请检查网络'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-20">
    <div class="card p-8">
      <div class="text-center mb-8">
        <div class="i-mdi-shield-account text-5xl text-primary mx-auto mb-4" />
        <h1 class="text-2xl font-bold">管理员登录</h1>
      </div>
      
      <form @submit.prevent="login" class="space-y-6">
        <div>
          <label class="block text-sm font-medium mb-1">用户名</label>
          <input v-model="username" type="text" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none">
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1">密码</label>
          <input v-model="password" type="password" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none">
        </div>
        
        <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        
        <button type="submit" :disabled="loading" class="w-full btn flex justify-center items-center gap-2">
          <div v-if="loading" class="i-mdi-loading animate-spin" />
          登录
        </button>
      </form>
    </div>
  </div>
</template>
