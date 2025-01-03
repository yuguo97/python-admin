<template>
  <div class="login-container">
    <div class="login-card">
      <h2>系统登录</h2>
      <el-form
        ref="loginForm"
        :model="loginData"
        :rules="loginRules"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginData.username"
            placeholder="用户名"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginData.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import request from '../api/request'

const router = useRouter()
const store = useStore()
const loginForm = ref(null)
const loading = ref(false)

const loginData = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginForm.value) return
  
  try {
    await loginForm.value.validate()
    loading.value = true
    
    const { data } = await request({
      url: '/auth/login',
      method: 'post',
      data: loginData
    })
    
    const token = data.token.startsWith('Bearer ') ? data.token : `Bearer ${data.token}`
    store.commit('setToken', token)
    store.commit('setUser', data.user)
    
    ElMessage.success('登录成功')
    
    const redirect = router.currentRoute.value.query.redirect || '/'
    router.push(redirect)
    
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error(error.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
}

.login-card {
  width: 100%;
  max-width: 360px;
  padding: 32px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-card h2 {
  text-align: center;
  color: #1e293b;
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
}

:deep(.el-input__wrapper) {
  background-color: #f8fafc;
}

:deep(.el-input__inner) {
  height: 40px;
}

:deep(.el-form-item__error) {
  color: #ef4444;
}
</style> 