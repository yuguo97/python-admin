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

// 根据权限过滤后的菜单
const routes = computed(() => {
  const menuCodes = userStore.menuCodes || []
  return filterMenus(JSON.parse(JSON.stringify(allRoutes)), menuCodes)
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
