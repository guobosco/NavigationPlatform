import { defineStore } from 'pinia'
import { ref } from 'vue'

// 用户状态 Store，主要处理本地凭据加密
export const useUserStore = defineStore('user', () => {
  // 会话密码（用于解密本地凭据），仅保存在内存中
  // 设置 30 分钟过期，防止长期驻留
  const sessionPassword = ref<string | null>(null)
  const sessionExpiry = ref<number | null>(null)

  // 设置会话密码
  const setSessionPassword = (password: string) => {
    sessionPassword.value = password
    sessionExpiry.value = Date.now() + 30 * 60 * 1000 // 30分钟后过期
    
    // 定时清理
    setTimeout(() => {
      if (sessionExpiry.value && Date.now() >= sessionExpiry.value) {
        clearSession()
      }
    }, 30 * 60 * 1000)
  }

  // 清除会话
  const clearSession = () => {
    sessionPassword.value = null
    sessionExpiry.value = null
  }

  // 检查会话是否有效
  const checkSession = () => {
    if (sessionExpiry.value && Date.now() > sessionExpiry.value) {
      clearSession()
      return false
    }
    return !!sessionPassword.value
  }

  // --- 加密辅助函数 ---
  
  // 获取或生成盐值（Salt）
  // 存储在 localStorage 中，用于 PBKDF2 密钥派生
  const getSalt = () => {
    let salt = localStorage.getItem('starbase_salt')
    if (!salt) {
      const randomValues = new Uint8Array(16)
      window.crypto.getRandomValues(randomValues)
      // ArrayBuffer 转 Hex 字符串
      salt = Array.from(randomValues).map(b => b.toString(16).padStart(2, '0')).join('')
      localStorage.setItem('starbase_salt', salt)
    }
    // Hex 字符串转 Uint8Array
    return new Uint8Array(salt.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16)))
  }

  // 派生密钥 (PBKDF2)
  // 使用用户的主密码和盐值生成加密密钥
  const deriveKey = async (password: string) => {
    const salt = getSalt()
    const enc = new TextEncoder()
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      enc.encode(password),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    )
    return window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: 100000,
        hash: "SHA-256",
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    )
  }

  // 加密凭据 (AES-GCM)
  const encryptCredential = async (password: string, data: string) => {
    const key = await deriveKey(password)
    const iv = window.crypto.getRandomValues(new Uint8Array(12)) // 12 字节 IV
    const enc = new TextEncoder()
    const encrypted = await window.crypto.subtle.encrypt(
      { name: "AES-GCM", iv: iv },
      key,
      enc.encode(data)
    )
    
    // 组合 IV + 加密数据，返回 Hex 格式
    const ivHex = Array.from(iv).map(b => b.toString(16).padStart(2, '0')).join('')
    const dataHex = Array.from(new Uint8Array(encrypted)).map(b => b.toString(16).padStart(2, '0')).join('')
    
    return `${ivHex}:${dataHex}`
  }

  // 解密凭据
  const decryptCredential = async (password: string, encryptedStr: string) => {
    const [ivHex, dataHex] = encryptedStr.split(':')
    const iv = new Uint8Array(ivHex.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16)))
    const data = new Uint8Array(dataHex.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16)))
    
    const key = await deriveKey(password)
    
    try {
      const decrypted = await window.crypto.subtle.decrypt(
        { name: "AES-GCM", iv: iv },
        key,
        data
      )
      return new TextDecoder().decode(decrypted)
    } catch (e) {
      console.error("Decryption failed", e)
      return null
    }
  }

  return {
    sessionPassword,
    setSessionPassword,
    checkSession,
    encryptCredential,
    decryptCredential
  }
})
