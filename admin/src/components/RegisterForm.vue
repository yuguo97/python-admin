<template>
  <div class="register-form">
    <h3>用户注册</h3>
    <div class="form-group">
      <label>用户名:</label>
      <input 
        v-model="formData.username" 
        type="text" 
        placeholder="请输入用户名"
      >
    </div>
    <div class="form-group">
      <label>密码:</label>
      <input 
        v-model="formData.password" 
        type="password" 
        placeholder="请输入密码"
      >
    </div>
    <div class="form-group">
      <label>邮箱:</label>
      <input 
        v-model="formData.email" 
        type="email" 
        placeholder="请输入邮箱"
      >
    </div>
    <div class="form-group">
      <label>手机号:</label>
      <input 
        v-model="formData.phone" 
        type="text" 
        placeholder="请输入手机号"
      >
    </div>
    <div class="form-actions">
      <button @click="handleRegister">注册</button>
      <button @click="$emit('switch-form')">返回登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { register } from '../api/user'

const formData = ref({
  username: '',
  password: '',
  email: '',
  phone: ''
})

const handleRegister = async () => {
  try {
    await register(formData.value)
    alert('注册成功')
    emit('switch-form')
  } catch (error) {
    alert(error.message)
  }
}
</script>

<style scoped>
.register-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: inline-block;
  width: 100px;
  font-weight: bold;
}

.form-group input {
  width: 250px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  margin-top: 20px;
}

button {
  margin-right: 10px;
}
</style> 