<template>
  <div class="dashboard-container">
    <div class="content-header">
      <h3>系统首页</h3>
      <p class="subtitle">系统概览</p>
    </div>

    <div class="dashboard-content">
      <!-- 数据概览卡片 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <template #header>
              <div class="card-header">
                <span>用户总数</span>
                <el-icon class="icon"><User /></el-icon>
              </div>
            </template>
            <div class="card-value">{{ stats.userCount || 0 }}</div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <template #header>
              <div class="card-header">
                <span>小说总数</span>
                <el-icon class="icon"><Document /></el-icon>
              </div>
            </template>
            <div class="card-value">{{ stats.novelCount || 0 }}</div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <template #header>
              <div class="card-header">
                <span>菜单总数</span>
                <el-icon class="icon"><Menu /></el-icon>
              </div>
            </template>
            <div class="card-value">{{ stats.menuCount || 0 }}</div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="data-card">
            <template #header>
              <div class="card-header">
                <span>系统状态</span>
                <el-icon class="icon"><Monitor /></el-icon>
              </div>
            </template>
            <div class="card-value">正常运行</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 系统信息 -->
      <el-card class="system-info" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>系统信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="系统名称">后台管理系统</el-descriptions-item>
          <el-descriptions-item label="当前版本">1.0.0</el-descriptions-item>
          <el-descriptions-item label="系统时间">{{ currentTime }}</el-descriptions-item>
          <el-descriptions-item label="运行环境">Vue 3 + Flask</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { User, Document, Menu, Monitor } from '@element-plus/icons-vue'

// 统计数据
const stats = ref({
  userCount: 0,
  novelCount: 0,
  menuCount: 0
})

// 当前时间
const currentTime = ref('')
let timer = null

// 更新时间
const updateTime = () => {
  currentTime.value = new Date().toLocaleString()
}

// 获取统计数据
const fetchStats = async () => {
  try {
    // 这里可以添加实际的API调用
    stats.value = {
      userCount: 10,
      novelCount: 100,
      menuCount: 5
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStats()
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.dashboard-container {
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

.data-card {
  transition: all 0.3s;
}

.data-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.icon {
  font-size: 20px;
  color: #409EFF;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #1e293b;
  text-align: center;
  padding: 20px 0;
}

.system-info :deep(.el-descriptions__label) {
  width: 120px;
}
</style> 