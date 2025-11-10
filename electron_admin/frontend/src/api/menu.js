import { adminService } from '@/utils/request'

/**
 * 获取菜单树
 */
export function getMenuTree() {
  return adminService({
    url: '/menus',
    method: 'get'
  })
}

/**
 * 获取菜单详情
 * @param {number} id - 菜单ID
 */
export function getMenu(id) {
  return adminService({
    url: `/menus/${id}`,
    method: 'get'
  })
}

/**
 * 创建菜单
 * @param {object} data - 菜单数据
 */
export function createMenu(data) {
  return adminService({
    url: '/menus',
    method: 'post',
    data
  })
}

/**
 * 更新菜单
 * @param {number} id - 菜单ID
 * @param {object} data - 菜单数据
 */
export function updateMenu(id, data) {
  return adminService({
    url: `/menus/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除菜单
 * @param {number} id - 菜单ID
 */
export function deleteMenu(id) {
  return adminService({
    url: `/menus/${id}`,
    method: 'delete'
  })
}
