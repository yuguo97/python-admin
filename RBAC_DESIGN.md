# RBAC权限管理系统设计

## 设计理念

采用基于角色的访问控制(RBAC)模型:
- **用户(User)** ←→ **角色(Role)** ←→ **菜单(Menu)**
- 通过角色关联菜单,实现权限控制

## 数据库设计

### 1. 角色表 (roles)
```sql
- id: 主键
- name: 角色名称
- code: 角色编码 (如: fcadmin, admin, editor)
- description: 描述
- created_at: 创建时间
- updated_at: 更新时间
```

### 2. 角色-菜单关联表 (role_menus)
```sql
- role_id: 角色ID
- menu_code: 菜单编码
- PRIMARY KEY (role_id, menu_code)
```

### 3. 用户-角色关联表 (user_roles)
```sql
- user_id: 用户ID
- role_id: 角色ID
- PRIMARY KEY (user_id, role_id)
```

## 菜单编码规范

菜单编码由路径自动生成,不可编辑:

| 菜单编码 | 菜单名称 | 路径 | 父级 |
|---------|---------|------|------|
| `dashboard` | 首页 | /dashboard | - |
| `system` | 系统管理 | /system | - |
| `system_users` | 用户管理 | /users | system |
| `system_roles` | 角色管理 | /roles | system |
| `system_permissions` | 权限管理 | /permissions | system |
| `system_menus` | 菜单管理 | /menus | system |

**编码规则**:
- 一级菜单: 直接使用路径名 (如: `dashboard`)
- 子菜单: `父级编码_路径名` (如: `system_users`)
- 使用下划线分隔,全小写

## 权限管理界面

### 布局设计
```
┌─────────────────────────────────────────┐
│           权限管理                        │
├──────────┬──────────────────────────────┤
│ 角色列表  │  菜单权限树                   │
│          │                              │
│ □ 超级管理│  ☑ 首页                      │
│ ■ 管理员  │  ☑ 系统管理                  │
│ □ 编辑    │    ☑ 用户管理                │
│ □ 访客    │    ☑ 角色管理                │
│          │    ☑ 权限管理                │
│          │    ☐ 菜单管理                │
│          │                              │
│          │  [保存权限]                  │
└──────────┴──────────────────────────────┘
```

### 功能说明
1. **左侧**: 显示所有角色列表,点击选择
2. **右侧**: 显示菜单树,支持多选
3. **操作**: 选择菜单后点击"保存权限"

## API接口

### 1. 获取角色的菜单权限
```
GET /roles/{role_id}/menus
Response: {
  "code": 200,
  "data": {
    "menu_codes": ["dashboard", "system", "system_users"]
  }
}
```

### 2. 更新角色的菜单权限
```
POST /roles/{role_id}/menus
Body: {
  "menu_codes": ["dashboard", "system", "system_users", "system_roles"]
}
Response: {
  "code": 200,
  "data": {
    "message": "权限更新成功"
  }
}
```

## 权限控制流程

### 1. 用户登录
```
用户登录 → 获取用户角色 → 获取角色菜单权限 → 生成前端菜单
```

### 2. 菜单渲染
```javascript
// 根据用户的菜单权限过滤菜单
const userMenuCodes = ['dashboard', 'system', 'system_users']
const filteredMenus = allMenus.filter(menu => 
  userMenuCodes.includes(menu.code)
)
```

### 3. 路由守卫
```javascript
router.beforeEach((to, from, next) => {
  const menuCode = to.meta.menuCode
  if (userMenuCodes.includes(menuCode)) {
    next()
  } else {
    next('/403') // 无权限
  }
})
```

## 使用示例

### 1. 创建角色并分配权限
```bash
# 1. 创建角色
POST /roles/
{
  "name": "编辑",
  "code": "editor",
  "description": "内容编辑人员"
}

# 2. 分配菜单权限
POST /roles/1/menus
{
  "menu_codes": ["dashboard", "system", "system_users"]
}
```

### 2. 为用户分配角色
```bash
# 创建用户时指定角色
POST /users
{
  "username": "editor1",
  "email": "editor1@example.com",
  "password": "123456",
  "role_ids": [1]  # 编辑角色
}
```

### 3. 用户登录后获取菜单
```bash
# 1. 登录
POST /auth/login
{
  "username": "editor1",
  "password": "123456"
}

# 2. 获取用户信息(包含角色)
GET /users/me

# 3. 根据角色获取菜单权限
GET /roles/1/menus

# 4. 前端根据菜单权限渲染菜单
```

## 优势

1. **灵活性**: 通过角色-菜单关联,可以灵活配置权限
2. **可维护性**: 菜单编码统一管理,易于维护
3. **扩展性**: 可以轻松添加新菜单和新角色
4. **安全性**: 前后端双重验证,确保权限安全

## 注意事项

1. **超级管理员**: `fcadmin` 角色拥有所有权限,不受限制
2. **菜单编码**: 必须与前端路由的 `meta.menuCode` 对应
3. **权限继承**: 选中父菜单会自动选中所有子菜单
4. **缓存更新**: 修改权限后,用户需要重新登录才能生效

## 未来扩展

1. **按钮级权限**: 在菜单基础上增加按钮权限控制
2. **数据权限**: 控制用户可以访问的数据范围
3. **权限审计**: 记录权限变更历史
4. **权限模板**: 预设常用的权限组合
