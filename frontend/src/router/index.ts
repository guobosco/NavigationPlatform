import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SubmitView from '../views/SubmitView.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const router = createRouter({
  // 使用 Hash 模式，支持本地文件系统直接打开 (file://)
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView // 首页
    },
    {
      path: '/submit',
      name: 'submit',
      component: SubmitView // 应用提交页
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLogin // 管理员登录页
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboard, // 管理员仪表盘
      meta: { requiresAuth: true } // 需要认证
    }
  ]
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('starbase_admin_token')
    if (!token) {
      // 如果没有 Token，重定向到登录页
      next('/admin/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
