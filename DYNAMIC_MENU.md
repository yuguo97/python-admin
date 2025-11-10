# 动态菜单权限系统

## 功能概述

实现基于用户角色的动态菜单权限控制,用户登录后根据其角色权限动态显示菜单。

## 实现流程

### 1. 用户登录
```
用户登录 → 获取Token → 获取用户信息 → 获取菜单权限 → 渲染菜单
```

### 2. 权限获取
后端API `/users/me` 返回用户信息时包含菜单权限:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "admin",
    "roles": [
      {
        "id": 1,
        "name": "超级管理员",
        "code": "fcadmin"
      }
    ],
    "menu_codes": [
      "dashboard",
      "system",
      "system:user",
      "system:role",
      "system:permission",
      "system:menu"
    ]
  }
}
```

### 3. 菜单过滤
前端根据 `menu_codes` 过滤菜单:
```javascript
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
      return menu.children.length > 0
    }
    
    return true
  })
}
```

## 后端实现

### 获取用户菜单权限
```python
@app.get("/users/me")
async def get_current_user_info(db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    user = models.User.get_by_id(db, int(user_id))
    user_dict = user.to_dict()
    
    # 获取用户的菜单权限
    menu_codes = []
    for role in user.roles:
        if role.code == "fcadmin":
            # 超级管理员拥有所有权限
            menu_codes = ["dashboard", "system", "system:user", ...]
            break
        else:
            # 查询角色的菜单权限
            sql = text("SELECT menu_code FROM role_menus WHERE role_id = :role_id")
            result = db.execute(sql, {"role_id": role.id})
            menu_codes.extend([row[0] for row in result])
    
    user_dict["menu_codes"] = list(set(menu_codes))
    return success_response(user_dict)
```

## 前端实现

### 1. 用户Store
```javascript
// stores/user.js
export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: null,
    menuCodes: []  // 菜单权限编码
  }),
  
  actions: {
    async fetchUserInfo() {
      const res = await getUserInfo()
      this.userInfo = res.data
      this.menuCodes = res.data.menu_codes || []
    }
  }
})
```

### 2. 侧边栏组件
```vue
<!-- Sidebar.vue -->
<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 所有菜单配置
const allRoutes = [
  {
    path: '/dashboard',
    meta: { title: '首页', icon: 'HomeFilled', menuCode: 'dashboard' }
  },
  {
    path: '/system',
    meta: { title: '系统管理', icon: 'Setting', menuCode: 'system' },
    children: [
      {
        path: '/users',
        meta: { title: '用户管理', icon: 'User', menuCode: 'system:user' }
      }
    ]
  }
]

// 根据权限过滤菜单
const routes = computed(() => {
  const menuCodes = userStore.menuCodes || []
  return filterMenus(JSON.parse(JSON.stringify(allRoutes)), menuCodes)
})
</script>
```

### 3. 路由守卫
```javascript
// router/index.js
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const menuCode = to.meta.menuCode
  
  // 检查菜单权限
  if (menuCode && !userStore.menuCodes.includes(menuCode)) {
    next('/403') // 无权限
  } else {
    next()
  }
})
```

## 菜单配置

### 菜单编码规范
每个菜单必须配置 `menuCode`:
```javascript
{
  path: '/users',
  meta: {
    title: '用户管理',
    icon: 'User',
    menuCode: 'system:user'  // 必须配置
  }
}
```

### 当前菜单编码

| 菜单 | 编码 | 说明 |
|-----|------|------|
| 首页 | `dashboard` | 一级菜单 |
| 系统管理 | `system` | 一级菜单 |
| 用户管理 | `system:user` | 二级菜单 |
| 角色管理 | `system:role` | 二级菜单 |
| 权限管理 | `system:permission` | 二级菜单 |
| 菜单管理 | `system:menu` | 二级菜单 |

## 权限管理优化

### 默认选择第一条数据
```javascript
const fetchRoles = async () => {
  const res = await getRoleList()
  if (res.data) {
    roleList.value = res.data
    // 默认选择第一条数据
    if (res.data.length > 0 && !selectedRole.value) {
      handleSelectRole(res.data[0])
    }
  }
}
```

## 菜单管理优化

### 显示菜单编码
在菜单管理页面的表格中添加菜单编码列:
```vue
<el-table-column prop="code" label="菜单编码" min-width="150">
  <template #default="{ row }">
    <el-tag size="small" type="info">{{ row.code }}</el-tag>
  </template>
</el-table-column>
```

## 使用场景

### 场景1: 普通管理员
```
角色: 管理员
权限: dashboard, system, system:user, system:role
显示菜单:
  - 首页
  - 系统管理
    - 用户管理
    - 角色管理
```

### 场景2: 编辑人员
```
角色: 编辑
权限: dashboard
显示菜单:
  - 首页
```

### 场景3: 超级管理员
```
角色: 超级管理员 (fcadmin)
权限: 所有菜单
显示菜单:
  - 首页
  - 系统管理
    - 用户管理
    - 角色管理
    - 权限管理
    - 菜单管理
```

## 优势

1. **动态性**: 菜单根据用户权限动态生成
2. **安全性**: 前后端双重验证,确保权限安全
3. **灵活性**: 可以灵活配置不同角色的菜单权限
4. **可维护性**: 菜单配置集中管理,易于维护
5. **用户体验**: 用户只看到有权限的菜单,界面更简洁

## 注意事项

1. **菜单编码唯一性**: 每个菜单的编码必须唯一
2. **权限同步**: 修改权限后需要重新登录才能生效
3. **父子关系**: 如果父菜单没有权限,子菜单也不会显示
4. **路由守卫**: 即使隐藏了菜单,也要在路由守卫中验证权限
5. **超级管理员**: 超级管理员默认拥有所有权限

## 扩展功能

### 1. 按钮级权限
```vue
<el-button v-permission="'system:user:create'">新增</el-button>
<el-button v-permission="'system:user:edit'">编辑</el-button>
<el-button v-permission="'system:user:delete'">删除</el-button>
```

### 2. 数据权限
```javascript
// 根据用户角色过滤数据
const filterData = (data) => {
  if (isSuperAdmin) {
    return data // 查看所有数据
  } else {
    return data.filter(item => item.creator_id === userId) // 只看自己的数据
  }
}
```

### 3. 动态路由
```javascript
// 根据权限动态添加路由
const addDynamicRoutes = (menuCodes) => {
  menuCodes.forEach(code => {
    const route = routeMap[code]
    if (route) {
      router.addRoute(route)
    }
  })
}
```
