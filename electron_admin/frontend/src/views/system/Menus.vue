<template>
  <div class="app-container">
    <el-card class="box-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">菜单管理</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新增菜单
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        row-key="id"
        border
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
        <el-table-column prop="title" label="菜单名称" min-width="200" />
        <el-table-column prop="path" label="路径" min-width="150" />
        <el-table-column prop="icon" label="图标" width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.icon">
              <component :is="row.icon" />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column label="可见" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.visible ? 'success' : 'info'" size="small">
              {{ row.visible ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Edit"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="菜单名称" prop="title">
          <el-input v-model="formData.title" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单编码" prop="code">
          <el-input 
            v-model="formData.code" 
            placeholder="自动生成,如: system:user"
            disabled
          />
          <div style="color: #909399; font-size: 12px; margin-top: 4px;">
            菜单编码由路径自动生成,不可手动修改
          </div>
        </el-form-item>
        <el-form-item label="路由路径" prop="path">
          <el-input 
            v-model="formData.path" 
            placeholder="请输入路由路径，如: users"
            @input="handlePathChange"
          />
          <div style="color: #909399; font-size: 12px; margin-top: 4px;">
            子菜单路径不需要斜杠开头,如: users, roles
          </div>
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="formData.icon" placeholder="请输入图标名称，如: User" />
        </el-form-item>
        <el-form-item label="父级菜单" prop="parent_id">
          <el-tree-select
            v-model="formData.parent_id"
            :data="menuTreeData"
            :props="{ label: 'title', value: 'id' }"
            placeholder="请选择父级菜单（不选则为顶级菜单）"
            clearable
            check-strictly
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="formData.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="是否可见" prop="visible">
          <el-switch v-model="formData.visible" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getMenuTree, createMenu, updateMenu, deleteMenu } from '@/api/menu'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const menuTreeData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增菜单')
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)

const formData = reactive({
  title: '',
  code: '',
  path: '',
  icon: '',
  parent_id: null,
  sort_order: 1,
  visible: true
})

const formRules = {
  title: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入路径', trigger: 'blur' }
  ]
}

// 根据路径自动生成菜单编码
const handlePathChange = () => {
  if (!formData.path) {
    formData.code = ''
    return
  }
  
  // 移除开头的斜杠
  let path = formData.path.replace(/^\/+/, '')
  
  // 如果有父级菜单,生成带父级的编码
  if (formData.parent_id) {
    const parentMenu = findMenuById(tableData.value, formData.parent_id)
    if (parentMenu) {
      // 父级编码:子路径
      formData.code = `${parentMenu.code}:${path}`
    } else {
      formData.code = path
    }
  } else {
    // 一级菜单直接使用路径
    formData.code = path
  }
}

// 递归查找菜单
const findMenuById = (menus, id) => {
  for (const menu of menus) {
    if (menu.id === id) {
      return menu
    }
    if (menu.children) {
      const found = findMenuById(menu.children, id)
      if (found) return found
    }
  }
  return null
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMenuTree()
    if (res.data) {
      tableData.value = res.data
      menuTreeData.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取菜单列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增菜单'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑菜单'
  Object.assign(formData, {
    title: row.title,
    code: row.code || '',
    path: row.path,
    icon: row.icon,
    parent_id: row.parent_id,
    sort_order: row.sort_order,
    visible: row.visible
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除菜单 "${row.title}" 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteMenu(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateMenu(editId.value, formData)
          ElMessage.success('更新成功')
        } else {
          await createMenu(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    title: '',
    code: '',
    path: '',
    icon: '',
    sort_order: 1,
    visible: true,
    parent_id: null
  })
}

onMounted(() => {
  fetchData()
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
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
}
</style>
