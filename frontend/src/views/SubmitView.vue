<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useRoute } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()

// 表单数据
const form = reactive({
  name: '',
  url: '',
  description: '',
  category_id: null as number | null,
  scope_id: null as number | null,
  developer: '',
  admin_contact: '',
  contact_info: '',
  server_location: '默认位置',
  thumbnail_base64: ''
})

const submitting = ref(false)
const success = ref(false)
const showCropModal = ref(false)
const cropImageSrc = ref('')
const cropCanvas = ref<HTMLCanvasElement | null>(null)
const errors = reactive<Record<string, string>>({})
const categories = ref<any[]>([])
const scopes = ref<any[]>([])
const isEditMode = ref(false)
const editAppId = ref<string | null>(null)

const config = reactive({
  title: '发布新系统',
  desc: '填写下方信息提交您的系统，管理员审核通过后将展示在首页',
  placeholder_name: '例如：协同办公系统',
  placeholder_url: 'http://example.com',
  placeholder_desc: '简要描述系统的主要功能和用途...',
  placeholder_developer: '开发团队或个人姓名',
  placeholder_admin_name: '系统管理员姓名',
  placeholder_contact_info: '手机号或邮箱地址',
  placeholder_server_location: '例如：总部机房 / 阿里云'
})

// Load Options
onMounted(async () => {
  try {
    const [catRes, scopeRes, configRes] = await Promise.all([
      fetch('/api/categories'),
      fetch('/api/scopes'),
      fetch('/api/config')
    ])
    if (catRes.ok) categories.value = await catRes.json()
    if (scopeRes.ok) scopes.value = await scopeRes.json()
    if (configRes.ok) {
      const data = await configRes.json()
      config.title = data.submit_page_title || '发布新系统'
      config.desc = data.submit_page_desc || '填写下方信息提交您的系统，管理员审核通过后将展示在首页'
      config.placeholder_name = data.placeholder_name || '例如：协同办公系统'
      config.placeholder_url = data.placeholder_url || 'http://example.com'
      config.placeholder_desc = data.placeholder_desc || '简要描述系统的主要功能和用途...'
      config.placeholder_developer = data.placeholder_developer || '开发团队或个人姓名'
      config.placeholder_admin_name = data.placeholder_admin_name || '系统管理员姓名'
      config.placeholder_contact_info = data.placeholder_contact_info || '手机号或邮箱地址'
      config.placeholder_server_location = data.placeholder_server_location || '例如：总部机房 / 阿里云'
    }
    
    // Set defaults if available (only if not editing)
    if (!route.query.edit) {
      if (categories.value.length > 0) form.category_id = categories.value[0].id
      if (scopes.value.length > 0) form.scope_id = scopes.value[0].id
    }
  } catch (e) {}

  // Check Edit Mode
  if (route.query.edit) {
    isEditMode.value = true
    editAppId.value = route.query.edit as string
    await loadAppData(editAppId.value)
  }
})

const loadAppData = async (id: string) => {
  try {
    const headers: any = {}
    if (userStore.token) headers['Authorization'] = `Bearer ${userStore.token}`
    
    const res = await fetch(`/api/apps/${id}`, { headers })
    if (res.ok) {
      const data = await res.json()
      // Populate Form
      form.name = data.name
      form.url = data.url
      form.description = data.description
      form.category_id = data.category_id
      form.scope_id = data.scope_id
      form.developer = data.developer
      form.admin_contact = data.admin_contact
      form.contact_info = data.contact_info || ''
      form.server_location = data.server_location
      form.thumbnail_base64 = data.thumbnail_base64 || ''
    } else {
      alert("无法加载系统数据，可能已被删除或无权访问")
    }
  } catch (e) {
    console.error(e)
  }
}

// 表单验证
const validate = () => {
  Object.keys(errors).forEach(k => delete errors[k])
  let valid = true
  
  if (!form.name) { errors.name = '请输入系统名称'; valid = false }
  if (!form.url) { errors.url = '请输入系统URL'; valid = false }
  
  if (!form.description) { errors.description = '请输入系统简介'; valid = false }
  if (form.description.length > 500) { errors.description = '系统简介不能超过500字'; valid = false }
  if (!form.scope_id) { errors.scope_id = '请选择系统适用范围'; valid = false }
  if (!form.category_id) { errors.category_id = '请选择系统类别'; valid = false }
  if (!form.developer) { errors.developer = '请输入开发者'; valid = false }
  if (!form.admin_contact) { errors.admin_contact = '请输入系统管理员'; valid = false }
  if (!form.contact_info) {
    errors.contact_info = '请输入管理员联系方式'
    valid = false
  } else if (!/^1[3-9]\d{9}$/.test(form.contact_info)) {
    errors.contact_info = '请输入有效的11位手机号码'
    valid = false
  }

  if (!form.server_location) { errors.server_location = '请输入服务器部署位置'; valid = false }

  if (form.url && /[\u4e00-\u9fa5]/.test(form.url)) {
    errors.url = '系统URL不能包含中文字符'
    valid = false
  }

  if (!form.thumbnail_base64) { 
    alert("请上传系统预览图")
    valid = false 
  }
  
  if (!valid) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
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
      // Check Aspect Ratio (16:9)
      const ratio = img.width / img.height
      const targetRatio = 16 / 9
      const tolerance = 0.05
      
      if (Math.abs(ratio - targetRatio) > tolerance) {
        // Open Crop Modal
        cropImageSrc.value = img.src
        showCropModal.value = true
        // Wait for modal to render
        setTimeout(initCrop, 100)
      } else {
        // Valid Ratio, process directly
        processImage(img)
      }
    }
    img.src = event.target?.result as string
  }
  reader.readAsDataURL(file)
  
  // Clear input value to allow re-selection of same file
  (e.target as HTMLInputElement).value = ''
}

const processImage = (img: HTMLImageElement, sx = 0, sy = 0, sWidth = 0, sHeight = 0) => {
  const canvas = document.createElement('canvas')
  const maxSize = 800
  
  // If crop params provided, use them, else use full image
  const sourceWidth = sWidth || img.width
  const sourceHeight = sHeight || img.height
  
  let width = sourceWidth
  let height = sourceHeight
  
  // Resize if too big (maintain aspect ratio)
  if (width > maxSize) {
    height *= maxSize / width
    width = maxSize
  }
  
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  
  if (sWidth && sHeight) {
    ctx?.drawImage(img, sx, sy, sWidth, sHeight, 0, 0, width, height)
  } else {
    ctx?.drawImage(img, 0, 0, width, height)
  }
  
  // Compress
  let quality = 0.8
  let dataUrl = canvas.toDataURL('image/jpeg', quality)
  while (dataUrl.length > 100 * 1024 && quality > 0.1) {
    quality -= 0.1
    dataUrl = canvas.toDataURL('image/jpeg', quality)
  }
  
  form.thumbnail_base64 = dataUrl
}

// Simple Cropper Logic
const cropX = ref(0)
const cropY = ref(0)
const cropScale = ref(1)
const isDragging = ref(false)
const lastMouseX = ref(0)
const lastMouseY = ref(0)
const imageWidth = ref(0)
const imageHeight = ref(0)
const containerWidth = ref(0)
const containerHeight = ref(0)
const cropContainer = ref<HTMLElement | null>(null)
const cropImg = ref<HTMLImageElement | null>(null)

// 16:9 Crop Box Size (Fixed for simplicity, or responsive)
const cropBoxWidth = 480
const cropBoxHeight = 270

const initCrop = () => {
  if (!cropImg.value || !cropContainer.value) return
  
  // Get natural dimensions
  const img = new Image()
  img.src = cropImageSrc.value
  img.onload = () => {
    imageWidth.value = img.width
    imageHeight.value = img.height
    
    // Initial Scale to cover the crop box
    const scaleX = cropBoxWidth / imageWidth.value
    const scaleY = cropBoxHeight / imageHeight.value
    cropScale.value = Math.max(scaleX, scaleY)
    
    // Center image
    cropX.value = (cropBoxWidth - imageWidth.value * cropScale.value) / 2
    cropY.value = (cropBoxHeight - imageHeight.value * cropScale.value) / 2
  }
}

const onMouseDown = (e: MouseEvent | TouchEvent) => {
  isDragging.value = true
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY
  lastMouseX.value = clientX
  lastMouseY.value = clientY
}

const onMouseMove = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  e.preventDefault()
  
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY
  
  const dx = clientX - lastMouseX.value
  const dy = clientY - lastMouseY.value
  
  cropX.value += dx
  cropY.value += dy
  
  lastMouseX.value = clientX
  lastMouseY.value = clientY
  
  // Boundary checks (Optional: keep image inside crop box? or crop box inside image?)
  // Here we usually want the crop box to be fully filled by the image.
  // So image edges should not go inside the crop box edges.
  // Let's implement simple bounds:
  // Image Left <= 0, Image Right >= cropBoxWidth
  // Image Top <= 0, Image Bottom >= cropBoxHeight
  
  // But since we are moving image relative to top-left of crop box container:
  // Max X is 0 (image left edge aligns with crop box left edge)
  // Min X is cropBoxWidth - currentImageWidth
  
  const currentWidth = imageWidth.value * cropScale.value
  const currentHeight = imageHeight.value * cropScale.value
  
  if (cropX.value > 0) cropX.value = 0
  if (cropX.value < cropBoxWidth - currentWidth) cropX.value = cropBoxWidth - currentWidth
  
  if (cropY.value > 0) cropY.value = 0
  if (cropY.value < cropBoxHeight - currentHeight) cropY.value = cropBoxHeight - currentHeight
}

const onMouseUp = () => {
  isDragging.value = false
}

const onWheel = (e: WheelEvent) => {
  e.preventDefault()
  const zoomSpeed = 0.1
  const newScale = cropScale.value - Math.sign(e.deltaY) * zoomSpeed
  
  // Min scale: cover the crop box
  const minScaleX = cropBoxWidth / imageWidth.value
  const minScaleY = cropBoxHeight / imageHeight.value
  const minScale = Math.max(minScaleX, minScaleY)
  
  if (newScale >= minScale && newScale <= 5) { // Max 5x zoom
    // Zoom towards center or mouse position? 
    // Simple center zoom for now to avoid complex math with offsets
    const oldWidth = imageWidth.value * cropScale.value
    const oldHeight = imageHeight.value * cropScale.value
    const newWidth = imageWidth.value * newScale
    const newHeight = imageHeight.value * newScale
    
    // Adjust position to keep centered relative to previous center
    const cx = cropX.value + oldWidth / 2
    const cy = cropY.value + oldHeight / 2
    
    cropX.value = cx - newWidth / 2
    cropY.value = cy - newHeight / 2
    
    cropScale.value = newScale
    
    // Re-apply bounds
    if (cropX.value > 0) cropX.value = 0
    if (cropX.value < cropBoxWidth - newWidth) cropX.value = cropBoxWidth - newWidth
    
    if (cropY.value > 0) cropY.value = 0
    if (cropY.value < cropBoxHeight - newHeight) cropY.value = cropBoxHeight - newHeight
  }
}

const onCropConfirm = () => {
  const img = new Image()
  img.onload = () => {
    // Calculate source rectangle
    // Map the crop box (0,0, 400,300) back to image coordinates
    // Image is at (cropX, cropY) with scale cropScale
    
    // cropBoxLeft (0) = imageLeft (cropX) + sx * scale
    // => sx = (0 - cropX) / scale
    
    const sx = -cropX.value / cropScale.value
    const sy = -cropY.value / cropScale.value
    const sWidth = cropBoxWidth / cropScale.value
    const sHeight = cropBoxHeight / cropScale.value
    
    processImage(img, sx, sy, sWidth, sHeight)
    showCropModal.value = false
  }
  img.src = cropImageSrc.value
}

// 提交表单
const submit = async () => {
  if (!validate()) return
  
  submitting.value = true
  try {
    const headers: any = { 'Content-Type': 'application/json' }
    if (userStore.token) {
      headers['Authorization'] = `Bearer ${userStore.token}`
    }

    const url = isEditMode.value ? `/api/apps/${editAppId.value}` : '/api/submit'
    const method = isEditMode.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers,
      body: JSON.stringify({
        ...form,
        thumbnail_base64: form.thumbnail_base64 || null
      })
    })
    
    if (res.ok) {
      success.value = true
    } else {
      const errorText = await res.text()
      try {
        const errorJson = JSON.parse(errorText)
        alert(`提交失败: ${errorJson.detail || '未知错误'}`)
      } catch (e) {
        alert(`提交失败: ${errorText}`)
      }
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
  <div class="max-w-4xl mx-auto py-8 px-4">
    <div class="text-center mb-10">
      <div class="inline-flex p-4 rounded-full bg-[var(--primary-light)]/20 text-[var(--primary-color)] mb-4">
        <img src="/satellite-icon-white.svg" alt="Logo" class="h-12 w-12" />
      </div>
      <h1 class="text-3xl font-bold mb-2">{{ isEditMode ? '编辑系统信息' : config.title }}</h1>
      <p class="text-[var(--text-secondary)] max-w-lg mx-auto">{{ config.desc }}</p>
    </div>

    <!-- 提交成功展示凭证 -->
    <div v-if="success" class="card p-10 text-center border-t-4 border-t-green-500 max-w-2xl mx-auto">
      <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <div class="i-mdi-check text-4xl text-green-600" />
      </div>
      <h2 class="text-2xl font-bold mb-2">提交成功！</h2>
      <p class="text-[var(--text-secondary)] mb-8">您的系统已成功提交至审核队列，请耐心等待管理员审核。</p>
      
      <div class="flex justify-center gap-4">
        <router-link to="/" class="btn bg-gray-500 hover:bg-gray-600">返回首页</router-link>
        <router-link v-if="userStore.isLoggedIn" to="/user" class="btn">查看我的发布</router-link>
      </div>
    </div>

    <!-- 提交表单 -->
    <form v-else @submit.prevent="submit" class="card p-8 space-y-8 max-w-3xl mx-auto">
      <!-- 基本信息 -->
      <div class="space-y-6">
        <h3 class="text-lg font-bold border-b border-[var(--border-color)] pb-2 flex items-center gap-2">
          <div class="i-mdi-information-outline text-[var(--primary-color)]" /> 基本信息
        </h3>
        
        <div>
          <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">系统名称 <span class="text-red-500">*</span></label>
          <input v-model="form.name" type="text" class="w-full px-4 py-3 bg-gray-50 dark:bg-slate-800 text-[var(--text-primary)] border-none rounded-xl focus:ring-2 focus:ring-[var(--primary-color)] focus:outline-none transition-all placeholder:text-gray-400/70" :placeholder="config.placeholder_name">
          <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">系统类别 <span class="text-red-500">*</span></label>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div 
              v-for="opt in categories" 
              :key="opt.id"
              @click="form.category_id = opt.id"
              class="cursor-pointer px-4 py-3 rounded-xl text-center transition-all border text-sm font-medium"
              :class="form.category_id === opt.id ? 'bg-[var(--primary-color)] text-white border-[var(--primary-color)] shadow-lg shadow-blue-500/30' : 'bg-[var(--bg-primary)] border-[var(--border-color)] hover:border-[var(--primary-color)] text-[var(--text-secondary)]'"
            >
              {{ opt.label }}
            </div>
          </div>
          <p v-if="errors.category_id" class="text-red-500 text-xs mt-1">{{ errors.category_id }}</p>
        </div>

        <div>
            <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">系统URL <span class="text-red-500">*</span></label>
            <div class="relative">
              <div class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-secondary)] pointer-events-none">
                <div class="i-mdi-link" />
              </div>
              <input v-model="form.url" type="text" class="w-full pl-11 pr-4 py-3 bg-gray-50 dark:bg-slate-800 text-[var(--text-primary)] border-none rounded-xl focus:ring-2 focus:ring-[var(--primary-color)] focus:outline-none transition-all placeholder:text-gray-400/70" :placeholder="config.placeholder_url">
            </div>
            <p v-if="errors.url" class="text-red-500 text-xs mt-1">{{ errors.url }}</p>
          </div>

          <div>
            <div class="flex justify-between items-center mb-1.5">
              <label class="block text-sm font-medium text-[var(--text-secondary)]">系统简介 <span class="text-red-500">*</span></label>
              <span class="text-xs" :class="form.description.length > 500 ? 'text-red-500' : 'text-[var(--text-secondary)]'">
                {{ form.description.length }}/500
              </span>
            </div>
            <textarea v-model="form.description" rows="4" maxlength="500" class="w-full px-4 py-3 bg-gray-50 dark:bg-slate-800 text-[var(--text-primary)] border-none rounded-xl focus:ring-2 focus:ring-[var(--primary-color)] focus:outline-none transition-all placeholder:text-gray-400/70 resize-none" :placeholder="config.placeholder_desc"></textarea>
            <p v-if="errors.description" class="text-red-500 text-xs mt-1">{{ errors.description }}</p>
          </div>
      </div>

      <!-- 属性信息 -->
      <div class="space-y-6">
        <h3 class="text-lg font-bold border-b border-[var(--border-color)] pb-2 flex items-center gap-2">
          <div class="i-mdi-tag-outline text-[var(--primary-color)]" /> 属性信息
        </h3>

        <div>
          <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">系统适用范围 <span class="text-red-500">*</span></label>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div 
                v-for="opt in scopes" 
                :key="opt.id"
                @click="form.scope_id = opt.id"
                class="cursor-pointer px-4 py-3 rounded-xl text-center transition-all border text-sm font-medium"
                :class="form.scope_id === opt.id ? 'bg-[var(--primary-color)] text-white border-[var(--primary-color)] shadow-lg shadow-blue-500/30' : 'bg-[var(--bg-primary)] border-[var(--border-color)] hover:border-[var(--primary-color)] text-[var(--text-secondary)]'"
              >
                {{ opt.label }}
              </div>
            </div>
          <p v-if="errors.scope_id" class="text-red-500 text-xs mt-1">{{ errors.scope_id }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">开发者 <span class="text-red-500">*</span></label>
          <input v-model="form.developer" type="text" class="w-full px-4 py-3 bg-gray-50 dark:bg-slate-800 text-[var(--text-primary)] border-none rounded-xl focus:ring-2 focus:ring-[var(--primary-color)] focus:outline-none transition-all placeholder:text-gray-400/70" :placeholder="config.placeholder_developer">
          <p v-if="errors.developer" class="text-red-500 text-xs mt-1">{{ errors.developer }}</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">系统管理员 <span class="text-red-500">*</span></label>
          <input v-model="form.admin_contact" type="text" class="w-full px-4 py-3 bg-gray-50 dark:bg-slate-800 text-[var(--text-primary)] border-none rounded-xl focus:ring-2 focus:ring-[var(--primary-color)] focus:outline-none transition-all placeholder:text-gray-400/70" :placeholder="config.placeholder_admin_name">
          <p v-if="errors.admin_contact" class="text-red-500 text-xs mt-1">{{ errors.admin_contact }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">管理员联系方式 <span class="text-red-500">*</span></label>
          <input v-model="form.contact_info" type="text" class="w-full px-4 py-3 bg-gray-50 dark:bg-slate-800 text-[var(--text-primary)] border-none rounded-xl focus:ring-2 focus:ring-[var(--primary-color)] focus:outline-none transition-all placeholder:text-gray-400/70" :placeholder="config.placeholder_contact_info">
          <p v-if="errors.contact_info" class="text-red-500 text-xs mt-1">{{ errors.contact_info }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5 text-[var(--text-secondary)]">服务器部署位置 <span class="text-red-500">*</span></label>
          <input v-model="form.server_location" type="text" class="w-full px-4 py-3 bg-gray-50 dark:bg-slate-800 text-[var(--text-primary)] border-none rounded-xl focus:ring-2 focus:ring-[var(--primary-color)] focus:outline-none transition-all placeholder:text-gray-400/70" :placeholder="config.placeholder_server_location">
          <p v-if="errors.server_location" class="text-red-500 text-xs mt-1">{{ errors.server_location }}</p>
        </div>
      </div>

      <!-- 图片上传 -->
      <div class="space-y-6">
        <h3 class="text-lg font-bold border-b border-[var(--border-color)] pb-2 flex items-center gap-2">
          <div class="i-mdi-image-outline text-[var(--primary-color)]" /> 系统预览图
        </h3>
        
        <div>
          <div class="border-2 border-dashed border-[var(--border-color)] rounded-xl p-8 text-center cursor-pointer hover:border-[var(--primary-color)] hover:bg-[var(--bg-primary)] transition-all relative group">
            <input type="file" accept="image/*" @change="handleFile" class="absolute inset-0 opacity-0 cursor-pointer z-10">
            
            <div v-if="form.thumbnail_base64" class="relative">
              <img :src="form.thumbnail_base64" class="h-48 mx-auto rounded-lg object-contain shadow-sm">
              <div class="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg">
                <span class="text-white font-medium flex items-center gap-2">
                  <div class="i-mdi-refresh" /> 点击更换
                </span>
              </div>
            </div>
            <div v-else class="py-4">
              <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <div class="i-mdi-cloud-upload text-3xl text-[var(--text-secondary)]" />
              </div>
              <p class="text-base font-medium mb-1">点击或拖拽图片到此处上传</p>
              <p class="text-xs text-[var(--text-secondary)] opacity-70">支持 PNG, JPG 格式 (建议尺寸 800x600)</p>
            </div>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-4 pt-6 border-t border-[var(--border-color)]">
        <router-link to="/" class="px-6 py-2.5 rounded-lg border border-[var(--border-color)] hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">取消</router-link>
        <button type="submit" :disabled="submitting" class="btn flex items-center gap-2 px-8 py-2.5 text-base shadow-lg shadow-blue-500/20">
          <div v-if="submitting" class="i-mdi-loading animate-spin" />
          <div v-else class="i-mdi-send" />
          {{ isEditMode ? '重新提交审核' : '提交审核' }}
        </button>
      </div>
    </form>
    <!-- Crop Modal -->
    <div v-if="showCropModal" class="fixed inset-0 bg-black/90 flex items-center justify-center z-[100] p-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-6 w-full max-w-3xl flex flex-col h-auto max-h-[95vh]">
        <h3 class="text-xl font-bold mb-4">裁剪图片</h3>
        <p class="text-sm text-[var(--text-secondary)] mb-4">请拖拽移动图片，滚动鼠标缩放，调整裁剪区域 (16:9)</p>
        
        <!-- Crop Container -->
        <div class="flex-1 flex items-center justify-center overflow-hidden bg-gray-900 rounded-lg select-none">
           <div 
             ref="cropContainer"
             class="relative overflow-hidden cursor-move"
             :style="{ width: cropBoxWidth + 'px', height: cropBoxHeight + 'px' }"
             @mousedown="onMouseDown"
             @touchstart="onMouseDown"
             @mousemove="onMouseMove"
             @touchmove="onMouseMove"
             @mouseup="onMouseUp"
             @touchend="onMouseUp"
             @mouseleave="onMouseUp"
             @wheel="onWheel"
           >
             <!-- Image -->
             <img 
               ref="cropImg"
               :src="cropImageSrc" 
               class="absolute max-w-none pointer-events-none origin-top-left"
               :style="{ 
                 transform: `translate(${cropX}px, ${cropY}px) scale(${cropScale})`,
                 width: imageWidth + 'px',
                 height: imageHeight + 'px'
               }" 
               draggable="false"
             />
             
             <!-- Mask / Guide Lines -->
             <div class="absolute inset-0 border-2 border-white/50 pointer-events-none shadow-[0_0_0_9999px_rgba(0,0,0,0.7)] z-10">
               <!-- Grid Lines -->
               <div class="absolute inset-0 grid grid-cols-3 grid-rows-3 opacity-50">
                 <div class="border-r border-b border-white/30"></div>
                 <div class="border-r border-b border-white/30"></div>
                 <div class="border-b border-white/30"></div>
                 <div class="border-r border-b border-white/30"></div>
                 <div class="border-r border-b border-white/30"></div>
                 <div class="border-b border-white/30"></div>
                 <div class="border-r border-white/30"></div>
                 <div class="border-r border-white/30"></div>
                 <div></div>
               </div>
             </div>
           </div>
        </div>

        <div class="flex justify-between items-center mt-6">
          <div class="text-xs text-[var(--text-secondary)]">
             缩放: {{ Math.round(cropScale * 100) }}%
          </div>
          <div class="flex gap-4">
            <button @click="showCropModal = false" class="px-4 py-2 rounded-lg border border-[var(--border-color)] hover:bg-gray-100 dark:hover:bg-slate-700">取消</button>
            <button @click="onCropConfirm" class="btn bg-[var(--primary-color)]">确认裁剪</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Scoped styles removed in favor of utility classes */
</style>
