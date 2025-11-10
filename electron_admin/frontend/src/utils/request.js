import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'
import { API_BASE_URLS, REQUEST_TIMEOUT } from '@/config/api'

// 创建axios实例 - Admin Service
const service = axios.create({
  baseURL: API_BASE_URLS.admin,
  timeout: REQUEST_TIMEOUT
})


// System Service 请求拦截器
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// System Service 响应拦截器
service.interceptors.response.use(
  response => response.data,
  error => {
    console.error('响应错误:', error)
    ElMessage({
      message: error.response?.data?.message || '请求失败',
      type: 'error',
      duration: 3000
    })
    return Promise.reject(error)
  }
)

// 请求拦截器
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的状态码不是200，则认为是错误
    if (res.code !== undefined && res.code !== 200) {
      ElMessage({
        message: res.message || '请求失败',
        type: 'error',
        duration: 3000
      })
      
      // 401: 未授权，跳转到登录页
      if (res.code === 401) {
        const userStore = useUserStore()
        userStore.logout()
        router.push('/login')
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  error => {
    console.error('响应错误:', error)
    
    let message = '请求失败'
    if (error.response) {
      switch (error.response.status) {
        case 401:
          message = '未授权，请重新登录'
          const userStore = useUserStore()
          userStore.logout()
          router.push('/login')
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求地址不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data?.message || '请求失败'
      }
    } else if (error.message) {
      if (error.message.includes('timeout')) {
        message = '请求超时'
      } else if (error.message.includes('Network Error')) {
        message = '网络错误'
      }
    }
    
    ElMessage({
      message,
      type: 'error',
      duration: 3000
    })
    
    return Promise.reject(error)
  }
)

export default service

// 额外导出按微服务区分的客户端实例
function createClient(baseURL) {
  const client = axios.create({
    baseURL,
    timeout: REQUEST_TIMEOUT
  })

  client.interceptors.request.use(
    config => {
      const userStore = useUserStore()
      if (userStore.token) {
        config.headers['Authorization'] = `Bearer ${userStore.token}`
      }
      return config
    },
    error => Promise.reject(error)
  )

  client.interceptors.response.use(
    response => {
      const res = response.data
      if (res?.code !== undefined && res.code !== 200) {
        ElMessage({ message: res.message || '请求失败', type: 'error', duration: 3000 })
        if (res.code === 401) {
          const userStore = useUserStore()
          userStore.logout()
          router.push('/login')
        }
        return Promise.reject(new Error(res.message || '请求失败'))
      }
      return res
    },
    error => {
      let message = error.response?.data?.message || error.message || '请求失败'
      if (typeof message === 'string' && message.includes('timeout')) message = '请求超时'
      if (typeof message === 'string' && message.includes('Network Error')) message = '网络错误'
      ElMessage({ message, type: 'error', duration: 3000 })
      return Promise.reject(error)
    }
  )

  return client
}

// 导出各微服务的客户端实例
export const adminService = createClient(API_BASE_URLS.admin)
export const systemService = createClient(API_BASE_URLS.system)
export const crawlerService = createClient(API_BASE_URLS.crawler)
export const aiService = createClient(API_BASE_URLS.ai)
