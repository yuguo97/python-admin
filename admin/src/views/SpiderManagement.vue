<template>
  <div class="page-container">
    <!-- 顶部导航 -->
    <div class="nav-header">
      <div class="nav-content">
        <div class="left">
          <img src="../assets/logo.png" alt="logo" class="logo">
          <h2>后台管理系统</h2>
        </div>
        <div class="center">
          <el-menu mode="horizontal" :router="true">
            <el-menu-item index="/users">用户管理</el-menu-item>
            <el-menu-item index="/spider">爬虫管理</el-menu-item>
          </el-menu>
        </div>
        <div class="right">
          <el-dropdown @command="handleCommand">
            <el-button class="user-button">
              <el-icon><User /></el-icon>
              {{ store.state.user?.username || 'admin' }}
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <div class="content-header">
        <h3>爬虫管理</h3>
        <p class="subtitle">管理小说爬取任务</p>
      </div>

      <div class="content-card">
        <!-- 工具栏 -->
        <div class="toolbar">
          <el-input
            v-model="newUrl"
            placeholder="请输入小说URL"
            class="url-input"
          >
            <template #append>
              <el-button @click="addUrl">
                <el-icon><Plus /></el-icon>添加
              </el-button>
            </template>
          </el-input>

          <el-button 
            type="primary" 
            :disabled="!urls.length"
            :loading="crawling"
            @click="handleStartCrawl"
          >
            <el-icon><VideoPlay /></el-icon>开始爬取
          </el-button>
        </div>

        <!-- URL列表 -->
        <div v-if="urls.length" class="url-list">
          <el-tag
            v-for="(url, index) in urls"
            :key="index"
            closable
            @close="removeUrl(index)"
            class="url-tag"
          >
            {{ url }}
          </el-tag>
        </div>

        <!-- 小说列表 -->
        <el-table 
          :data="novels" 
          v-loading="loading"
          style="width: 100%; margin-top: 20px;"
        >
          <el-table-column label="小说信息" min-width="300">
            <template #default="{ row }">
              <div class="novel-info">
                <div class="title">{{ row.title }}</div>
                <div class="meta">
                  <span class="author">
                    <el-icon><User /></el-icon>
                    {{ row.author || '未知作者' }}
                  </span>
                  <span class="chapters">
                    <el-icon><Document /></el-icon>
                    {{ row.chapters_count }}章
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="更新时间" width="180">
            <template #default="{ row }">
              <span class="time">{{ row.updated_at }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                link
                @click="openNovel(row.source_url)"
              >
                <el-icon><Link /></el-icon>查看源网页
              </el-button>
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, ArrowDown, Plus, VideoPlay, Document, 
  Link, SwitchButton 
} from '@element-plus/icons-vue'
import { getNovels, startCrawl } from '../api/spider'

const store = useStore()
const router = useRouter()

// 数据相关
const loading = ref(false)
const crawling = ref(false)
const novels = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const newUrl = ref('')
const urls = ref([])

// 获取小说列表
const fetchNovels = async () => {
  try {
    loading.value = true
    const response = await getNovels({
      page: currentPage.value,
      per_page: pageSize.value
    })
    
    console.log('Novels response:', response)  // 添加调试日志
    novels.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    console.error('Fetch novels error:', error)
    ElMessage.error('获取小说列表失败')
  } finally {
    loading.value = false
  }
}

// 添加URL
const addUrl = () => {
  if (!newUrl.value) {
    ElMessage.warning('请输入URL')
    return
  }
  if (urls.value.includes(newUrl.value)) {
    ElMessage.warning('该URL已添加')
    return
  }
  urls.value.push(newUrl.value)
  newUrl.value = ''
}

// 移除URL
const removeUrl = (index) => {
  urls.value.splice(index, 1)
}

// 开始爬取
const handleStartCrawl = async () => {
  if (!urls.value.length) {
    ElMessage.warning('请先添加要爬取的URL')
    return
  }
  
  try {
    crawling.value = true
    const response = await startCrawl(urls.value)
    ElMessage.success('爬取任务已完成')
    urls.value = []  // 清空URL列表
    fetchNovels()  // 刷新小说列表
  } catch (error) {
    console.error('Start crawl error:', error)
    ElMessage.error('爬取失败')
  } finally {
    crawling.value = false
  }
}

// 分页相关
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchNovels()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchNovels()
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    0: '爬取失败',
    1: '爬取中',
    2: '已完成'
  }
  return statusMap[status] || '未知状态'
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    0: 'danger',
    1: 'warning',
    2: 'success'
  }
  return typeMap[status] || 'info'
}

// 打开小说源网页
const openNovel = (url) => {
  window.open(url, '_blank')
}

// 退出登录
const handleCommand = (command) => {
  if (command === 'logout') {
    store.commit('clearToken')
    router.push('/login')
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchNovels()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(120deg, #e0f2fe 0%, #bfdbfe 100%);
}

.nav-header {
  background: white;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  padding: 0 20px;
  height: 60px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 32px;
  height: 32px;
}

.left h2 {
  color: #1e40af;
  font-size: 18px;
  margin: 0;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 20px;
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
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.url-input {
  flex: 1;
}

.url-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.url-tag {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.novel-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title {
  font-weight: 500;
  color: #1e293b;
}

.meta {
  display: flex;
  gap: 16px;
  color: #64748b;
  font-size: 13px;
}

.author,
.chapters {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.time {
  color: #64748b;
  font-size: 13px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
  }
  
  .url-input {
    width: 100%;
  }
}
</style> 