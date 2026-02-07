<script setup lang="ts">
import { computed } from 'vue'
import BadgeCategory from './Badge_Category.vue'
import { useUserStore } from '../stores/user'

const props = defineProps<{
  app: any
}>()

const emit = defineEmits(['refresh', 'open-credential', 'open-edit'])

const userStore = useUserStore()

const isNew = computed(() => {
  if (!props.app.created_at) return false
  const created = new Date(props.app.created_at)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - created.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) 
  return diffDays <= 90 // 3 months approx
})

// 打开应用链接
const openApp = (e: Event) => {
  // Prevent if clicking on buttons
  if ((e.target as HTMLElement).closest('button')) return
  
  let url = props.app.url
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url
  }
  window.open(url, '_blank')
  
  // Record visit
  try {
    fetch(`/api/apps/${props.app.id}/visit`, { method: 'POST' })
  } catch(e) {}
}

// 凭据管理
const openCredential = (e: Event) => {
  e.stopPropagation()
  emit('open-credential', props.app)
}

const openEditModal = (e: Event) => {
  e.stopPropagation()
  emit('open-edit', props.app)
}
</script>

<template>
  <div 
    class="card flex flex-col h-full relative group border bg-white dark:bg-[#1e293b] shadow-[0_4px_16px_rgba(0,0,0,0.1)] hover:shadow-[0_12px_24px_-4px_rgba(0,0,0,0.15)] dark:shadow-[0_4px_16px_rgba(0,0,0,0.3)] dark:hover:shadow-[0_10px_30px_rgba(0,0,0,0.5)] transition-all duration-300 ease-out cursor-pointer overflow-hidden rounded-xl hover:-translate-y-1.5" 
    :class="[
      app.is_starred 
        ? '!border-[#0A3A7D]/30 dark:!border-[#ffffff]/30 !border-2' 
        : '!border-[#0A3A7D]/30 dark:!border-[#ffffff]/30 hover:!border-[#0A3A7D] dark:hover:!border-[#ffffff]'
    ]"
    @click="openApp"
  >
    <!-- 上方：缩略图区域 (横向占满) -->
    <div class="relative w-full aspect-video bg-gray-50 dark:bg-slate-800/50 overflow-hidden border-b border-gray-200 dark:border-gray-700">
      <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10" />
      <img v-if="app.thumbnail_base64" :src="app.thumbnail_base64" class="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-110" />
      <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-300 dark:text-gray-600 bg-gray-50 dark:bg-slate-800">
        <div class="i-mdi-image-outline text-5xl mb-2 opacity-50" />
        <span class="text-xs font-medium tracking-wide uppercase opacity-50">No Preview</span>
      </div>
      <!-- 分类标签 (悬浮在图片右上角) -->
      <div class="absolute top-2 right-2 flex items-center gap-1.5 z-20">
        <!-- Pin & Star Badges -->
        <div v-if="app.is_pinned" class="bg-gradient-to-br from-red-500 to-rose-600 text-white px-2 py-1 rounded shadow-lg shadow-red-500/20 flex items-center gap-1 backdrop-blur-sm transform hover:scale-105 transition-transform" title="置顶推荐">
           <div class="i-mdi-pin text-xs" />
           <span class="text-[10px] font-bold">置顶</span>
        </div>
        <div v-if="app.is_starred" class="bg-gradient-to-br from-amber-400 to-orange-500 text-white px-2 py-1 rounded shadow-lg shadow-orange-500/20 flex items-center gap-1 backdrop-blur-sm transform hover:scale-105 transition-transform" title="星级推荐">
           <div class="i-mdi-star text-xs" />
           <span class="text-[10px] font-bold">推荐</span>
        </div>
        <div v-if="isNew" class="bg-gradient-to-br from-green-400 to-emerald-500 text-white px-2 py-1 rounded shadow-lg shadow-green-500/20 flex items-center gap-1 backdrop-blur-sm transform hover:scale-105 transition-transform" title="近期上新">
           <div class="i-mdi-new-box text-xs" />
           <span class="text-[10px] font-bold">上新</span>
        </div>
        
        <BadgeCategory :category="app.category_label || app.category_id || app.category" class="shadow-sm opacity-90 backdrop-blur-sm" />
      </div>
      
      <!-- 密码本入口 (左上角，登录可见) -->
      <button v-if="userStore.isLoggedIn" @click="openCredential" class="absolute top-3 left-3 p-2 rounded-full bg-blue-600/80 hover:bg-blue-600 text-white backdrop-blur-md shadow-lg transition-all duration-300 z-20 hover:scale-110 active:scale-95" title="管理密码">
         <div class="i-mdi-key-variant text-sm" />
      </button>

      <!-- 管理员快速编辑 (左上角，管理员可见) -->
      <button v-if="userStore.isAdmin" @click="openEditModal" class="absolute top-14 left-3 p-2 rounded-full bg-purple-600/80 hover:bg-purple-600 text-white backdrop-blur-md shadow-lg transition-all duration-300 z-20 hover:scale-110 active:scale-95" title="快速编辑">
         <div class="i-mdi-pencil text-sm" />
      </button>
    </div>

    <!-- 下方：内容区域 -->
    <div class="p-5 flex flex-col flex-grow relative">
      <!-- 装饰背景 -->
      <div class="absolute top-0 right-0 p-4 opacity-[0.03] dark:opacity-[0.05] pointer-events-none transition-opacity group-hover:opacity-10">
        <div class="i-mdi-cube-outline text-6xl" />
      </div>

      <!-- 标题和链接 -->
      <div class="flex items-start justify-between mb-3 relative z-0">
        <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100 leading-tight group-hover:text-[var(--primary-color)] transition-colors duration-300 tracking-tight" :title="app.name">
          {{ app.name }}
        </h3>
      </div>

      <!-- 简介 -->
      <p class="text-sm text-slate-500 dark:text-slate-400 line-clamp-3 mb-5 leading-relaxed h-[4.5em] relative z-0" :title="app.description || '暂无描述'">
        {{ app.description || '暂无描述' }}
      </p>

      <!-- 详细元数据列表 -->
      <div class="mt-auto space-y-1.5 pt-3 border-t border-[var(--border-color)]">
        <div class="flex items-center justify-between text-[11px] text-[var(--text-secondary)]">
          <span class="flex items-center gap-1.5 opacity-80">
            <div class="i-mdi-eye-outline text-[var(--primary-color)] opacity-70" />
            <span>访问次数</span>
          </span>
          <span class="font-medium truncate max-w-[50%]">{{ app.visits || 0 }} 次</span>
        </div>
        
        <div class="flex items-center justify-between text-[11px] text-[var(--text-secondary)]">
          <span class="flex items-center gap-1.5 opacity-80">
            <div class="i-mdi-domain text-[var(--primary-color)] opacity-70" />
            <span>开发单位</span>
          </span>
          <span class="font-medium truncate max-w-[55%] text-slate-700 dark:text-slate-200" :title="app.developer">{{ app.developer }}</span>
        </div>
        
        <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 group/item">
          <span class="flex items-center gap-2 opacity-80 group-hover/item:opacity-100 transition-opacity">
            <div class="i-mdi-account-tie text-[var(--primary-color)]/70" />
            <span>管理员</span>
          </span>
          <div class="flex flex-col items-end max-w-[55%]">
             <span class="font-medium truncate w-full text-right text-slate-700 dark:text-slate-200" :title="app.admin_contact">{{ app.admin_contact }}</span>
             <span v-if="app.contact_info" class="text-[10px] truncate w-full text-right opacity-70" :title="app.contact_info">{{ app.contact_info }}</span>
          </div>
        </div>

        <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 group/item">
          <span class="flex items-center gap-2 opacity-80 group-hover/item:opacity-100 transition-opacity">
            <div class="i-mdi-map-marker-radius text-[var(--primary-color)]/70" />
            <span>应用范围</span>
          </span>
          <span class="font-medium truncate max-w-[55%] text-slate-700 dark:text-slate-200" :title="app.scope_label || app.scope">{{ app.scope_label || app.scope }}</span>
        </div>
      </div>
    </div>

  </div>
</template>
