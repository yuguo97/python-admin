# Views 目录结构说明

## 目录组织

```
views/
├── Login.vue              # 登录页面
├── Dashboard.vue          # 首页/仪表盘
├── system/               # 系统管理模块
│   ├── Users.vue         # 用户管理
│   ├── Roles.vue         # 角色管理
│   ├── Permissions.vue   # 权限管理
│   └── Menus.vue         # 菜单管理
└── example/              # 示例页面
```

## 菜单编码规范

### 编码格式
使用 **冒号分隔** 的层级结构:
- 一级菜单: `模块名`
- 二级菜单: `模块名:功能名`
- 三级菜单: `模块名:功能名:子功能名`

### 当前菜单编码

| 菜单路径 | 菜单名称 | 菜单编码 | 说明 |
|---------|---------|---------|------|
| `/dashboard` | 首页 | `dashboard` | 一级菜单 |
| `/system` | 系统管理 | `system` | 一级菜单 |
| `/system/users` | 用户管理 | `system:user` | 二级菜单 |
| `/system/roles` | 角色管理 | `system:role` | 二级菜单 |
| `/system/permissions` | 权限管理 | `system:permission` | 二级菜单 |
| `/system/menus` | 菜单管理 | `system:menu` | 二级菜单 |

### 编码命名规则

1. **使用小写字母**
2. **使用冒号(:)分隔层级**
3. **使用单数形式** (user 而不是 users)
4. **简洁明了** (permission 而不是 permission_management)

### 示例

```javascript
// ✅ 正确
'system:user'
'system:role'
'content:article'
'content:article:publish'

// ❌ 错误
'system_user'        // 不要使用下划线
'system:users'       // 不要使用复数
'SystemUser'         // 不要使用大写
'system-user'        // 不要使用连字符
```

## 路由配置

### 路由命名规范
- 使用 PascalCase
- 包含模块前缀
- 示例: `SystemUsers`, `SystemRoles`

### 路由meta配置
```javascript
{
  path: 'users',
  name: 'SystemUsers',
  component: () => import('@/views/system/Users.vue'),
  meta: {
    title: '用户管理',      // 显示标题
    icon: 'User',           // 图标
    menuCode: 'system:user' // 菜单编码(用于权限控制)
  }
}
```

## 添加新模块

### 1. 创建模块目录
```bash
mkdir src/views/模块名
```

### 2. 添加页面文件
```bash
# 例如: 内容管理模块
src/views/content/
├── Articles.vue
├── Categories.vue
└── Tags.vue
```

### 3. 配置路由
```javascript
{
  path: '/content',
  component: () => import('@/layout/Index.vue'),
  redirect: '/content/articles',
  meta: { title: '内容管理', icon: 'Document', menuCode: 'content' },
  children: [
    {
      path: 'articles',
      name: 'ContentArticles',
      component: () => import('@/views/content/Articles.vue'),
      meta: { title: '文章管理', icon: 'Document', menuCode: 'content:article' }
    }
  ]
}
```

### 4. 更新权限管理
在 `views/system/Permissions.vue` 中添加新菜单:
```javascript
{
  code: 'content',
  title: '内容管理',
  icon: 'Document',
  children: [
    {
      code: 'content:article',
      title: '文章管理',
      icon: 'Document'
    }
  ]
}
```

## 权限控制

### 路由守卫
在路由守卫中检查用户是否有权限访问:
```javascript
router.beforeEach((to, from, next) => {
  const menuCode = to.meta.menuCode
  const userMenuCodes = userStore.menuCodes // 用户拥有的菜单编码
  
  if (menuCode && !userMenuCodes.includes(menuCode)) {
    next('/403') // 无权限
  } else {
    next()
  }
})
```

### 按钮权限
使用自定义指令控制按钮显示:
```vue
<el-button v-permission="'system:user:create'">新增用户</el-button>
<el-button v-permission="'system:user:edit'">编辑</el-button>
<el-button v-permission="'system:user:delete'">删除</el-button>
```

## 最佳实践

1. **模块化**: 相关功能放在同一目录下
2. **命名一致**: 文件名、路由名、组件名保持一致
3. **编码规范**: 严格遵循菜单编码规范
4. **权限细化**: 可以细化到按钮级别的权限控制
5. **文档更新**: 添加新模块时及时更新文档

## 注意事项

1. 菜单编码一旦确定,不要轻易修改
2. 删除菜单时,需要同步删除相关的权限配置
3. 新增模块时,需要在权限管理页面添加对应的菜单树节点
4. 路由路径和菜单编码要保持对应关系
