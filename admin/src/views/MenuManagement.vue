<template>
  <div class="page-container">
    <div class="content-header">
      <h3>菜单管理</h3>
      <p class="subtitle">管理系统菜单配置</p>
    </div>

    <div class="content-card">
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-button type="primary" @click="showMenuDialog()">
          <el-icon><Plus /></el-icon>添加菜单
        </el-button>
      </div>

      <!-- 菜单表格 -->
      <el-table
        :data="menus"
        row-key="id"
        :tree-props="{ children: 'children' }"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="name" label="菜单名称" min-width="180">
          <template #default="{ row }">
            <span>
              <el-icon v-if="row.icon"><component :is="row.icon" /></el-icon>
              {{ row.name }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="path" label="路由路径" min-width="180" />
        <el-table-column prop="component" label="组件路径" min-width="180" />
        
        <el-table-column prop="sort" label="排序" width="100" align="center" />
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_show" label="显示" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_show ? 'success' : 'info'">
              {{ row.is_show ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link
              @click="showMenuDialog(row)"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 菜单表单对话框 -->
    <el-dialog
      :title="currentMenu ? '编辑菜单' : '添加菜单'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="上级菜单">
          <el-tree-select
            v-model="formData.parent_id"
            :data="menuOptions"
            :props="{ label: 'name', value: 'id' }"
            placeholder="请选择上级菜单"
            clearable
          />
        </el-form-item>

        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入菜单名称" />
        </el-form-item>

        <el-form-item label="路由路径" prop="path">
          <el-input v-model="formData.path" placeholder="请输入路由路径" />
        </el-form-item>

        <el-form-item label="组件路径" prop="component">
          <el-input v-model="formData.component" placeholder="请输入组件路径" />
        </el-form-item>

        <el-form-item label="图标" prop="icon">
          <el-input v-model="formData.icon" placeholder="请输入图标名称" />
        </el-form-item>

        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="formData.sort" :min="0" />
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="是否显示">
          <el-switch v-model="formData.is_show" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, ArrowDown, Plus, SwitchButton 
} from '@element-plus/icons-vue'
import { getMenus, createMenu, updateMenu, deleteMenu } from '../api/menu'

const store = useStore()
const router = useRouter()

// 数据
const loading = ref(false)
const submitting = ref(false)
const menus = ref([])
const dialogVisible = ref(false)
const currentMenu = ref(null)
const formRef = ref(null)

// 表单数据
const formData = ref({
  parent_id: 0,
  name: '',
  path: '',
  component: '',
  icon: '',
  sort: 0,
  status: 1,
  is_show: true
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  path: [{ required: true, message: '请输入路由路径', trigger: 'blur' }],
  component: [{ required: true, message: '请输入组件路径', trigger: 'blur' }]
}

// 获取菜单列表
const fetchMenus = async () => {
  try {
    loading.value = true
    const response = await getMenus()
    menus.value = response.data || []
  } catch (error) {
    console.error('Fetch menus error:', error)
    ElMessage.error('获取菜单列表失败')
  } finally {
    loading.value = false
  }
}

// 显示菜单对话框
const showMenuDialog = (menu = null) => {
  currentMenu.value = menu
  if (menu) {
    formData.value = { ...menu }
  } else {
    formData.value = {
      parent_id: 0,
      name: '',
      path: '',
      component: '',
      icon: '',
      sort: 0,
      status: 1,
      is_show: true
    }
  }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (currentMenu.value) {
          await updateMenu(currentMenu.value.id, formData.value)
          ElMessage.success('更新成功')
        } else {
          await createMenu(formData.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchMenus()
      } catch (error) {
        console.error('Submit error:', error)
        ElMessage.error('操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 删除菜单
const handleDelete = (menu) => {
  ElMessageBox.confirm(
    '确定要删除该菜单吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteMenu(menu.id)
      ElMessage.success('删除成功')
      fetchMenus()
    } catch (error) {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 退出登录
const handleCommand = (command) => {
  if (command === 'logout') {
    store.commit('clearToken')
    router.push('/login')
  }
}

// 计算菜单选项
const menuOptions = computed(() => {
  return [
    { id: 0, name: '顶级菜单' },
    ...menus.value
  ]
})

onMounted(() => {
  fetchMenus()
})
</script>

<style scoped>
.page-container {
  min-height: 100%;
  padding: 20px;
}

.content-header {
  margin-bottom: 24px;
}

.content-header h3 {
  color: #1e293b;
  font-size: 24px;
  margin: 0 0 8px;
}

.subtitle {
  color: #64748b;
  margin: 0;
}

.content-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  padding: 24px;
}

.toolbar {
  margin-bottom: 24px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 