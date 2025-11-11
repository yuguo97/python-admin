<template>
  <div class="app-container">
    <div class="page-controls" style="margin-bottom:12px; display:flex; align-items:center; gap:12px;">
      <el-button type="primary" size="small" :loading="loading" :disabled="loading" @click="fetchSystemInfo">刷新</el-button>
      <el-switch v-model="autoRefresh" active-text="自动刷新" inactive-text="自动刷新" />
      <el-select v-model="refreshInterval" size="small" style="width:120px">
        <el-option :label="'5s'" :value="5000" />
        <el-option :label="'10s'" :value="10000" />
        <el-option :label="'30s'" :value="30000" />
      </el-select>
      <span style="color:#909399; font-size:12px">(间隔 {{ refreshInterval/1000 }}s)</span>
    </div>
    <div style="margin-bottom:12px">
      <!-- 错误改为全局 ElMessage 弹窗，保留占位用于兼容 older UI */ -->
      <div v-if="false"></div>
    </div>

    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="概览" name="overview">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>CPU 信息</span>
          </template>
          <div class="chart-wrapper">
            <div ref="cpuChartRef" class="chart" />
          </div>
          <el-descriptions :column="1" border style="margin-top:12px">
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
          <div class="chart-wrapper">
            <div ref="memChartRef" class="chart" />
          </div>
          <el-descriptions :column="1" border style="margin-top:12px">
            <el-descriptions-item label="内存使用率">
              <el-progress :percentage="memoryUsage" :color="getColor(memoryUsage)" />
            </el-descriptions-item>
            <el-descriptions-item label="总内存">{{ totalMemory }} GB</el-descriptions-item>
            <el-descriptions-item label="已用内存">{{ usedMemory }} GB</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

      </el-tab-pane>

      <el-tab-pane label="进程" name="processes">
        <el-row style="margin-bottom:12px; display:flex; align-items:center; gap:12px">
          <el-input v-model="processSearch" placeholder="按进程名搜索" size="small" style="width:240px" clearable @clear="onProcessSearch" @keyup.enter.native="onProcessSearch" />
          <el-button type="primary" size="small" @click="onProcessSearch">搜索</el-button>
          <el-button type="link" size="small" @click="refreshProcesses">刷新</el-button>
          <el-select v-model="processPageSize" size="small" style="width:120px">
            <el-option :label="'10'" :value="10" />
            <el-option :label="'20'" :value="20" />
            <el-option :label="'50'" :value="50" />
          </el-select>
        </el-row>

        <el-table :data="displayedProcesses" size="small" style="width:100%" :stripe="true">
          <el-table-column prop="pid" label="PID" width="100" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="cpu_percent" label="CPU%" width="120" />
          <el-table-column prop="memory_percent" label="内存%" width="120" />
        </el-table>

        <div style="margin-top:12px; text-align:right">
          <el-pagination
            background
            layout="prev, pager, next, jumper, ->, total"
            v-model:current-page="processPage"
            v-model:page-size="processPageSize"
            :total="processTotal"
            @current-change="onProcessPageChange"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="服务" name="services">
        <el-row style="margin-bottom:12px; display:flex; align-items:center; gap:12px">
          <el-button type="primary" size="small" @click="refreshServices">刷新服务状态</el-button>
        </el-row>
        <el-table :data="servicesList" size="small" style="width:100%" :stripe="true">
          <el-table-column prop="service" label="服务" width="200" />
          <el-table-column prop="port" label="端口" width="120" />
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column prop="timestamp" label="时间戳" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

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

          <el-collapse v-if="partitions.length" style="margin-top:12px">
            <el-collapse-item v-for="(p, idx) in partitions" :key="p.mountpoint || idx" :title="p.mountpoint + ' (' + p.device + ')'">
              <div style="display:flex; align-items:center; gap:12px">
                <div style="flex:1">
                  <el-progress :percentage="p.percentage" :color="getColor(p.percentage)" />
                  <div style="margin-top:8px; color:#606266; font-size:13px">总: {{ bytesToGB(p.total) }} GB · 已用: {{ bytesToGB(p.used) }} GB · 可用: {{ bytesToGB(p.free) }} GB</div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
          <div v-else style="margin-top:12px; color:#909399">无分区信息</div>
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

    <!-- 网络与硬件行 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>网络信息 (连接数: {{ networkConnections }})</span>
          </template>
          <div v-if="Object.keys(networkInterfaces).length">
            <el-table :data="Object.keys(networkInterfaces).map(k => ({ name: k, ...networkInterfaces[k] }))" style="width:100%" size="small" :stripe="true">
              <el-table-column prop="name" label="接口" width="140" />
              <el-table-column prop="bytes_sent" label="发送 (GB)" :formatter="formatBytes" />
              <el-table-column prop="bytes_recv" label="接收 (GB)" :formatter="formatBytes" />
              <el-table-column prop="packets_sent" label="包(发)" />
              <el-table-column prop="packets_recv" label="包(收)" />
              <el-table-column prop="errors_in" label="输入错误" />
              <el-table-column prop="errors_out" label="输出错误" />
            </el-table>
          </div>
          <div v-else style="color:#909399">无网络接口统计信息</div>

          <div style="margin-top:12px">
            <template>
              <div style="font-weight:600; margin-bottom:8px">网卡 (名称 / IP / MAC / 速率)</div>
              <el-table :data="networkCards" style="width:100%" size="small" :stripe="true">
                <el-table-column prop="name" label="名称" width="140" />
                <el-table-column prop="ip" label="IP" />
                <el-table-column prop="mac" label="MAC" />
                <el-table-column prop="speed" label="速率 (Mbps)" width="120" />
              </el-table>
            </template>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>硬件与标识</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="主板序列号">{{ motherboardSerial || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="系统 UUID">{{ systemUUID || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="CPU 详情">
              <div>型号: {{ cpuDetail.model || '-' }}</div>
              <div>物理核: {{ cpuDetail.physical_cores ?? '-' }} · 逻辑核: {{ cpuDetail.total_cores ?? '-' }}</div>
              <div>频率: {{ cpuDetail.current_frequency ?? '-' }} MHz / Max: {{ cpuDetail.max_frequency ?? '-' }} MHz</div>
            </el-descriptions-item>
            <el-descriptions-item label="内存详情">
              <div>总量: {{ memoryDetail.total ? bytesToGB(memoryDetail.total) + ' GB' : '-' }}</div>
              <div>插槽数: {{ memoryDetail.slots ? memoryDetail.slots.length : '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 已安装软件 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>已安装软件 (显示前 200 条)</span>
          </template>
          <div v-if="installedSoftware && installedSoftware.length">
            <el-table :data="displayedInstalled" style="width:100%" size="small">
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="version" label="版本" width="140" />
              <el-table-column prop="publisher" label="发布者" width="200" />
              <el-table-column prop="date" label="安装日期" width="160" />
            </el-table>

            <div style="margin-top:12px; text-align:right">
              <el-pagination
                background
                layout="prev, pager, next, sizes, jumper, ->, total"
                v-model:current-page="installedPage"
                v-model:page-size="installedPageSize"
                :page-sizes="[10,20,50,100]"
                :total="installedTotal"
              />
            </div>
          </div>
          <div v-else style="color:#909399">无已安装软件信息或权限不足</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { getSystemInfo, getProcesses, getServiceList } from '@/api/system'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const cpuUsage = ref(0)
const cpuCount = ref(0)
const memoryUsage = ref(0)
const totalMemory = ref(0)
const usedMemory = ref(0)
const diskUsage = ref(0)
const totalDisk = ref(0)
const usedDisk = ref(0)
const osName = ref('')
const osVersion = ref('')
const uptime = ref('')

const timerRef = ref(null)
const refreshInterval = ref(5000)
const autoRefresh = ref(true)
const loading = ref(false)
const errorMsg = ref('')

const partitions = ref([])

const installedSoftware = ref([])
const networkCards = ref([])
const motherboardSerial = ref('')
const cpuDetail = ref({})
const memoryDetail = ref({})
const systemUUID = ref('')
const networkInterfaces = ref({})
const networkConnections = ref(0)

// Tabs
const activeTab = ref('overview')

// Installed software pagination
const installedPage = ref(1)
const installedPageSize = ref(20)
const installedTotal = computed(() => installedSoftware.value.length)
const displayedInstalled = computed(() => {
  const start = (installedPage.value - 1) * installedPageSize.value
  return installedSoftware.value.slice(start, start + installedPageSize.value)
})

// Processes
const processList = ref([])
const processPage = ref(1)
const processPageSize = ref(20)
const processSearch = ref('')

const filteredProcesses = computed(() => {
  return processSearch.value
    ? processList.value.filter(p => p.name && p.name.toLowerCase().includes(processSearch.value.toLowerCase()))
    : processList.value
})

const processTotal = computed(() => filteredProcesses.value.length)

const displayedProcesses = computed(() => {
  const start = (processPage.value - 1) * processPageSize.value
  return filteredProcesses.value.slice(start, start + processPageSize.value)
})

// Services
const servicesList = ref([])

// chart refs
const cpuChartRef = ref(null)
const memChartRef = ref(null)
let cpuChart = null
let memChart = null
const cpuTrend = ref([])
const memTrend = ref([])
const maxPoints = 20

const getColor = (percentage) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const bytesToGB = (bytes) => {
  return +(bytes / (1024 ** 3)).toFixed(2)
}

const formatBytes = (_row, _col, cell) => {
  if (cell == null) return '-'
  try { return bytesToGB(cell) }
  catch (e) { return '-'}
}

const formatUptime = (bootIso) => {
  try {
    const boot = new Date(bootIso)
    const diff = Date.now() - boot.getTime()
    const secs = Math.floor(diff / 1000)
    const days = Math.floor(secs / 86400)
    const hours = Math.floor((secs % 86400) / 3600)
    const minutes = Math.floor((secs % 3600) / 60)
    let s = ''
    if (days) s += `${days}天 `
    if (hours) s += `${hours}小时 `
    if (minutes) s += `${minutes}分钟`
    return s || '刚刚启动'
  } catch (e) {
    return ''
  }
}

const fetchSystemInfo = async () => {
  loading.value = true
  try {
    const res = await getSystemInfo()
    if (res?.data) {
      const info = res.data
      // CPU
      cpuUsage.value = info.cpu?.total_cpu_usage ?? 0
      cpuCount.value = info.cpu?.physical_cores ?? info.cpu?.total_cores ?? 0

      // Memory
      memoryUsage.value = info.memory?.percentage ?? 0
      totalMemory.value = info.memory?.total ? bytesToGB(info.memory.total) : 0
      usedMemory.value = info.memory?.used ? bytesToGB(info.memory.used) : 0

      // Disk - aggregate partitions
      const parts = info.disk?.partitions || []
      let total = 0
      let used = 0
      parts.forEach(p => {
        total += p.total || 0
        used += p.used || 0
      })
      totalDisk.value = total ? bytesToGB(total) : 0
      usedDisk.value = used ? bytesToGB(used) : 0
      diskUsage.value = total > 0 ? Math.round((used / total) * 100) : 0
  // set partitions for UI
  partitions.value = parts

  // System
  osName.value = `${info.system || ''} ${info.machine || ''}`.trim()
  osVersion.value = `${info.release || ''} ${info.version || ''}`.trim()
  uptime.value = formatUptime(info.boot_time)

  // extras from latest采集
  installedSoftware.value = info.installed_software || []
  networkCards.value = info.network_cards || []
  motherboardSerial.value = info.motherboard_serial || ''
  cpuDetail.value = info.cpu_detail || {}
  memoryDetail.value = info.memory_detail || {}
  systemUUID.value = info.system_uuid || ''
  networkInterfaces.value = info.network?.interfaces || {}
  networkConnections.value = info.network?.connections || 0
    } else {
      const msg = '无效的接口返回'
      console.warn('getSystemInfo 返回空或无 data 字段', res)
      ElMessage.error(msg)
    }
  } catch (err) {
    const msg = err?.message || String(err)
    console.error('获取系统信息失败:', err)
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

// Processes & Services fetch
const fetchProcesses = async (limit = 500) => {
  try {
    const res = await getProcesses(limit)
    if (res?.data) {
      const info = res.data
      processList.value = info.processes || []
      // processTotal will be computed from filtered list
    } else {
      ElMessage.error('获取进程信息失败：无效响应')
    }
  } catch (e) {
    console.error('获取进程失败', e)
    ElMessage.error(e?.message || '获取进程列表失败')
  }
}

const refreshProcesses = () => {
  // fetch a reasonably large amount and page on client side
  fetchProcesses(500)
}

const onProcessSearch = () => {
  processPage.value = 1
  // keep client-side filtering; ensure UI shows first page
}

// reset process page when page size changes
watch(processPageSize, (n) => {
  processPage.value = 1
})

// reset installed page when page size changes
watch(installedPageSize, (n) => {
  installedPage.value = 1
})

const onProcessPageChange = (page) => {
  processPage.value = page
}

const fetchServices = async () => {
  try {
    const res = await getServiceList()
    if (res?.data) {
      const info = res.data
      // info is an object with keys e.g. admin_service
      const rows = Object.keys(info).map(key => ({ service: key, ...info[key] }))
      servicesList.value = rows
    } else {
      ElMessage.error('获取服务状态失败：无效响应')
    }
  } catch (e) {
    console.error('获取服务失败', e)
    ElMessage.error(e?.message || '获取服务状态失败')
  }
}

const refreshServices = () => {
  fetchServices()
}

const initCharts = () => {
  // Initialize charts only when container has measurable size
  try {
    if (cpuChartRef.value && !cpuChart) {
      const rect = cpuChartRef.value.getBoundingClientRect()
      if (rect.width > 0 && rect.height > 0) {
        cpuChart = echarts.init(cpuChartRef.value)
        cpuChart.setOption({
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: [], boundaryGap: false },
          yAxis: { type: 'value', min: 0, max: 100 },
          series: [{ name: 'CPU', type: 'line', data: [], smooth: true, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(64,158,255,0.4)' }, { offset: 1, color: 'rgba(64,158,255,0.05)' }] } }, lineStyle: { width: 2 } }]
        })
      }
    }

    if (memChartRef.value && !memChart) {
      const rect2 = memChartRef.value.getBoundingClientRect()
      if (rect2.width > 0 && rect2.height > 0) {
        memChart = echarts.init(memChartRef.value)
        memChart.setOption({
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: [], boundaryGap: false },
          yAxis: { type: 'value', min: 0, max: 100 },
          series: [{ name: 'Memory', type: 'line', data: [], smooth: true, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(230,162,60,0.35)' }, { offset: 1, color: 'rgba(230,162,60,0.04)' }] } }, lineStyle: { width: 2 } }]
        })
      }
    }
  } catch (e) {
    console.warn('initCharts error', e)
  }
}

// Retry init until containers have non-zero size (used when inside hidden tabs)
const chartInitAttempts = ref(0)
const tryInitCharts = async () => {
  chartInitAttempts.value = 0
  const max = 8
  const tick = async () => {
    chartInitAttempts.value += 1
    await nextTick()
    initCharts()
    if ((!cpuChart || !memChart) && chartInitAttempts.value < max) {
      setTimeout(tick, 200)
    } else {
      // ensure charts are resized after init
      setTimeout(() => { cpuChart && cpuChart.resize(); memChart && memChart.resize() }, 100)
    }
  }
  tick()
}

const updateCharts = () => {
  const now = new Date().toLocaleTimeString()
  cpuTrend.value.push({ t: now, v: cpuUsage.value })
  memTrend.value.push({ t: now, v: memoryUsage.value })
  if (cpuTrend.value.length > maxPoints) cpuTrend.value.shift()
  if (memTrend.value.length > maxPoints) memTrend.value.shift()

  const x = cpuTrend.value.map(i => i.t)
  const cpuData = cpuTrend.value.map(i => i.v)
  const memData = memTrend.value.map(i => i.v)

  if (cpuChart) cpuChart.setOption({ xAxis: { data: x }, series: [{ data: cpuData }] })
  if (memChart) memChart.setOption({ xAxis: { data: x }, series: [{ data: memData }] })
  // resize to make sure responsive
  setTimeout(() => {
    cpuChart && cpuChart.resize()
    memChart && memChart.resize()
  }, 100)
}

// helper to setup and clear timer
const clearTimer = () => {
  if (timerRef.value) {
    clearInterval(timerRef.value)
    timerRef.value = null
  }
}

const setupTimer = (interval = refreshInterval.value) => {
  clearTimer()
  timerRef.value = setInterval(() => { fetchSystemInfo().then(updateCharts).catch(() => {}) }, interval)
}

watch(autoRefresh, (v) => {
  if (v) setupTimer()
  else clearTimer()
})

watch(refreshInterval, (n) => {
  if (autoRefresh.value) setupTimer(n)
})

watch(activeTab, (v) => {
  if (v === 'processes') {
    // fetch processes when user opens tab
    fetchProcesses(500)
  } else if (v === 'services') {
    fetchServices()
  }
  if (v === 'overview') {
    // initialize charts when returning to overview
    tryInitCharts()
    // refresh overview data
    fetchSystemInfo().then(() => { updateCharts() })
  }
})

onMounted(() => {
  // initialize charts only when overview tab is visible
  if (activeTab.value === 'overview') {
    tryInitCharts()
  }
  fetchSystemInfo().then(() => { updateCharts() })
  // 每 refreshInterval 刷新一次（由 setupTimer 管理）
  if (autoRefresh.value) setupTimer()

  // resize charts on window resize
  const onResize = () => {
    cpuChart && cpuChart.resize()
    memChart && memChart.resize()
  }

  const handleVisibility = () => {
    setTimeout(() => {
      cpuChart && cpuChart.resize()
      memChart && memChart.resize()
    }, 100)
  }

  // store handlers on refs so we can remove them later
  window.addEventListener('resize', onResize)
  document.addEventListener('visibilitychange', handleVisibility)

  // save handlers for cleanup
  window.__sys_on_resize = onResize
  window.__sys_on_visibility = handleVisibility
})

onUnmounted(() => {
  clearTimer()
  if (cpuChart) { cpuChart.dispose(); cpuChart = null }
  if (memChart) { memChart.dispose(); memChart = null }
  const onResize = window.__sys_on_resize
  const onVisibility = window.__sys_on_visibility
  if (onResize) window.removeEventListener('resize', onResize)
  if (onVisibility) document.removeEventListener('visibilitychange', onVisibility)
  try { delete window.__sys_on_resize } catch (e) {}
  try { delete window.__sys_on_visibility } catch (e) {}
})
</script>

<style lang="less" scoped>
.app-container {
  padding: 20px;
}

.chart {
  min-height: 180px;
}
</style>
