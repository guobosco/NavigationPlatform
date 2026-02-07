import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SubmitView from '../views/SubmitView.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'
import { useUserStore } from '../stores/user'

const router = createRouter({
  // 使用 Hash 模式，支持本地文件系统直接打开 (file://)
  // 这对于不需要服务器端配置的简单部署非常有用
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView // 首页：展示应用导航
    },
    {
      path: '/submit',
      name: 'submit',
      component: SubmitView // 应用提交页：用户提交新系统
    },
    {
      path: '/admin-login',
      name: 'admin-login',
      component: AdminLogin // 登录页：管理员和用户通用登录
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboard, // 管理员仪表盘：系统管理
      meta: { requiresAuth: true, role: 'admin' } // 需要管理员权限
    },
    {
      path: '/user',
      name: 'user-dashboard',
      component: UserDashboard, // 用户仪表盘：个人应用管理
      meta: { requiresAuth: true } // 需要登录
    }
  ]
})

// 全局前置守卫：处理权限控制
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    // 未登录跳转登录页
    if (!userStore.isLoggedIn) {
      next('/admin-login')
      return
    }
    
    // 检查角色权限 (如管理员页面需要 admin 角色)
    if (to.meta.role && userStore.user?.role !== to.meta.role) {
      next('/') // 权限不足，跳转首页
      return
    }
    
    next()
  } else {
    next()
  }
})

export default router
