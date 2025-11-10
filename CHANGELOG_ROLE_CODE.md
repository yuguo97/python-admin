# 角色管理优化 - 添加角色编码功能

## 更新时间
2025-11-10

## 更新内容

### 1. 数据库模型更新
**文件**: `admin_service/app/models.py`

- 为 `Role` 模型添加 `code` 字段
  - 类型: `String(50)`
  - 唯一索引
  - 用于角色的唯一标识和关联

```python
code = Column(String(50), unique=True, index=True, comment="角色编码")
```

- 更新 `to_dict()` 方法,包含 `code` 字段

### 2. API Schema更新
**文件**: `admin_service/app/schemas.py`

- `RoleBase`: 添加 `code: str` 必填字段
- `RoleCreate`: 继承 `RoleBase`,包含 `code`
- `RoleUpdate`: 添加 `code: Optional[str]` 可选字段
- `Role`: 响应模型包含 `code` 字段

### 3. 前端页面更新
**文件**: `electron_admin/frontend/src/views/Roles.vue`

#### 表格显示
- 添加"角色编码"列,显示在角色名称之后

#### 表单
- 新增"角色编码"输入框
- 添加验证规则:
  - 必填项
  - 只能包含小写字母和下划线
  - 正则: `/^[a-z_]+$/`

#### 数据处理
- 创建/编辑/重置时都包含 `code` 字段

### 4. 数据库迁移
**文件**: `scripts/add_role_code.py`

自动迁移脚本,功能:
- 检查 `code` 列是否存在
- 添加 `code` 列(VARCHAR(50), UNIQUE)
- 为现有角色自动生成编码(基于角色名称)
- 创建索引

**运行方式**:
```bash
python scripts/add_role_code.py
```

### 5. 初始化脚本更新
**文件**: `scripts/create_admin.py`

- 创建超级管理员角色时添加 `code = "super_admin"`
- 如果角色已存在但没有code,自动补充

## 使用说明

### 角色编码规范
1. **格式**: 小写字母 + 下划线
2. **示例**:
   - `super_admin` - 超级管理员
   - `admin` - 管理员
   - `user` - 普通用户
   - `guest` - 访客
   - `content_manager` - 内容管理员

### 创建角色示例
```json
{
  "name": "内容管理员",
  "code": "content_manager",
  "description": "负责内容的创建、编辑和发布"
}
```

### API使用
```bash
# 创建角色
POST /roles/
{
  "name": "编辑",
  "code": "editor",
  "description": "内容编辑权限"
}

# 更新角色
PUT /roles/{id}
{
  "name": "高级编辑",
  "code": "senior_editor",
  "description": "高级内容编辑权限"
}
```

## 数据关联

角色编码可用于:
1. **权限关联**: 通过 `role_id` 关联权限
2. **用户关联**: 通过 `user_roles` 关联表关联用户
3. **代码中引用**: 使用编码而不是ID,更稳定可靠

```python
# 通过编码查询角色
admin_role = db.query(Role).filter(Role.code == "admin").first()

# 检查用户是否有某个角色
has_admin = any(role.code == "admin" for role in user.roles)
```

## 注意事项

1. **唯一性**: 角色编码必须唯一,不能重复
2. **不可变性**: 建议角色编码创建后不要修改,避免影响关联数据
3. **命名规范**: 使用有意义的英文单词,便于理解和维护
4. **小写规范**: 统一使用小写字母,保持一致性

## 兼容性

- ✅ 已有数据自动迁移
- ✅ 向后兼容
- ✅ 前端自动更新
- ✅ API自动支持

## 测试建议

1. 创建新角色,验证编码唯一性
2. 编辑现有角色,确保编码可更新
3. 测试编码格式验证
4. 验证角色关联功能正常
