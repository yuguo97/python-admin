<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>用户管理系统</h2>
          <p class="subtitle">欢迎登录</p>
        </div>
      </template>
      
      <el-form 
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="formData.username"
            :prefix-icon="User"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="formData.password"
            :prefix-icon="Lock"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <div class="form-actions">
          <el-button 
            type="primary" 
            :loading="loading"
            class="submit-btn" 
            @click="handleLogin"
          >
            登录
          </el-button>
          <el-button 
            class="register-btn"
            @click="$emit('switch-form')"
          >
            注册新用户
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '../api/user'

const router = useRouter()
const store = useStore()
const formRef = ref(null)
const loading = ref(false)

const formData = ref({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await login(formData.value)
        store.commit('setToken', response.data.token)
        ElMessage.success('登录成功')
        router.push('/users')
      } catch (error) {
        ElMessage.error(error.message || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
  padding: 10px 0;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.subtitle {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

:deep(.el-form-item__label) {
  font-weight: 500;
  padding-bottom: 8px;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-actions {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.submit-btn,
.register-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.submit-btn {
  background: linear-gradient(to right, #667eea, #764ba2);
  border: none;
}

.submit-btn:hover {
  background: linear-gradient(to right, #5a6fd6, #6a439c);
  transform: translateY(-1px);
  transition: all 0.3s ease;
}

.register-btn {
  border: 1px solid #dcdfe6;
}

.register-btn:hover {
  border-color: #764ba2;
  color: #764ba2;
}

@media (max-width: 480px) {
  .login-card {
    width: 90%;
    margin: 20px;
  }
}
</style> 