import { adminService } from '@/utils/request'

/**
 * 获取角色的菜单权限
 * @param {number} roleId - 角色ID
 */
export function getRoleMenus(roleId) {
  return adminService({
    url: `/roles/${roleId}/menus`,
    method: 'get'
  })
}

/**
 * 更新角色的菜单权限
 * @param {number} roleId - 角色ID
 * @param {array} menuCodes - 菜单编码数组
 */
export function updateRoleMenus(roleId, menuCodes) {
  return adminService({
    url: `/roles/${roleId}/menus`,
    method: 'post',
    data: { menu_codes: menuCodes }
  })
}
