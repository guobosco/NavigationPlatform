<script setup lang="ts">
import { ref, reactive } from 'vue'

// 表单数据
const form = reactive({
  name: '',
  url: '',
  description: '',
  category: 'web',
  scope: '',
  developer: '',
  admin_contact: '',
  deploy_env: '生产环境',
  thumbnail_base64: ''
})

const submitting = ref(false)
const successToken = ref('') // 提交成功后的凭证
const errors = reactive<Record<string, string>>({})

// 分类选项
const categories = [
  { value: 'web', label: 'Web应用' },
  { value: 'desktop', label: '桌面应用' },
  { value: 'mobile', label: '移动应用' },
  { value: 'service', label: '后台服务' },
  { value: 'data', label: '数据平台' },
  { value: 'other', label: '其他' },
]

// 内网 IP 正则表达式
const urlRegex = /^https?:\/\/(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.).*$/

// 表单验证
const validate = () => {
  Object.keys(errors).forEach(k => delete errors[k])
  let valid = true
  
  if (!form.name) { errors.name = '请输入系统名称'; valid = false }
  if (!form.url) { errors.url = '请输入系统URL'; valid = false }
  else if (!urlRegex.test(form.url)) { errors.url = '仅支持内网IP/域名 (10.x, 172.16-31.x, 192.168.x)'; valid = false }
  
  if (!form.description) { errors.description = '请输入功能描述'; valid = false }
  if (!form.scope) { errors.scope = '请输入应用范围'; valid = false }
  if (!form.developer) { errors.developer = '请输入开发者'; valid = false }
  if (!form.admin_contact) { errors.admin_contact = '请输入系统管理员'; valid = false }
  
  return valid
}

// 处理图片上传
const handleFile = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  
  if (file.size > 2 * 1024 * 1024) {
    alert("图片过大，请选择<2MB的图片")
    return
  }
  
  const reader = new FileReader()
  reader.onload = (event) => {
    const img = new Image()
    img.onload = () => {
      // 使用 Canvas 压缩图片
      const canvas = document.createElement('canvas')
      let width = img.width
      let height = img.height
      const maxSize = 800
      
      // 调整尺寸
      if (width > height) {
        if (width > maxSize) {
          height *= maxSize / width
          width = maxSize
        }
      } else {
        if (height > maxSize) {
          width *= maxSize / height
          height = maxSize
        }
      }
      
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(img, 0, 0, width, height)
      
      // 压缩至 < 100KB
      let quality = 0.8
      let dataUrl = canvas.toDataURL('image/jpeg', quality)
      while (dataUrl.length > 100 * 1024 && quality > 0.1) {
        quality -= 0.1
        dataUrl = canvas.toDataURL('image/jpeg', quality)
      }
      
      form.thumbnail_base64 = dataUrl
    }
    img.src = event.target?.result as string
  }
  reader.readAsDataURL(file)
}

// 提交表单
const submit = async () => {
  if (!validate()) return
  
  submitting.value = true
  try {
    const res = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    if (res.ok) {
      const data = await res.json()
      successToken.value = data.submit_token
      // 保存提交记录到本地
      const mySubmits = JSON.parse(localStorage.getItem('my_submits') || '[]')
      mySubmits.push({ token: data.submit_token, timestamp: Date.now(), name: form.name })
      localStorage.setItem('my_submits', JSON.stringify(mySubmits))
    } else {
      alert("提交失败，请重试")
    }
  } catch (e) {
    console.error(e)
    alert("网络错误")
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="text-center mb-8">
      <div class="inline-block p-4 rounded-full bg-primary/10 text-primary mb-4">
        <div class="i-mdi-rocket-launch text-4xl" />
      </div>
      <h1 class="text-3xl font-bold mb-2">我要发布新系统</h1>
      <p class="text-[var(--text-secondary)]">填写系统信息，提交后将进入审核流程</p>
    </div>

    <!-- 提交成功展示凭证 -->
    <div v-if="successToken" class="card p-8 text-center border-l-4 border-l-green-500">
      <div class="i-mdi-check-circle text-5xl text-green-500 mx-auto mb-4" />
      <h2 class="text-2xl font-bold mb-2">🚀 提交成功！</h2>
      <p class="mb-4">系统已进入审核队列</p>
      <div class="bg-[var(--bg-primary)] p-4 rounded font-mono text-lg select-all border border-dashed border-[var(--border-color)]">
        凭证号：{{ successToken }}
      </div>
      <div class="mt-6">
        <router-link to="/" class="btn">返回首页</router-link>
      </div>
    </div>

    <!-- 提交表单 -->
    <form v-else @submit.prevent="submit" class="card p-8 space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium mb-1">系统名称 <span class="text-red-500">*</span></label>
          <input v-model="form.name" type="text" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none" placeholder="例如：协同办公系统">
          <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">系统类别 <span class="text-red-500">*</span></label>
          <select v-model="form.category" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none">
            <option v-for="opt in categories" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">系统URL (内网) <span class="text-red-500">*</span></label>
        <input v-model="form.url" type="text" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none" placeholder="http://192.168.1.100:8080">
        <p class="text-xs text-[var(--text-secondary)] mt-1">仅支持 10.x, 172.16-31.x, 192.168.x 网段</p>
        <p v-if="errors.url" class="text-red-500 text-xs mt-1">{{ errors.url }}</p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">功能描述 <span class="text-red-500">*</span></label>
        <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none" placeholder="简要描述系统的主要功能和用途"></textarea>
        <p v-if="errors.description" class="text-red-500 text-xs mt-1">{{ errors.description }}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium mb-1">应用范围 <span class="text-red-500">*</span></label>
          <input v-model="form.scope" type="text" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none" placeholder="例如：全公司、研发部">
          <p v-if="errors.scope" class="text-red-500 text-xs mt-1">{{ errors.scope }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">开发者 <span class="text-red-500">*</span></label>
          <input v-model="form.developer" type="text" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none" placeholder="开发团队或个人姓名">
          <p v-if="errors.developer" class="text-red-500 text-xs mt-1">{{ errors.developer }}</p>
        </div>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-1">系统管理员 <span class="text-red-500">*</span></label>
        <input v-model="form.admin_contact" type="text" class="w-full px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded focus:border-primary focus:outline-none" placeholder="系统管理员姓名或联系方式">
        <p v-if="errors.admin_contact" class="text-red-500 text-xs mt-1">{{ errors.admin_contact }}</p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">系统缩略图 (可选)</label>
        <div class="border-2 border-dashed border-[var(--border-color)] rounded-lg p-6 text-center cursor-pointer hover:border-primary transition-colors relative">
          <input type="file" accept="image/*" @change="handleFile" class="absolute inset-0 opacity-0 cursor-pointer">
          <div v-if="form.thumbnail_base64" class="relative">
            <img :src="form.thumbnail_base64" class="h-32 mx-auto rounded object-cover">
            <span class="text-xs text-[var(--text-secondary)] block mt-2">点击更换</span>
          </div>
          <div v-else>
            <div class="i-mdi-cloud-upload text-3xl text-[var(--text-secondary)] mx-auto mb-2" />
            <p class="text-sm text-[var(--text-secondary)]">点击或拖拽图片到此处上传</p>
            <p class="text-xs text-[var(--text-secondary)] opacity-70">支持PNG、JPG格式</p>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-4 pt-4 border-t border-[var(--border-color)]">
        <router-link to="/" class="px-6 py-2 rounded border border-[var(--border-color)] hover:bg-[var(--bg-primary)] transition-colors">取消</router-link>
        <button type="submit" :disabled="submitting" class="btn flex items-center gap-2">
          <div v-if="submitting" class="i-mdi-loading animate-spin" />
          <div v-else class="i-mdi-send" />
          提交审核
        </button>
      </div>
    </form>
  </div>
</template>
