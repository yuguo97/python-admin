/**
 * API 配置文件
 * 统一管理所有微服务的基础配置
 */

// 网关地址（从环境变量读取，默认本地开发地址）
export const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8999'

// 各微服务通过网关访问的基础路径
// 格式: {网关地址}/{服务名}
export const API_BASE_URLS = {
  // 管理服务 - 用户、角色、权限、菜单管理
  admin: `${GATEWAY_URL}/admin`,
  
  // 系统服务 - 系统信息、监控
  system: `${GATEWAY_URL}/system`,
  
  // 爬虫服务 - 爬虫任务管理
  crawler: `${GATEWAY_URL}/crawler`,
  
  // AI服务 - AI相关功能
  ai: `${GATEWAY_URL}/ai`
}

// 请求超时配置
export const REQUEST_TIMEOUT = 15000

// API 版本
export const API_VERSION = 'v1'

// 导出默认配置
export default {
  GATEWAY_URL,
  API_BASE_URLS,
  REQUEST_TIMEOUT,
  API_VERSION
}
