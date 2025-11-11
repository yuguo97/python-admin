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
        <el-table-column label="操作" width="260" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'running'"
              type="danger"
              size="small"
              :icon="VideoPause"
              link
              :loading="row.loading"
              :disabled="row.service_name === 'admin'"
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
              :disabled="row.service_name === 'admin'"
              @click="handleStart(row)"
            >
              启动
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              type="warning"
              size="small"
              :icon="RefreshRight"
              link
              :loading="row.loading"
              :disabled="row.service_name === 'admin'"
              @click="handleRestart(row)"
            >
              重启
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, VideoPlay, VideoPause, RefreshRight, View } from '@element-plus/icons-vue'
import { getServiceList, startService, stopService, restartService } from '@/api/service'

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
      // 优先使用后端返回的 code/status 字段判断(如果可用)
      const msg = error?.message || '未知错误'
      if (error?.code === 400 && error?.status === 'error' && typeof msg === 'string' && msg.includes('已在运行')) {
        ElMessage.info(`${row.name} 已在运行中`)
        try { await fetchData() } catch (e) {}
      } else {
        ElMessage.error(`启动失败: ${msg}`)
      }
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
  // 立即将行状态设为已停止以提高响应感知，随后再刷新列表以确认最终状态
  row.status = 'stopped'
  ElMessage.success(`${row.name} 已停止`)
  // 等待短暂时间让服务进程完成退出，再刷新列表同步最终状态
  await new Promise(resolve => setTimeout(resolve, 1000))
  await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      // 优先使用后端返回的 code/status 字段判断(如果可用)
      const msg = error?.message || '未知错误'
      if (error?.code === 400 && error?.status === 'error' && typeof msg === 'string' && msg.includes('未运行')) {
        ElMessage.info(`${row.name} 未运行，状态已更新`)
        row.status = 'stopped'
        try { await fetchData() } catch (e) {}
      } else if (error?.code === 500) {
        // 服务器无法确认停止（可能自动重启或端口被占用），提示用户检查日志
        ElMessage.error(`停止失败: 服务停止未能确认，请检查后台日志: ${msg}`)
      } else {
        ElMessage.error(`停止失败: ${msg}`)
      }
    }
  } finally {
    row.loading = false
  }
}

// 重启服务
const handleRestart = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要重启 ${row.name} 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    row.loading = true
    await restartService(row.service_name)
    ElMessage.success(`${row.name} 重启成功`)
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      const msg = error?.message || '未知错误'
      ElMessage.error(`重启失败: ${msg}`)
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
  // 定期轮询以保持服务状态同步（每 10 秒）
  intervalId = setInterval(fetchData, 10000)
})

let intervalId = null

onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId)
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
