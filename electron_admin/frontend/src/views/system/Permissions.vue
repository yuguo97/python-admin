<template>
  <div class="app-container">
    <el-card class="box-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">权限管理</span>
        </div>
      </template>

      <div class="permission-container">
        <!-- 左侧角色列表 -->
        <div class="role-list">
          <div class="list-header">
            <span>角色列表</span>
          </div>
          <el-scrollbar height="600px">
            <div
              v-for="role in roleList"
              :key="role.id"
              class="role-item"
              :class="{ active: selectedRole?.id === role.id }"
              @click="handleSelectRole(role)"
            >
              <el-icon><UserFilled /></el-icon>
              <span class="role-name">{{ role.name }}</span>
              <el-tag v-if="role.code === 'fcadmin'" type="danger" size="small">超管</el-tag>
            </div>
          </el-scrollbar>
        </div>

        <!-- 右侧菜单树 -->
        <div class="menu-tree">
          <div class="tree-header">
            <span>菜单权限</span>
            <el-button
              v-if="selectedRole && selectedRole.code !== 'fcadmin'"
              type="primary"
              size="small"
              :loading="saveLoading"
              @click="handleSave"
            >
              保存权限
            </el-button>
            <el-tag v-if="selectedRole && selectedRole.code === 'fcadmin'" type="warning" size="small">
              超级管理员拥有全部权限,不可修改
            </el-tag>
          </div>
          <div v-if="!selectedRole" class="empty-tip">
            <el-empty description="请先选择一个角色" />
          </div>
          <el-scrollbar v-else height="600px">
            <el-tree
              ref="treeRef"
              :data="menuTree"
              :props="treeProps"
              show-checkbox
              node-key="code"
              default-expand-all
              :default-checked-keys="checkedMenus"
              :disabled="selectedRole?.code === 'fcadmin'"
            >
              <template #default="{ node, data }">
                <span class="custom-tree-node">
                  <el-icon>
                    <component :is="data.icon" />
                  </el-icon>
                  <span>{{ node.label }}</span>
                  <el-tag size="small" type="info">{{ data.code }}</el-tag>
                </span>
              </template>
            </el-tree>
          </el-scrollbar>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled, HomeFilled, Setting, User, UserFilled as UserFilledIcon, Lock, Menu } from '@element-plus/icons-vue'
import { getRoleList } from '@/api/role'
import { getRoleMenus, updateRoleMenus } from '@/api/roleMenu'

const roleList = ref([])
const selectedRole = ref(null)
const treeRef = ref(null)
const saveLoading = ref(false)
const checkedMenus = ref([])

const treeProps = {
  children: 'children',
  label: 'title'
}

// 菜单树数据(带编码) - 使用冒号分隔的编码格式
const menuTree = [
  {
    code: 'dashboard',
    title: '首页',
    icon: 'HomeFilled',
    children: []
  },
  {
    code: 'system',
    title: '系统管理',
    icon: 'Setting',
    children: [
      {
        code: 'system:user',
        title: '用户管理',
        icon: 'User'
      },
      {
        code: 'system:role',
        title: '角色管理',
        icon: 'UserFilled'
      },
      {
        code: 'system:permission',
        title: '权限管理',
        icon: 'Lock'
      },
      {
        code: 'system:menu',
        title: '菜单管理',
        icon: 'Menu'
      },
      {
        code: 'system:service',
        title: '服务管理',
        icon: 'Monitor'
      }
    ]
  }
]

const fetchRoles = async () => {
  try {
    const res = await getRoleList()
    if (res.data) {
      roleList.value = res.data
      // 默认选择第一条数据
      if (res.data.length > 0 && !selectedRole.value) {
        handleSelectRole(res.data[0])
      }
    }
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  }
}

const handleSelectRole = async (role) => {
  selectedRole.value = role
  // 获取该角色的菜单权限
  try {
    const res = await getRoleMenus(role.id)
    if (res.data) {
      checkedMenus.value = res.data.menu_codes || []
      // 等待树渲染完成后设置选中
      setTimeout(() => {
        treeRef.value?.setCheckedKeys(checkedMenus.value)
      }, 100)
    }
  } catch (error) {
    console.error('获取角色菜单失败:', error)
    checkedMenus.value = []
  }
}

const handleSave = async () => {
  if (!selectedRole.value) {
    return
  }
  
  const checkedKeys = treeRef.value.getCheckedKeys()
  const halfCheckedKeys = treeRef.value.getHalfCheckedKeys()
  const allKeys = [...checkedKeys, ...halfCheckedKeys]
  
  saveLoading.value = true
  try {
    await updateRoleMenus(selectedRole.value.id, allKeys)
    ElMessage.success('权限保存成功')
  } catch (error) {
    ElMessage.error('权限保存失败')
  } finally {
    saveLoading.value = false
  }
}

onMounted(() => {
  fetchRoles()
})
</script>

<style lang="less" scoped>
.app-container {
  .box-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 16px;
        font-weight: 500;
      }
    }
  }
}

.permission-container {
  display: flex;
  gap: 20px;
  min-height: 600px;

  .role-list {
    width: 280px;
    border: 1px solid #EBEEF5;
    border-radius: 4px;
    overflow: hidden;

    .list-header {
      padding: 15px;
      background: #F5F7FA;
      font-weight: 500;
      border-bottom: 1px solid #EBEEF5;
    }

    .role-item {
      padding: 15px;
      cursor: pointer;
      border-bottom: 1px solid #EBEEF5;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.3s;

      &:hover {
        background: #F5F7FA;
      }

      &.active {
        background: #ECF5FF;
        border-left: 3px solid #409EFF;
      }

      .role-name {
        flex: 1;
      }
    }
  }

  .menu-tree {
    flex: 1;
    border: 1px solid #EBEEF5;
    border-radius: 4px;
    overflow: hidden;

    .tree-header {
      padding: 15px;
      background: #F5F7FA;
      font-weight: 500;
      border-bottom: 1px solid #EBEEF5;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .empty-tip {
      padding: 50px;
    }

    :deep(.el-tree) {
      padding: 15px;

      .custom-tree-node {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;

        .el-icon {
          font-size: 16px;
        }

        .el-tag {
          margin-left: auto;
        }
      }
    }
  }
}
</style>
