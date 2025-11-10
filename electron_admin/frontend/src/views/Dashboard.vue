<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon user-icon">
              <el-icon :size="40"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.users }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon role-icon">
              <el-icon :size="40"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.roles }}</div>
              <div class="stat-label">角色总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon permission-icon">
              <el-icon :size="40"><Lock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.permissions }}</div>
              <div class="stat-label">权限总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon menu-icon">
              <el-icon :size="40"><Menu /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.menus }}</div>
              <div class="stat-label">菜单总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :lg="12">
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">系统信息</span>
            </div>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">系统名称:</span>
              <span class="info-value">后台管理系统</span>
            </div>
            <div class="info-item">
              <span class="info-label">系统版本:</span>
              <span class="info-value">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">框架:</span>
              <span class="info-value">Vue 3 + Element Plus</span>
            </div>
            <div class="info-item">
              <span class="info-label">后端:</span>
              <span class="info-value">FastAPI + Python</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" :icon="Plus" @click="goTo('/users')">
              新增用户
            </el-button>
            <el-button type="success" :icon="Plus" @click="goTo('/roles')">
              新增角色
            </el-button>
            <el-button type="warning" :icon="Plus" @click="goTo('/permissions')">
              新增权限
            </el-button>
            <el-button type="info" :icon="Plus" @click="goTo('/menus')">
              新增菜单
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="welcome-card" shadow="never">
          <div class="welcome-content">
            <h2>欢迎使用后台管理系统 👋</h2>
            <p>这是一个基于 Vue 3 + Element Plus + FastAPI 构建的现代化后台管理系统</p>
            <div class="features">
              <el-tag type="success" effect="plain">用户管理</el-tag>
              <el-tag type="primary" effect="plain">角色管理</el-tag>
              <el-tag type="warning" effect="plain">权限管理</el-tag>
              <el-tag type="info" effect="plain">菜单管理</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, UserFilled, Lock, Menu, Plus } from '@element-plus/icons-vue'
import { getUserList } from '@/api/user'
import { getRoleList } from '@/api/role'
import { getPermissionList } from '@/api/permission'
import { getMenuTree } from '@/api/menu'

const router = useRouter()

const stats = ref({
  users: 0,
  roles: 0,
  permissions: 0,
  menus: 0
})

const fetchStats = async () => {
  try {
    const [usersRes, rolesRes, permissionsRes, menusRes] = await Promise.all([
      getUserList(0, 1),
      getRoleList(),
      getPermissionList(),
      getMenuTree()
    ])
    
    stats.value.users = usersRes.data?.total || usersRes.data?.length || 0
    stats.value.roles = rolesRes.data?.length || 0
    stats.value.permissions = permissionsRes.data?.length || 0
    stats.value.menus = menusRes.data?.length || 0
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const goTo = (path) => {
  router.push(path)
}

onMounted(() => {
  fetchStats()
})
</script>

<style lang="less" scoped>
.dashboard-container {
  .stat-card {
    margin-bottom: 20px;
    
    .stat-content {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .stat-icon {
        width: 80px;
        height: 80px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        
        &.user-icon {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        &.role-icon {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        &.permission-icon {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        &.menu-icon {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }
      
      .stat-info {
        flex: 1;
        
        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: #303133;
          margin-bottom: 8px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }
  
  .info-card {
    .card-header {
      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .info-list {
      .info-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        
        &:last-child {
          border-bottom: none;
        }
        
        .info-label {
          color: #909399;
          font-size: 14px;
        }
        
        .info-value {
          color: #303133;
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
    
    .quick-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }
  }
  
  .welcome-card {
    .welcome-content {
      text-align: center;
      padding: 40px 20px;
      
      h2 {
        font-size: 28px;
        color: #303133;
        margin: 0 0 16px 0;
      }
      
      p {
        font-size: 16px;
        color: #606266;
        margin: 0 0 24px 0;
      }
      
      .features {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
      }
    }
  }
}
</style>
