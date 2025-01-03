<template>
  <div class="page-container">
    <div class="content-header">
      <h3>用户管理</h3>
      <p class="subtitle">管理系统用户信息</p>
    </div>

    <div class="content-card">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="left">
          <el-button type="primary" @click="showUserDialog()">
            <el-icon><Plus /></el-icon>添加用户
          </el-button>
        </div>
        
        <!-- 添加右侧快捷菜单 -->
        <div class="right">
          <el-button type="primary" plain @click="router.push('/system/menus')">
            <el-icon><Menu /></el-icon>菜单管理
          </el-button>
        </div>
      </div>

      <!-- 用户列表 -->
      <el-table 
        :data="users" 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column label="用户信息" min-width="280">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar 
                :size="40" 
                :icon="UserFilled"
                class="user-avatar"
              />
              <div class="info-content">
                <div class="username">{{ row.username }}</div>
                <div class="contact-info">
                  <el-tooltip 
                    :content="row.email"
                    placement="top"
                    :show-after="500"
                  >
                    <span class="email">
                      <el-icon><Message /></el-icon>
                      {{ row.email }}
                    </span>
                  </el-tooltip>
                  <span class="phone" v-if="row.phone">
                    <el-icon><Phone /></el-icon>
                    {{ row.phone }}
                  </span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="备注" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="remark">{{ row.remark || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            <span class="text-secondary">{{ row.created_at }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                type="primary" 
                link
                @click="handleEdit(row)"
              >
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button 
                type="danger" 
                link
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 用户编辑弹窗 -->
    <user-modal
      v-model:visible="modalVisible"
      :user="currentUser"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Plus, Menu } from '@element-plus/icons-vue'
import { getUsers, deleteUser } from '../api/user'
import UserModal from '../components/UserModal.vue'

const router = useRouter()
const loading = ref(false)
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const modalVisible = ref(false)
const currentUser = ref(null)
const searchQuery = ref('')

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const { data } = await getUsers({
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchQuery.value || ''
    })
    
    users.value = data.items
    total.value = data.total
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchUsers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchUsers()
}

// 添加用户
const showUserDialog = () => {
  currentUser.value = null
  modalVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  currentUser.value = row
  modalVisible.value = true
}

// 删除用户
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除该用户吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      fetchUsers()
    } catch (error) {
      console.error('Delete user error:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 操作成功回调
const handleSuccess = () => {
  modalVisible.value = false
  fetchUsers()
}

onMounted(() => {
  fetchUsers()
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar .left,
.toolbar .right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.el-button :deep(.el-icon) {
  margin-right: 4px;
  font-size: 16px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .content-card {
    padding: 16px;
  }

  .toolbar {
    flex-direction: column;
    gap: 16px;
  }

  .pagination-container {
    justify-content: center;
  }
}
</style> 