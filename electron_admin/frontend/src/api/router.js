import request from '@/utils/request'

/**
 * 获取用户菜单路由
 */
export function getUserMenus() {
  return request({
    url: '/user/menus',
    method: 'get'
  })
}
