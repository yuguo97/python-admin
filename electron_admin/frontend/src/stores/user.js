import { defineStore } from 'pinia'
import { login as loginApi, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null,
    menuCodes: [],
    menus: [],
    routesAdded: false
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.is_admin || false
  },
  
  actions: {
    // 登录 - 只负责获取 Token
    async login(username, password) {
      try {
        const res = await loginApi(username, password)
        if (res.data) {
          this.token = res.data.access_token
          localStorage.setItem('token', res.data.access_token)
          return true
        }
        return false
      } catch (error) {
        console.error('登录失败:', error)
        return false
      }
    },
    
    // 获取用户信息并添加动态路由
    async fetchUserInfo() {
      try {
        const res = await getUserInfo()
        if (res.data) {
          this.userInfo = res.data
          this.menuCodes = res.data.menu_codes || []
          this.menus = res.data.menus || []
          
          // 动态添加路由
          if (this.menus.length > 0) {
            const { addDynamicRoutes } = await import('@/router/index')
            const success = addDynamicRoutes(this.menus)
            if (success) {
              this.routesAdded = true
            }
          }
          
          return true
        }
        return false
      } catch (error) {
        console.error('获取用户信息失败:', error)
        return false
      }
    },
    
    // 登出
    logout() {
      this.token = ''
      this.userInfo = null
      this.menuCodes = []
      this.menus = []
      this.routesAdded = false
      localStorage.removeItem('token')
      
      // 重置路由
      import('@/router/index').then(({ resetRouter }) => {
        resetRouter()
      })
    }
  }
})
