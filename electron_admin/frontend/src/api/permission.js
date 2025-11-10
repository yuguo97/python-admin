import { adminService } from '@/utils/request'

/**
 * 获取权限列表
 * @param {number} skip - 跳过的记录数
 * @param {number} limit - 返回的最大记录数
 */
export function getPermissionList(skip = 0, limit = 100) {
  return adminService({
    url: '/permissions/',
    method: 'get',
    params: { skip, limit }
  })
}

/**
 * 获取权限详情
 * @param {number} id - 权限ID
 */
export function getPermission(id) {
  return adminService({
    url: `/permissions/${id}`,
    method: 'get'
  })
}

/**
 * 创建权限
 * @param {object} data - 权限数据
 */
export function createPermission(data) {
  return adminService({
    url: '/permissions/',
    method: 'post',
    data
  })
}

/**
 * 更新权限
 * @param {number} id - 权限ID
 * @param {object} data - 权限数据
 */
export function updatePermission(id, data) {
  return adminService({
    url: `/permissions/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除权限
 * @param {number} id - 权限ID
 */
export function deletePermission(id) {
  return adminService({
    url: `/permissions/${id}`,
    method: 'delete'
  })
}
