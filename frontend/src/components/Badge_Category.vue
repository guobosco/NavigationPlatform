<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  category: string
}>()

const colors: Record<string, string> = {
  web: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  desktop: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  mobile: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  service: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  data: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  other: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
}

const colorClass = computed(() => colors[props.category] || colors.other)
const label = computed(() => {
  const map: Record<string, string> = {
    web: 'Web应用',
    desktop: '桌面应用',
    mobile: '移动应用',
    service: '后台服务',
    data: '数据平台',
    other: '其他'
  }
  return map[props.category] || props.category
})
</script>

<template>
  <span class="px-2.5 py-0.5 rounded-full text-xs font-medium" :class="colorClass">
    {{ label }}
  </span>
</template>
