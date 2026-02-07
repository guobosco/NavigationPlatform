import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
// 引入 UnoCSS 样式
import 'virtual:uno.css'
// 引入 Tailwind 重置样式
import '@unocss/reset/tailwind.css'
// 引入全局自定义样式
import './style.css'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia 状态管理
app.use(createPinia())
// 注册 Vue Router 路由
app.use(router)

// 挂载应用到 DOM
app.mount('#app')
