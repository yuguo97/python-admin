<template>
  <div class="navbar">
    <div class="left-menu">
      <el-icon class="hamburger" @click="toggleSidebar">
        <Fold v-if="sidebar.opened" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb class="breadcrumb" separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
          {{ item.meta?.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <div class="right-menu">
      <el-dropdown class="avatar-container" trigger="click">
        <div class="avatar-wrapper">
          <el-avatar :size="32" :src="userInfo?.avatar">
            <el-icon><UserFilled /></el-icon>
          </el-avatar>
          <span class="username">{{ userInfo?.username || '管理员' }}</span>
          <el-icon class="el-icon--right">
            <arrow-down />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleChangePassword">
              <el-icon><Key /></el-icon>
              修改密码
            </el-dropdown-item>
            <el-dropdown-item @click="handleProfile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordFormData"
        :rules="passwordFormRules"
        label-width="100px"
      >
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordFormData.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordFormData.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePasswordSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { updateUser } from '@/api/user'
import {
  Fold,
  Expand,
  UserFilled,
  User,
  SwitchButton,
  ArrowDown,
  Key
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const userStore = useUserStore()

const sidebar = computed(() => appStore.sidebar)
const userInfo = computed(() => userStore.userInfo)

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title)
})

const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)
const submitLoading = ref(false)

const passwordFormData = reactive({
  new_password: '',
  confirm_password: ''
})

const passwordFormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordFormData.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

const handleProfile = () => {
  router.push('/profile')
}

const handleChangePassword = () => {
  passwordFormData.new_password = ''
  passwordFormData.confirm_password = ''
  passwordDialogVisible.value = true
}

const handlePasswordSubmit = () => {
  passwordFormRef.value?.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await updateUser(userStore.userInfo.id, { password: passwordFormData.new_password })
        ElMessage.success('密码修改成功,请重新登录')
        passwordDialogVisible.value = false
        setTimeout(() => {
          userStore.logout()
          router.push('/login')
        }, 1500)
      } catch (error) {
        ElMessage.error('密码修改失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  })
}
</script>

<style lang="less" scoped>
.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;

  .left-menu {
    display: flex;
    align-items: center;
    
    .hamburger {
      font-size: 20px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        color: #409EFF;
      }
    }
    
    .breadcrumb {
      margin-left: 20px;
    }
  }

  .right-menu {
    display: flex;
    align-items: center;
    height: 100%;

    .avatar-container {
      cursor: pointer;
      height: 100%;
      display: flex;
      align-items: center;

      .avatar-wrapper {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .username {
          font-size: 14px;
          color: #606266;
        }
        
        &:hover {
          .username {
            color: #409EFF;
          }
        }
      }
    }
  }
}
</style>
