import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import store from '../store'

const service = axios.create({
  baseURL: '/api',
  timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = store.state.token
    if (token) {
      config.headers['Authorization'] = token
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) {
      return res
    }
    
    // 显示错误消息
    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        store.commit('clearToken')
        router.push({
          path: '/login',
          query: { redirect: router.currentRoute.value.fullPath }
        })
        ElMessage.error(data.message || '登录已过期，请重新登录')
      } else {
        ElMessage.error(data.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default service 