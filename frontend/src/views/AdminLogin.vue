<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const isRegister = ref(false)
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

// 切换模式
const toggleMode = () => {
  isRegister.value = !isRegister.value
  error.value = ''
  username.value = ''
  password.value = ''
  confirmPassword.value = ''
}

// 提交处理
const handleSubmit = async () => {
  if (isRegister.value) {
    await register()
  } else {
    await login()
  }
}

// 注册处理
const register = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    
    if (res.ok) {
      const data = await res.json()
      handleAuthSuccess(data)
    } else {
      const errorData = await res.json()
      error.value = errorData.detail || '注册失败'
    }
  } catch (e) {
    error.value = '注册失败，请检查网络'
  } finally {
    loading.value = false
  }
}

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
      handleAuthSuccess(data)
    } else {
      error.value = '用户名或密码错误'
    }
  } catch (e) {
    error.value = '登录失败，请检查网络'
  } finally {
    loading.value = false
  }
}

const handleAuthSuccess = (data: any) => {
  // 更新 Store 状态
  userStore.login(data.access_token, data.username, data.role)
  
  // 根据角色跳转
  if (data.role === 'admin') {
    router.push('/admin')
  } else {
    router.push('/user')
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-20">
    <div class="card p-8">
      <div class="text-center mb-8">
        <div class="i-mdi-shield-account text-5xl text-primary mx-auto mb-4" />
        <h1 class="text-2xl font-bold">{{ isRegister ? '用户注册' : '系统登录' }}</h1>
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium mb-1">用户名</label>
          <input v-model="username" type="text" required class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none">
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1">密码</label>
          <input v-model="password" type="password" required class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none">
        </div>

        <div v-if="isRegister">
          <label class="block text-sm font-medium mb-1">确认密码</label>
          <input v-model="confirmPassword" type="password" required class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none">
        </div>
        
        <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        
        <button type="submit" :disabled="loading" class="w-full btn flex justify-center items-center gap-2">
          <div v-if="loading" class="i-mdi-loading animate-spin" />
          {{ isRegister ? '注册并登录' : '登录' }}
        </button>

        <div class="text-center pt-2">
          <button type="button" @click="toggleMode" class="text-sm text-[var(--primary-color)] hover:underline">
            {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
