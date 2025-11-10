<template>
  <div class="app-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>CPU 信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="CPU 使用率">
              <el-progress :percentage="cpuUsage" :color="getColor(cpuUsage)" />
            </el-descriptions-item>
            <el-descriptions-item label="核心数">{{ cpuCount }} 核</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>内存信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="内存使用率">
              <el-progress :percentage="memoryUsage" :color="getColor(memoryUsage)" />
            </el-descriptions-item>
            <el-descriptions-item label="总内存">{{ totalMemory }} GB</el-descriptions-item>
            <el-descriptions-item label="已用内存">{{ usedMemory }} GB</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>磁盘信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="磁盘使用率">
              <el-progress :percentage="diskUsage" :color="getColor(diskUsage)" />
            </el-descriptions-item>
            <el-descriptions-item label="总容量">{{ totalDisk }} GB</el-descriptions-item>
            <el-descriptions-item label="已用容量">{{ usedDisk }} GB</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>系统信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="操作系统">{{ osName }}</el-descriptions-item>
            <el-descriptions-item label="系统版本">{{ osVersion }}</el-descriptions-item>
            <el-descriptions-item label="运行时间">{{ uptime }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const cpuUsage = ref(45)
const cpuCount = ref(8)
const memoryUsage = ref(62)
const totalMemory = ref(16)
const usedMemory = ref(9.9)
const diskUsage = ref(58)
const totalDisk = ref(512)
const usedDisk = ref(297)
const osName = ref('Windows 11')
const osVersion = ref('23H2')
const uptime = ref('3天 5小时 23分钟')

let timer = null

const getColor = (percentage) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const fetchSystemInfo = async () => {
  // TODO: 调用实际的API获取系统信息
  // 模拟数据变化
  cpuUsage.value = Math.floor(Math.random() * 30) + 40
  memoryUsage.value = Math.floor(Math.random() * 20) + 55
}

onMounted(() => {
  fetchSystemInfo()
  // 每5秒刷新一次
  timer = setInterval(fetchSystemInfo, 5000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style lang="less" scoped>
.app-container {
  padding: 20px;
}
</style>
