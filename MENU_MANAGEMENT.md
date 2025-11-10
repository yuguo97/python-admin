# 菜单管理说明

## 菜单编码规则

### 自动生成机制
菜单编码由路由路径自动生成,不可手动修改。

### 生成规则

1. **一级菜单**: 直接使用路径作为编码
   ```
   路径: dashboard
   编码: dashboard
   ```

2. **二级菜单**: 父级编码 + 冒号 + 子路径
   ```
   父级编码: system
   子路径: user
   编码: system:user
   ```

3. **三级菜单**: 父级编码 + 冒号 + 子路径
   ```
   父级编码: system:user
   子路径: detail
   编码: system:user:detail
   ```

## 路由路径规范

### 一级菜单
- 使用完整路径,不带斜杠
- 示例: `dashboard`, `system`

### 子菜单
- 使用相对路径,不带斜杠开头
- 示例: `users`, `roles`, `permissions`

### 完整路由
系统会自动拼接完整路由:
```
父级路径: /system
子路径: users
完整路由: /system/users
```

## 当前菜单配置

| 菜单名称 | 菜单编码 | 路由路径 | 完整路由 | 层级 |
|---------|---------|---------|---------|------|
| 首页 | `dashboard` | `dashboard` | `/dashboard` | 1级 |
| 系统管理 | `system` | `system` | `/system` | 1级 |
| 用户管理 | `system:user` | `users` | `/users` | 2级 |
| 角色管理 | `system:role` | `roles` | `/roles` | 2级 |
| 权限管理 | `system:permission` | `permissions` | `/permissions` | 2级 |
| 菜单管理 | `system:menu` | `menus` | `/menus` | 2级 |

## 动态路由配置

### 路由结构
```javascript
{
  path: '/',
  component: Layout,
  children: [
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { 
        title: '首页', 
        icon: 'HomeFilled', 
        menuCode: 'dashboard' 
      }
    },
    {
      path: 'users',
      name: 'SystemUsers',
      component: () => import('@/views/system/Users.vue'),
      meta: { 
        title: '用户管理', 
        icon: 'User', 
        menuCode: 'system:user' 
      }
    }
  ]
}
```

### 路由元信息
- `title`: 菜单显示名称
- `icon`: 菜单图标
- `menuCode`: 菜单编码(用于权限控制)

## 菜单管理页面

### 显示字段
- ✅ 菜单名称
- ✅ 菜单编码 (新增)
- ✅ 路由路径 (优化)
- ✅ 图标
- ✅ 排序
- ✅ 可见性
- ✅ 创建时间

### 表单字段
- **菜单名称**: 手动输入
- **菜单编码**: 自动生成,禁止编辑
- **路由路径**: 手动输入,自动生成编码
- **图标**: 手动输入
- **父级菜单**: 下拉选择
- **排序**: 数字输入
- **可见性**: 开关

### 路径输入提示
```
子菜单路径不需要斜杠开头,如: users, roles
```

### 编码生成提示
```
菜单编码由路径自动生成,不可手动修改
```

## 添加新菜单示例

### 示例1: 添加一级菜单
```
菜单名称: 内容管理
路由路径: content
图标: Document
父级菜单: (不选)

自动生成:
菜单编码: content
完整路由: /content
```

### 示例2: 添加二级菜单
```
菜单名称: 文章管理
路由路径: articles
图标: Document
父级菜单: 内容管理

自动生成:
菜单编码: content:article
完整路由: /articles
```

## 权限控制

### 菜单权限
在权限管理页面,通过菜单编码控制用户可见的菜单:
```javascript
// 用户拥有的菜单编码
userMenuCodes = ['dashboard', 'system', 'system:user']

// 过滤菜单
visibleMenus = allMenus.filter(menu => 
  userMenuCodes.includes(menu.code)
)
```

### 路由守卫
```javascript
router.beforeEach((to, from, next) => {
  const menuCode = to.meta.menuCode
  if (menuCode && !userMenuCodes.includes(menuCode)) {
    next('/403') // 无权限
  } else {
    next()
  }
})
```

## 注意事项

1. **编码唯一性**: 菜单编码必须唯一,不能重复
2. **路径规范**: 子菜单路径不要以斜杠开头
3. **层级限制**: 建议最多3级菜单,避免层级过深
4. **图标命名**: 使用Element Plus图标名称,如: `User`, `Setting`
5. **排序规则**: 数字越小越靠前
6. **删除限制**: 删除父菜单会同时删除所有子菜单

## 最佳实践

1. **命名规范**: 菜单名称简洁明了,路径使用英文小写
2. **图标选择**: 选择与功能相关的图标
3. **合理分组**: 相关功能放在同一父菜单下
4. **权限细化**: 通过菜单编码实现细粒度权限控制
5. **动态加载**: 根据用户权限动态加载菜单和路由
