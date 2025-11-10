# 超级管理员保护机制

## 设计原则

超级管理员(fcadmin)是系统的最高权限角色,具有特殊保护机制。

## 保护措施

### 1. 唯一性保护
- ✅ 系统中只能有一个超级管理员角色
- ✅ 角色编码固定为 `fcadmin`
- ✅ 禁止创建新的超级管理员角色

### 2. 不可删除
- ✅ 禁止删除超级管理员角色
- ✅ 前端不显示删除按钮
- ✅ 后端API拦截删除请求

### 3. 编码不可修改
- ✅ 禁止修改超级管理员的角色编码
- ✅ 前端编辑时编码字段禁用
- ✅ 后端API验证编码修改

### 4. 权限不可修改
- ✅ 超级管理员默认拥有所有菜单权限
- ✅ 禁止修改超级管理员的菜单权限
- ✅ 权限管理页面显示提示信息
- ✅ 菜单树禁用编辑

## 后端API保护

### 创建角色
```python
@app.post("/roles/")
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    # 禁止创建超级管理员角色
    if role.code == "fcadmin":
        return error_response("不能创建超级管理员角色", status_code=400)
```

### 更新角色
```python
@app.put("/roles/{role_id}")
async def update_role(role_id: int, role: schemas.RoleUpdate, db: Session = Depends(get_db)):
    # 禁止修改超级管理员角色的编码
    if db_role.code == "fcadmin":
        if "code" in update_data and update_data["code"] != "fcadmin":
            return error_response("不能修改超级管理员角色编码", status_code=400)
```

### 删除角色
```python
@app.delete("/roles/{role_id}")
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    # 禁止删除超级管理员角色
    if db_role.code == "fcadmin":
        return error_response("不能删除超级管理员角色", status_code=400)
```

### 获取角色菜单
```python
@app.get("/roles/{role_id}/menus")
async def get_role_menus(role_id: int, db: Session = Depends(get_db)):
    # 超级管理员拥有所有菜单权限
    if role and role.code == "fcadmin":
        all_menu_codes = ["dashboard", "system", "system:user", "system:role", "system:permission", "system:menu"]
        return success_response({"menu_codes": all_menu_codes, "is_super_admin": True})
```

### 更新角色菜单
```python
@app.post("/roles/{role_id}/menus")
async def update_role_menus(role_id: int, menu_data: dict, db: Session = Depends(get_db)):
    # 禁止修改超级管理员权限
    if role and role.code == "fcadmin":
        return error_response("超级管理员权限不可修改", status_code=400)
```

## 前端UI保护

### 角色管理页面
```vue
<!-- 超级管理员不显示编辑删除按钮 -->
<el-button v-if="row.code !== 'fcadmin'" type="primary">编辑</el-button>
<el-button v-if="row.code !== 'fcadmin'" type="danger">删除</el-button>
<el-tag v-if="row.code === 'fcadmin'" type="info">系统角色</el-tag>

<!-- 编辑时禁止修改编码 -->
<el-input 
  v-model="formData.code" 
  :disabled="isEdit && formData.code === 'fcadmin'"
/>
```

### 权限管理页面
```vue
<!-- 超级管理员不显示保存按钮 -->
<el-button v-if="selectedRole && selectedRole.code !== 'fcadmin'">
  保存权限
</el-button>

<!-- 显示提示信息 -->
<el-tag v-if="selectedRole && selectedRole.code === 'fcadmin'" type="warning">
  超级管理员拥有全部权限,不可修改
</el-tag>

<!-- 菜单树禁用编辑 -->
<el-tree :disabled="selectedRole?.code === 'fcadmin'" />
```

## 用户管理优化

### 移除"管理员"字段
- ✅ 用户表不再需要 `is_admin` 字段
- ✅ 通过角色来控制权限,更加灵活
- ✅ 前端移除"管理员"列和表单项

### 权限判断逻辑
```javascript
// 旧方式: 通过 is_admin 字段判断
if (user.is_admin) {
  // 管理员权限
}

// 新方式: 通过角色判断
if (user.roles.some(role => role.code === 'fcadmin')) {
  // 超级管理员权限
}
```

## 默认权限

超级管理员默认拥有的菜单权限:
- `dashboard` - 首页
- `system` - 系统管理
- `system:user` - 用户管理
- `system:role` - 角色管理
- `system:permission` - 权限管理
- `system:menu` - 菜单管理

## 安全建议

1. **定期审计**: 定期检查超级管理员账号的使用情况
2. **最小权限**: 日常操作使用普通管理员账号,只在必要时使用超级管理员
3. **密码强度**: 超级管理员账号必须使用强密码
4. **操作日志**: 记录超级管理员的所有操作
5. **双因素认证**: 建议为超级管理员启用双因素认证

## 注意事项

1. 超级管理员角色在系统初始化时创建,不能通过界面创建
2. 如需修改超级管理员的名称或描述,可以编辑,但编码不能改
3. 超级管理员的菜单权限由系统自动维护,不存储在数据库中
4. 删除超级管理员角色会导致系统无法正常管理,因此被禁止
