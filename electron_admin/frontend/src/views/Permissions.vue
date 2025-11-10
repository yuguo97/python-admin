<template>
  <div class="app-container">
    <el-card class="box-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">权限管理</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新增权限
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="权限名称" min-width="150" />
        <el-table-column prop="code" label="权限代码" min-width="150" />
        <el-table-column label="所属角色" min-width="120">
          <template #default="{ row }">
            <el-tag v-if="row.role_name" size="small">{{ row.role_name }}</el-tag>
            <span v-else style="color: #999">未分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
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
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限代码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入权限代码，如: user:create" />
        </el-form-item>
        <el-form-item label="所属角色" prop="role_id">
          <el-select
            v-model="formData.role_id"
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option
              v-for="role in roleList"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入权限描述"
          />
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
import { getPermissionList, createPermission, updatePermission, deletePermission } from '@/api/permission'
import { getRoleList } from '@/api/role'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const roleList = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增权限')
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)

const formData = reactive({
  name: '',
  code: '',
  description: '',
  role_id: null
})

const formRules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入权限代码', trigger: 'blur' }
  ],
  role_id: [
    { required: true, message: '请选择所属角色', trigger: 'change' }
  ]
}

const fetchRoles = async () => {
  try {
    const res = await getRoleList()
    if (res.data) {
      roleList.value = res.data
    }
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPermissionList()
    if (res.data) {
      // 添加角色名称
      tableData.value = res.data.map(item => {
        const role = roleList.value.find(r => r.id === item.role_id)
        return {
          ...item,
          role_name: role ? role.name : ''
        }
      })
    }
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增权限'
  fetchRoles()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑权限'
  fetchRoles()
  Object.assign(formData, {
    name: row.name,
    code: row.code,
    description: row.description,
    role_id: row.role_id
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除权限 "${row.name}" 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deletePermission(row.id)
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
          await updatePermission(editId.value, formData)
          ElMessage.success('更新成功')
        } else {
          await createPermission(formData)
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
    name: '',
    code: '',
    description: '',
    role_id: null
  })
}

onMounted(() => {
  fetchRoles().then(() => {
    fetchData()
  })
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
