<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2 class="login-title">后台管理系统</h2>
        <p class="login-subtitle">欢迎登录</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        auto-complete="on"
        label-position="left"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            name="username"
            type="text"
            tabindex="1"
            auto-complete="on"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            :type="passwordType"
            placeholder="请输入密码"
            name="password"
            tabindex="2"
            auto-complete="on"
            size="large"
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
          >
            <template #suffix>
              <el-icon class="password-icon" @click="showPassword">
                <View v-if="passwordType === 'password'" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-button
          :loading="loading"
          type="primary"
          size="large"
          style="width: 100%; margin-bottom: 30px"
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-form>
    </div>
    
    <div class="login-footer">
      <p>© 2024 后台管理系统. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { View, Hide } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const passwordType = ref('password')
const loading = ref(false)

const loginForm = reactive({
  username: 'admin',
  password: '123456'
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const showPassword = () => {
  passwordType.value = passwordType.value === 'password' ? 'text' : 'password'
}

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 1. 登录获取 Token
        const success = await userStore.login(loginForm.username, loginForm.password)
        if (success) {
          // 2. 获取用户信息并添加动态路由
          await userStore.fetchUserInfo()
          
          ElMessage.success('登录成功')
          // 3. 跳转到首页
          router.push('/dashboard')
        } else {
          ElMessage.error('登录失败')
        }
      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error('登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="less" scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.1" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,154.7C960,171,1056,181,1152,165.3C1248,149,1344,107,1392,85.3L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
    background-size: cover;
  }

  .login-box {
    width: 450px;
    padding: 40px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    z-index: 1;

    .login-header {
      text-align: center;
      margin-bottom: 40px;

      .login-title {
        font-size: 28px;
        font-weight: 700;
        color: #333;
        margin: 0 0 10px 0;
      }

      .login-subtitle {
        font-size: 14px;
        color: #999;
        margin: 0;
      }
    }

    .login-form {
      .password-icon {
        cursor: pointer;
        user-select: none;
      }
    }
  }

  .login-footer {
    position: absolute;
    bottom: 20px;
    text-align: center;
    color: rgba(255, 255, 255, 0.8);
    font-size: 14px;
    z-index: 1;

    p {
      margin: 0;
    }
  }
}
</style>
