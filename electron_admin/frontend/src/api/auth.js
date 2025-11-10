import { adminService } from '@/utils/request'

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 */
export function login(username, password) {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)

  return adminService({
    url: '/auth/login',
    method: 'post',
    data: params,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

/**
 * 刷新令牌
 */
export function refreshToken() {
  return adminService({
    url: '/auth/refresh-token',
    method: 'post'
  })
}

/**
 * 获取当前用户信息
 */
export function getUserInfo() {
  return adminService({
    url: '/users/me',
    method: 'get'
  })
}
