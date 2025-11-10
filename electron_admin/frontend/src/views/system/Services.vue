<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>服务管理</span>
          <el-button type="primary" :icon="Refresh" @click="fetchData">刷新</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" border style="width: 100%">
        <el-table-column prop="name" label="服务名称" width="200" />
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'running' ? 'success' : 'danger'" size="small">
              {{ row.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="port" label="端口" width="100" align="center" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'running'"
              type="danger"
              size="small"
              :icon="VideoPause"
              link
              :loading="row.loading"
              @click="handleStop(row)"
            >
              停止
            </el-button>
            <el-button
              v-else
              type="success"
              size="small"
              :icon="VideoPlay"
              link
              :loading="row.loading"
              @click="handleStart(row)"
            >
              启动
            </el-button>
            <el-button
              type="primary"
              size="small"
              :icon="View"
              link
              @click="handleView(row)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, VideoPlay, VideoPause, View } from '@element-plus/icons-vue'
import { getServiceList, startService, stopService } from '@/api/service'

const loading = ref(false)
const tableData = ref([])

// 获取服务列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getServiceList()
    if (res.data) {
      tableData.value = res.data.map(item => ({
        ...item,
        loading: false
      }))
    }
  } catch (error) {
    ElMessage.error('获取服务列表失败')
  } finally {
    loading.value = false
  }
}

// 启动服务
const handleStart = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要启动 ${row.name} 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    row.loading = true
    await startService(row.service_name)
    ElMessage.success(`${row.name} 启动成功`)
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`启动失败: ${error.message || '未知错误'}`)
    }
  } finally {
    row.loading = false
  }
}

// 停止服务
const handleStop = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止 ${row.name} 吗？停止后可能影响系统功能。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    row.loading = true
    await stopService(row.service_name)
    ElMessage.success(`${row.name} 已停止`)
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`停止失败: ${error.message || '未知错误'}`)
    }
  } finally {
    row.loading = false
  }
}

// 查看服务
const handleView = (row) => {
  window.open(`http://localhost:${row.port}/docs`, '_blank')
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="less" scoped>
.app-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
