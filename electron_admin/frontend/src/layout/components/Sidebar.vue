<template>
  <div class="sidebar-wrapper">
    <div class="sidebar-logo">
      <router-link to="/" class="sidebar-logo-link">
        <img v-if="logo" :src="logo" class="sidebar-logo-img" />
        <h1 class="sidebar-title" :class="{ 'hide-title': !sidebar.opened }">
          {{ title }}
        </h1>
      </router-link>
    </div>
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="!sidebar.opened"
        :background-color="variables.menuBg"
        :text-color="variables.menuText"
        :active-text-color="variables.menuActiveText"
        :unique-opened="false"
        :collapse-transition="false"
        mode="vertical"
      >
        <SidebarItem
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import SidebarItem from './SidebarItem.vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()

const sidebar = computed(() => appStore.sidebar)
const activeMenu = computed(() => route.path)

const title = '后台管理系统'
const logo = null

const variables = {
  menuBg: '#304156',
  menuText: '#bfcbd9',
  menuActiveText: '#409EFF'
}

// 所有菜单配置(带菜单编码)
const allRoutes = [
  {
    path: '/dashboard',
    meta: { title: '首页', icon: 'HomeFilled', menuCode: 'dashboard' }
  },
  {
    path: '/app',
    meta: { title: '应用管理', icon: 'Monitor', menuCode: 'app' },
    children: [
      {
        path: '/app/services',
        meta: { title: '服务管理', icon: 'Monitor', menuCode: 'app:services' }
      },
      {
        path: '/app/systeminfo',
        meta: { title: '系统信息', icon: 'DataAnalysis', menuCode: 'app:systeminfo' }
      }
    ]
  },
  {
    path: '/system',
    meta: { title: '系统管理', icon: 'Setting', menuCode: 'system' },
    children: [
      {
        path: '/system/users',
        meta: { title: '用户管理', icon: 'User', menuCode: 'system:user' }
      },
      {
        path: '/system/roles',
        meta: { title: '角色管理', icon: 'UserFilled', menuCode: 'system:role' }
      },
      {
        path: '/system/permissions',
        meta: { title: '权限管理', icon: 'Lock', menuCode: 'system:permission' }
      },
      {
        path: '/system/menus',
        meta: { title: '菜单管理', icon: 'Menu', menuCode: 'system:menu' }
      }
    ]
  }
]

// 根据用户权限过滤菜单
const filterMenus = (menus, menuCodes) => {
  return menus.filter(menu => {
    const menuCode = menu.meta?.menuCode
    if (!menuCode) return true
    
    // 检查是否有权限
    const hasPermission = menuCodes.includes(menuCode)
    if (!hasPermission) return false
    
    // 如果有子菜单,递归过滤
    if (menu.children) {
      menu.children = filterMenus(menu.children, menuCodes)
      // 如果所有子菜单都被过滤掉了,也不显示父菜单
      return menu.children.length > 0
    }
    
    return true
  })
}

// 将后端下发的菜单（userStore.menus）合并到本地路由定义后再按权限过滤
const routes = computed(() => {
  const menuCodes = userStore.menuCodes || []
  const userMenus = userStore.menus || []

  // 深拷贝一份基础路由定义，避免修改原始 allRoutes
  const baseRoutes = JSON.parse(JSON.stringify(allRoutes))

  // Helper: 找到父节点，先按 menuCode 匹配其 meta.menuCode，再按 path 的最后一段匹配
  const findParent = (parentKey) => {
    if (!parentKey) return null
    let p = baseRoutes.find(r => r.meta?.menuCode === parentKey)
    if (p) return p
    // 尝试按 path 尾部匹配 (例如 parentKey === 'system' -> path '/system')
    p = baseRoutes.find(r => r.path === `/${parentKey}` || r.path === parentKey)
    return p || null
  }

  // 合并后端菜单到 baseRoutes
  userMenus.forEach(m => {
    try {
      // 支持后端不同字段名: path / route / url
      const rawPath = m.path || m.route || m.url || (m.meta && m.meta.path)
      if (!rawPath) return

      const itemPath = rawPath.startsWith('/') ? rawPath : `/${rawPath}`

      // 构建 node.meta，优先使用后端 meta 中的信息
      const metaFromBackend = m.meta || {}
      const node = {
        path: itemPath,
        meta: {
          title: metaFromBackend.title || m.title || m.name || '未命名',
          icon: metaFromBackend.icon || m.icon,
          menuCode: metaFromBackend.menuCode || m.menuCode || m.menu_code || metaFromBackend.menu_code
        }
      }

      // 支持 parent 字段可能在多个位置（m.parent, m.meta.parent, m.parent_code）
      const parentKey = m.parent || metaFromBackend.parent || m.parent_code || metaFromBackend.parent_code

      const parent = findParent(parentKey)
      if (parent) {
        parent.children = parent.children || []
        // 避免重复添加（按 path 或 menuCode 识别）
        const exists = parent.children.find(ch => ch.path === node.path || ch.meta?.menuCode === node.meta.menuCode)
        if (!exists) {
          parent.children.push(node)
        }
      } else {
        // 若未找到父节点, 将其作为顶级项加入（避免重复）
        const existsTop = baseRoutes.find(r => r.path === node.path || r.meta?.menuCode === node.meta.menuCode)
        if (!existsTop) baseRoutes.push(node)
      }
    } catch (e) {
      console.error('合并后端菜单失败:', e, m)
    }
  })

  return filterMenus(baseRoutes, menuCodes)
})
</script>

<style lang="less" scoped>
.sidebar-wrapper {
  height: 100%;
  background-color: #304156;
}

.sidebar-logo {
  position: relative;
  width: 100%;
  height: 50px;
  line-height: 50px;
  background: #2b2f3a;
  text-align: center;
  overflow: hidden;

  .sidebar-logo-link {
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    .sidebar-logo-img {
      width: 32px;
      height: 32px;
      vertical-align: middle;
      margin-right: 12px;
    }

    .sidebar-title {
      display: inline-block;
      margin: 0;
      color: #fff;
      font-weight: 600;
      line-height: 50px;
      font-size: 14px;
      font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
      vertical-align: middle;
      transition: all 0.3s;
      
      &.hide-title {
        display: none;
      }
    }
  }
}

.el-menu {
  border: none;
  height: 100%;
  width: 100% !important;
}

:deep(.scrollbar-wrapper) {
  overflow-x: hidden !important;
}
</style>
