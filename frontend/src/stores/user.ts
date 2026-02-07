import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  username: string
  role: 'admin' | 'user'
}

export const useUserStore = defineStore('user', () => {
  // 状态：Token 和 用户信息
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  
  // Initialize user from token if present (basic decoding, not verification)
  // 初始化：如果存在 Token，解析用户信息（仅做基本解码，不做验证）
  if (token.value) {
    try {
      const payload = JSON.parse(atob(token.value.split('.')[1]))
      user.value = {
        username: payload.sub,
        role: payload.role
      }
    } catch (e) {
      token.value = null
      localStorage.removeItem('token')
    }
  }

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isUser = computed(() => user.value?.role === 'user')

  // Actions
  const login = (accessToken: string, username: string, role: 'admin' | 'user') => {
    token.value = accessToken
    user.value = { username, role }
    localStorage.setItem('token', accessToken)
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    isUser,
    login,
    logout
  }
})
