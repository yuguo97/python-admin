import { systemService } from '@/utils/request'

/**
 * 获取系统信息
 */
export function getSystemInfo() {
  return systemService({
    url: '/system/info',
    method: 'get'
  })
}

/**
 * 获取CPU信息
 */
export function getCpuInfo() {
  return systemService({
    url: '/system/cpu',
    method: 'get'
  })
}

/**
 * 获取内存信息
 */
export function getMemoryInfo() {
  return systemService({
    url: '/system/memory',
    method: 'get'
  })
}

/**
 * 获取磁盘信息
 */
export function getDiskInfo() {
  return systemService({
    url: '/system/disk',
    method: 'get'
  })
}

/**
 * 获取服务列表
 */
export function getServiceList() {
  return systemService({
    url: '/services',
    method: 'get'
  })
}

/**
 * 启动服务
 */
export function startService(serviceName) {
  return systemService({
    url: `/services/${serviceName}/start`,
    method: 'post'
  })
}

/**
 * 停止服务
 */
export function stopService(serviceName) {
  return systemService({
    url: `/services/${serviceName}/stop`,
    method: 'post'
  })
}
