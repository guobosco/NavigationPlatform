import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // Session password (cleared after 30m)
  const sessionPassword = ref<string | null>(null)
  const sessionExpiry = ref<number | null>(null)

  const setSessionPassword = (password: string) => {
    sessionPassword.value = password
    sessionExpiry.value = Date.now() + 30 * 60 * 1000
    
    setTimeout(() => {
      if (sessionExpiry.value && Date.now() >= sessionExpiry.value) {
        clearSession()
      }
    }, 30 * 60 * 1000)
  }

  const clearSession = () => {
    sessionPassword.value = null
    sessionExpiry.value = null
  }

  const checkSession = () => {
    if (sessionExpiry.value && Date.now() > sessionExpiry.value) {
      clearSession()
      return false
    }
    return !!sessionPassword.value
  }

  // Crypto Helpers
  const getSalt = () => {
    let salt = localStorage.getItem('starbase_salt')
    if (!salt) {
      const randomValues = new Uint8Array(16)
      window.crypto.getRandomValues(randomValues)
      // ArrayBuffer to Hex
      salt = Array.from(randomValues).map(b => b.toString(16).padStart(2, '0')).join('')
      localStorage.setItem('starbase_salt', salt)
    }
    // Hex to Uint8Array
    return new Uint8Array(salt.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16)))
  }

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

  const encryptCredential = async (password: string, data: string) => {
    const key = await deriveKey(password)
    const iv = window.crypto.getRandomValues(new Uint8Array(12))
    const enc = new TextEncoder()
    const encrypted = await window.crypto.subtle.encrypt(
      { name: "AES-GCM", iv: iv },
      key,
      enc.encode(data)
    )
    
    // Combine IV + Encrypted Data
    const ivHex = Array.from(iv).map(b => b.toString(16).padStart(2, '0')).join('')
    const dataHex = Array.from(new Uint8Array(encrypted)).map(b => b.toString(16).padStart(2, '0')).join('')
    
    return `${ivHex}:${dataHex}`
  }

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
