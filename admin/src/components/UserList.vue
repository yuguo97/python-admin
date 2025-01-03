<template>
  <div class="user-list">
    <el-table 
      :data="users" 
      style="width: 100%"
      border
      stripe
      v-loading="loading"
      class="custom-table"
    >
      <!-- 用户信息列 -->
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

      <!-- 状态列 -->
      <el-table-column prop="status" label="状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag 
            :type="row.status === 1 ? 'success' : 'danger'"
            :effect="row.status === 1 ? 'light' : 'dark'"
            class="status-tag"
          >
            <el-icon>
              <component :is="row.status === 1 ? 'CircleCheckFilled' : 'CircleCloseFilled'" />
            </el-icon>
            {{ row.status === 1 ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 创建时间列 -->
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          <div class="time-info">
            <el-icon><Calendar /></el-icon>
            {{ formatDate(row.created_at) }}
          </div>
        </template>
      </el-table-column>

      <!-- 最后登录列 -->
      <el-table-column label="最后登录" width="180">
        <template #default="{ row }">
          <div class="time-info" :class="{ 'text-secondary': !row.last_login }">
            <el-icon><Timer /></el-icon>
            {{ row.last_login ? formatDate(row.last_login) : '从未登录' }}
          </div>
        </template>
      </el-table-column>

      <!-- 备注列 -->
      <el-table-column prop="remark" label="备注" min-width="150">
        <template #default="{ row }">
          <el-tooltip 
            :content="row.remark || '暂无备注'"
            placement="top"
            :show-after="500"
          >
            <span class="remark">{{ row.remark || '暂无备注' }}</span>
          </el-tooltip>
        </template>
      </el-table-column>

      <!-- 操作列 -->
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button 
              type="primary" 
              link
              @click="$emit('edit', row)"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-popconfirm
              title="确定要删除此用户吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="$emit('delete', row.id)"
            >
              <template #reference>
                <el-button 
                  type="danger" 
                  link
                >
                  <el-icon><Delete /></el-icon>删除
                </el-button>
              </template>
            </el-popconfirm>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { 
  UserFilled, Message, Phone, Calendar, 
  Timer, Edit, Delete, CircleCheckFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'

defineProps({
  users: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['edit', 'delete'])

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.user-list {
  position: relative;
}

.custom-table {
  --el-table-border-color: #e5e7eb;
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f0f9ff;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header) {
  th {
    background-color: var(--el-table-header-bg-color) !important;
    font-weight: 600;
    color: #1e293b;
  }
}

:deep(.el-table__row) {
  td {
    padding: 12px 0;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  background: linear-gradient(120deg, #3b82f6 0%, #2563eb 100%);
  border: 2px solid white;
  box-shadow: 0 2px 4px rgb(0 0 0 / 0.1);
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 500;
  color: #1e293b;
}

.contact-info {
  display: flex;
  gap: 16px;
  color: #64748b;
  font-size: 13px;
}

.email,
.phone {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  
  :deep(.el-icon) {
    margin-right: 2px;
  }
}

.time-info {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  font-size: 13px;
}

.text-secondary {
  color: #94a3b8;
}

.remark {
  color: #64748b;
  font-size: 13px;
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

:deep(.el-button--link) {
  height: auto;
  padding: 0;
  font-size: 14px;
  
  .el-icon {
    margin-right: 4px;
  }
}

@media (max-width: 768px) {
  .contact-info {
    flex-direction: column;
    gap: 4px;
  }

  .action-buttons {
    gap: 12px;
  }
}
</style> 