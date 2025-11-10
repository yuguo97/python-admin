<template>
  <div class="app-container">
    <el-card class="box-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">角色管理</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新增角色
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
        <el-table-column prop="name" label="角色名称" min-width="150" />
        <el-table-column prop="code" label="角色编码" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.code !== 'fcadmin'"
              type="primary"
              size="small"
              :icon="Edit"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.code !== 'fcadmin'"
              type="danger"
              size="small"
              :icon="Delete"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
            <el-tag v-if="row.code === 'fcadmin'" type="info" size="small">系统角色</el-tag>
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
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input 
            v-model="formData.code" 
            placeholder="请输入角色编码，如: admin, user"
            :disabled="isEdit && formData.code === 'fcadmin'"
          />
          <div v-if="isEdit && formData.code === 'fcadmin'" style="color: #909399; font-size: 12px; margin-top: 4px;">
            超级管理员编码不可修改
          </div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入角色描述"
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
import { getRoleList, createRole, updateRole, deleteRole } from '@/api/role'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)

const formData = reactive({
  name: '',
  code: '',
  description: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[a-z_]+$/, message: '角色编码只能包含小写字母和下划线', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getRoleList()
    if (res.data) {
      tableData.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增角色'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑角色'
  Object.assign(formData, {
    name: row.name,
    code: row.code,
    description: row.description
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除角色 "${row.name}" 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteRole(row.id)
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
          await updateRole(editId.value, formData)
          ElMessage.success('更新成功')
        } else {
          await createRole(formData)
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
    description: ''
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
