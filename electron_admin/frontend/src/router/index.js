import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

// 静态路由(不需要权限)
const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/Index.vue'),
    redirect: '/dashboard',
    children: []
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes: constantRoutes
})

// 使用 import.meta.glob 预加载所有视图组件
const modules = import.meta.glob('../views/**/*.vue')

// 动态加载组件
const loadComponent = (componentPath) => {
  // componentPath 格式: "Dashboard" 或 "system/Users"
  const path = `../views/${componentPath}.vue`
  
  const component = modules[path]
  if (!component) {
    console.error(`组件未找到: ${path}`)
    return null
  }
  
  return component
}

// 动态添加路由
export function addDynamicRoutes(menus) {
  if (!menus || menus.length === 0) return false
  
  try {
    menus.forEach(menu => {
      const component = loadComponent(menu.component)
      if (component) {
        const route = {
          path: menu.path,
          name: menu.name,
          component: component,
          meta: menu.meta
        }
        console.log("route1111111111111",route)
        router.addRoute('Layout', route)
      }
    })
    return true
  } catch (error) {
    console.error('添加动态路由失败:', error)
    return false
  }
}

// 重置路由
export function resetRouter() {
  const newRouter = createRouter({
    history: createWebHashHistory(),
    routes: constantRoutes
  })
  router.matcher = newRouter.matcher
}

// 路由守卫 - 只负责权限验证
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const userStore = useUserStore()
  const isLoggedIn = userStore.isLoggedIn
  
  // 白名单路由
  const whiteList = ['/login']
  
  if (whiteList.includes(to.path)) {
    // 已登录访问登录页,跳转到首页
    if (isLoggedIn) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    // 需要登录的页面
    if (isLoggedIn) {
      // 刷新页面时,如果路由还没加载,先加载路由
      if (!userStore.routesAdded && userStore.token) {
        try {
          await userStore.fetchUserInfo()
          next({ ...to, replace: true })
        } catch (error) {
          console.error('加载路由失败:', error)
          userStore.logout()
          next('/login')
        }
      } else {
        next()
      }
    } else {
      // 未登录,跳转到登录页
      next('/login')
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
