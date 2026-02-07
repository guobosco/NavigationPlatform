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
const username = ref('') 

// 检查是否存在已保存的凭据
const hasCredential = computed(() => {
  // 暂时未实现持久化存储凭据的逻辑
  return false 
})

// 打开应用链接
const openApp = () => {
  window.open(props.app.url, '_blank')
}

// 处理凭据解密和自动填充（模拟）
const handleKey = async () => {
  if (!userStore.checkSession()) {
    const pwd = prompt("请输入您的主密码以解密凭据：")
    if (pwd) {
      userStore.setSessionPassword(pwd)
    } else {
      return
    }
  }
  // 解密逻辑
  alert("凭据自动填充功能受限于浏览器安全策略，请使用'复制'功能。\n(模拟：已解密凭据)")
}
</script>

<template>
  <div class="card flex flex-col h-full relative group hover:border-[var(--primary-color)] hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden" @click="openApp">
    <!-- 上方：缩略图区域 (横向占满) -->
    <div class="relative w-full h-32 bg-gray-100 dark:bg-slate-700 overflow-hidden">
      <img v-if="app.thumbnail_base64" :src="app.thumbnail_base64" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
      <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-300 dark:text-gray-600 bg-gray-50 dark:bg-slate-800">
        <div class="i-mdi-image-outline text-4xl mb-1" />
        <span class="text-[10px]">暂无预览</span>
      </div>
      <!-- 分类标签 (悬浮在图片右上角) -->
      <div class="absolute top-2 right-2">
        <BadgeCategory :category="app.category" class="shadow-sm opacity-90 backdrop-blur-sm" />
      </div>
    </div>

    <!-- 下方：内容区域 -->
    <div class="p-4 flex flex-col flex-grow">
      <!-- 标题和链接 -->
      <div class="flex items-start justify-between mb-2">
        <!-- 移除 line-clamp-1，允许标题自动换行 -->
        <h3 class="font-bold text-base text-[var(--text-primary)] leading-tight group-hover:text-[var(--primary-color)] transition-colors" :title="app.name">
          {{ app.name }}
        </h3>
      </div>

      <!-- 简介 -->
      <!-- 添加 title 属性，鼠标悬浮显示全文 -->
      <p class="text-xs text-[var(--text-secondary)] line-clamp-2 mb-4 leading-relaxed h-8" :title="app.description || '暂无描述'">
        {{ app.description || '暂无描述' }}
      </p>

      <!-- 详细元数据列表 -->
      <div class="mt-auto space-y-1.5 pt-3 border-t border-[var(--border-color)]">
        <div class="flex items-center justify-between text-[11px] text-[var(--text-secondary)]">
          <span class="flex items-center gap-1.5 opacity-80">
            <div class="i-mdi-domain text-[var(--primary-color)] opacity-70" />
            <span>开发单位</span>
          </span>
          <span class="font-medium truncate max-w-[50%]" :title="app.developer">{{ app.developer }}</span>
        </div>
        
        <div class="flex items-center justify-between text-[11px] text-[var(--text-secondary)]">
          <span class="flex items-center gap-1.5 opacity-80">
            <div class="i-mdi-account-tie text-[var(--primary-color)] opacity-70" />
            <span>管理员</span>
          </span>
          <span class="font-medium truncate max-w-[50%]" :title="app.admin_contact">{{ app.admin_contact }}</span>
        </div>

        <div class="flex items-center justify-between text-[11px] text-[var(--text-secondary)]">
          <span class="flex items-center gap-1.5 opacity-80">
            <div class="i-mdi-map-marker-radius text-[var(--primary-color)] opacity-70" />
            <span>应用范围</span>
          </span>
          <span class="font-medium truncate max-w-[50%]" :title="app.scope">{{ app.scope }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
