# 动态路由系统

## 功能概述

实现从后端接口动态获取菜单数据并生成前端路由,根据用户权限动态加载路由。

## 实现原理

### 1. 路由分类
- **静态路由**: 不需要权限的路由(如登录页)
- **动态路由**: 根据用户权限从后端获取的路由

### 2. 加载流程
```
用户登录 → 获取Token → 路由守卫检查 → 调用后端API → 获取菜单数据 → 动态添加路由 → 渲染页面
```

## 后端实现

### API接口: `/user/menus`
```python
@app.get("/user/menus")
async def get_user_menus(db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    """获取当前用户可见的菜单路由"""
    # 获取用户权限
    menu_codes = []
    for role in user.roles:
        if role.code == "fcadmin":
            menu_codes = ["dashboard", "system:user", ...]
        else:
            # 查询role_menus表
            ...
    
    # 返回菜单配置
    all_menus = [
        {
            "path": "dashboard",
            "name": "Dashboard",
            "component": "Dashboard",
            "meta": {
                "title": "首页",
                "icon": "HomeFilled",
                "menuCode": "dashboard"
            }
        },
        ...
    ]
    
    # 根据权限过滤
    filtered_menus = [menu for menu in all_menus if menu["meta"]["menuCode"] in menu_codes]
    return success_response(filtered_menus)
```

### 返回数据格式
```json
{
  "code": 200,
  "data": [
    {
      "path": "dashboard",
      "name": "Dashboard",
      "component": "Dashboard",
      "meta": {
        "title": "首页",
        "icon": "HomeFilled",
        "menuCode": "dashboard"
      }
    },
    {
      "path": "users",
      "name": "SystemUsers",
      "component": "system/Users",
      "meta": {
        "title": "用户管理",
        "icon": "User",
        "menuCode": "system:user"
      }
    }
  ]
}
```

## 前端实现

### 1. 路由配置 (`router/index.js`)

#### 静态路由
```javascript
const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/',
    component: () => import('@/layout/Index.vue'),
    redirect: '/dashboard',
    children: []  // 动态路由会添加到这里
  }
]
```

#### 组件映射表
```javascript
const componentMap = {
  'Dashboard': () => import('@/views/Dashboard.vue'),
  'system/Users': () => import('@/views/system/Users.vue'),
  'system/Roles': () => import('@/views/system/Roles.vue'),
  'system/Permissions': () => import('@/views/system/Permissions.vue'),
  'system/Menus': () => import('@/views/system/Menus.vue')
}
```

#### 动态添加路由
```javascript
export async function addDynamicRoutes() {
  const res = await getUserMenus()
  if (res.data && res.data.length > 0) {
    const routes = res.data.map(menu => ({
      path: menu.path,
      name: menu.name,
      component: componentMap[menu.component],
      meta: menu.meta
    }))
    
    // 添加到主路由的children中
    routes.forEach(route => {
      router.addRoute('/', route)
    })
    
    return true
  }
  return false
}
```

### 2. 路由守卫
```javascript
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const isLoggedIn = userStore.isLoggedIn
  
  if (to.path === '/login') {
    // 登录页逻辑
    next()
  } else {
    if (isLoggedIn) {
      // 如果已登录但还没有加载动态路由
      if (!userStore.routesLoaded) {
        try {
          await addDynamicRoutes()
          userStore.routesLoaded = true
          // 重新导航到目标路由
          next({ ...to, replace: true })
        } catch (error) {
          next('/login')
        }
      } else {
        next()
      }
    } else {
      next('/login')
    }
  }
})
```

### 3. 用户Store
```javascript
export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: null,
    menuCodes: [],
    routesLoaded: false  // 标记路由是否已加载
  }),
  
  actions: {
    logout() {
      this.token = ''
      this.userInfo = null
      this.menuCodes = []
      this.routesLoaded = false  // 重置状态
      localStorage.removeItem('token')
    }
  }
})
```

## 工作流程

### 首次登录
```
1. 用户输入账号密码
2. 调用登录API,获取Token
3. 保存Token到localStorage
4. 跳转到首页
5. 路由守卫检测到未加载路由
6. 调用 /user/menus 获取菜单数据
7. 动态添加路由
8. 标记 routesLoaded = true
9. 重新导航到目标页面
10. 渲染页面
```

### 刷新页面
```
1. 从localStorage读取Token
2. 路由守卫检测到已登录但未加载路由
3. 调用 /user/menus 获取菜单数据
4. 动态添加路由
5. 标记 routesLoaded = true
6. 渲染页面
```

### 登出
```
1. 清空Token
2. 清空用户信息
3. 重置 routesLoaded = false
4. 跳转到登录页
```

## 优势

### 1. 安全性
- 路由配置存储在后端,前端无法篡改
- 根据用户权限动态生成,无权限的路由不会被添加

### 2. 灵活性
- 新增菜单只需修改后端配置
- 不同用户看到不同的路由
- 支持多角色权限组合

### 3. 可维护性
- 路由配置集中管理
- 前端只需维护组件映射表
- 权限变更无需重新部署前端

### 4. 性能
- 按需加载,只加载有权限的路由
- 减少前端代码体积
- 提升首屏加载速度

## 扩展功能

### 1. 路由缓存
```javascript
// 缓存已加载的路由,避免重复请求
let cachedRoutes = null

export async function addDynamicRoutes() {
  if (cachedRoutes) {
    // 使用缓存
    cachedRoutes.forEach(route => {
      router.addRoute('/', route)
    })
    return true
  }
  
  // 首次加载
  const res = await getUserMenus()
  // ... 处理路由
  cachedRoutes = routes
}
```

### 2. 路由权限验证
```javascript
router.beforeEach((to, from, next) => {
  const menuCode = to.meta.menuCode
  const userStore = useUserStore()
  
  // 验证是否有权限访问
  if (menuCode && !userStore.menuCodes.includes(menuCode)) {
    next('/403')  // 无权限
  } else {
    next()
  }
})
```

### 3. 面包屑导航
```javascript
const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title)
})
```

## 注意事项

1. **组件路径**: 后端返回的 `component` 必须在 `componentMap` 中有对应的映射
2. **路由名称**: 每个路由的 `name` 必须唯一
3. **刷新问题**: 刷新页面会重新加载路由,需要保持Token有效
4. **404页面**: 动态路由加载完成后再添加404路由
5. **权限同步**: 修改权限后需要重新登录或刷新页面

## 调试技巧

### 查看已加载的路由
```javascript
console.log(router.getRoutes())
```

### 查看当前路由
```javascript
console.log(router.currentRoute.value)
```

### 手动添加路由
```javascript
router.addRoute('/', {
  path: 'test',
  name: 'Test',
  component: () => import('@/views/Test.vue')
})
```

## 常见问题

### Q1: 刷新页面后路由丢失?
**A**: 检查Token是否有效,路由守卫是否正确执行

### Q2: 动态路由不生效?
**A**: 检查组件映射表是否包含对应的组件路径

### Q3: 权限修改后不生效?
**A**: 需要重新登录或清除缓存后刷新页面

### Q4: 404页面一直显示?
**A**: 确保404路由在动态路由加载完成后添加
