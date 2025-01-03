import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'
import Layout from '../components/Layout.vue'
import { getMenus } from '../api/menu'

// 静态路由
export const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled', requiresAuth: true }
      },
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import('../views/UserManagement.vue'),
        meta: { title: '用户管理', icon: 'User', requiresAuth: true }
      },
      {
        path: 'system/menus',
        name: 'MenuManagement',
        component: () => import('../views/MenuManagement.vue'),
        meta: { title: '菜单管理', icon: 'Menu', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = store.state.token
  
  if (to.meta.requiresAuth && !token) {
    next({ 
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    if (token && store.state.menus.length === 0) {
      try {
        const { data } = await getMenus()
        if (data) {
          store.commit('setMenus', data)
        }
      } catch (error) {
        console.error('获取菜单失败:', error)
        store.commit('clearToken')
        next('/login')
        return
      }
    }
    next()
  }
})

export default router 