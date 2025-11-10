import { adminService } from '@/utils/request'

/**
 * 获取用户列表
 * @param {number} skip - 跳过的记录数
 * @param {number} limit - 返回的最大记录数
 */
export function getUserList(skip = 0, limit = 10) {
  return adminService({
    url: '/users',
    method: 'get',
    params: { skip, limit }
  })
}

/**
 * 获取用户详情
 * @param {number} id - 用户ID
 */
export function getUser(id) {
  return adminService({
    url: `/users/${id}`,
    method: 'get'
  })
}

/**
 * 创建用户
 * @param {object} data - 用户数据
 */
export function createUser(data) {
  return adminService({
    url: '/users',
    method: 'post',
    data
  })
}

/**
 * 更新用户
 * @param {number} id - 用户ID
 * @param {object} data - 用户数据
 */
export function updateUser(id, data) {
  return adminService({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 * @param {number} id - 用户ID
 */
export function deleteUser(id) {
  return adminService({
    url: `/users/${id}`,
    method: 'delete'
  })
}
