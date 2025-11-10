import { adminService } from '@/utils/request'

/**
 * 获取角色列表
 * @param {number} skip - 跳过的记录数
 * @param {number} limit - 返回的最大记录数
 */
export function getRoleList(skip = 0, limit = 100) {
  return adminService({
    url: '/roles/',
    method: 'get',
    params: { skip, limit }
  })
}

/**
 * 获取角色详情
 * @param {number} id - 角色ID
 */
export function getRole(id) {
  return adminService({
    url: `/roles/${id}`,
    method: 'get'
  })
}

/**
 * 创建角色
 * @param {object} data - 角色数据
 */
export function createRole(data) {
  return adminService({
    url: '/roles/',
    method: 'post',
    data
  })
}

/**
 * 更新角色
 * @param {number} id - 角色ID
 * @param {object} data - 角色数据
 */
export function updateRole(id, data) {
  return adminService({
    url: `/roles/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除角色
 * @param {number} id - 角色ID
 */
export function deleteRole(id) {
  return adminService({
    url: `/roles/${id}`,
    method: 'delete'
  })
}
