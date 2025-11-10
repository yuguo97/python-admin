import { adminService } from '@/utils/request'

/**
 * 获取服务列表
 */
export function getServiceList() {
  return adminService({
    url: '/services',
    method: 'get'
  })
}

/**
 * 启动服务
 * @param {string} serviceName - 服务名称
 */
export function startService(serviceName) {
  return adminService({
    url: `/services/${serviceName}/start`,
    method: 'post'
  })
}

/**
 * 停止服务
 * @param {string} serviceName - 服务名称
 */
export function stopService(serviceName) {
  return adminService({
    url: `/services/${serviceName}/stop`,
    method: 'post'
  })
}

/**
 * 重启服务
 * @param {string} serviceName - 服务名称
 */
export function restartService(serviceName) {
  return adminService({
    url: `/services/${serviceName}/restart`,
    method: 'post'
  })
}

/**
 * 获取服务状态
 * @param {string} serviceName - 服务名称
 */
export function getServiceStatus(serviceName) {
  return adminService({
    url: `/services/${serviceName}/status`,
    method: 'get'
  })
}
