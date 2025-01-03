<template>
  <el-dialog
    :title="user ? '编辑用户' : '添加用户'"
    v-model="dialogVisible"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="formData.username"
          placeholder="请输入用户名"
          :disabled="!!user"
        />
      </el-form-item>
      
      <el-form-item label="邮箱" prop="email">
        <el-input 
          v-model="formData.email"
          placeholder="请输入邮箱"
        />
      </el-form-item>
      
      <el-form-item 
        label="密码" 
        prop="password"
        :rules="user ? passwordRules : requiredPasswordRules"
      >
        <el-input 
          v-model="formData.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>
      
      <el-form-item label="手机号" prop="phone">
        <el-input 
          v-model="formData.phone"
          placeholder="请输入手机号"
        />
      </el-form-item>
      
      <el-form-item label="状态">
        <el-radio-group v-model="formData.status">
          <el-radio :label="1">正常</el-radio>
          <el-radio :label="0">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="备注">
        <el-input 
          v-model="formData.remark"
          type="textarea"
          placeholder="请输入备注信息"
          :rows="3"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createUser, updateUser } from '../api/user'

const props = defineProps({
  visible: Boolean,
  user: Object
})

const emit = defineEmits(['update:visible', 'success'])

const dialogVisible = ref(props.visible)
const loading = ref(false)
const formRef = ref(null)

// 表单数据
const formData = ref({
  username: '',
  email: '',
  password: '',
  phone: '',
  status: 1,
  remark: ''
})

// 表单验证规则
const requiredPasswordRules = [
  { required: true, message: '请输入密码', trigger: 'blur' },
  { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
]

const passwordRules = [
  { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
]

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能小于3位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ]
}

// 监听visible属性变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
})

// 监听dialogVisible变化
watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 监听user属性变化
watch(() => props.user, (val) => {
  if (val) {
    formData.value = {
      ...val,
      password: '' // 编辑时不显示密码
    }
  } else {
    formData.value = {
      username: '',
      email: '',
      password: '',
      phone: '',
      status: 1,
      remark: ''
    }
  }
})

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate(async (valid) => {
      if (valid) {
        loading.value = true
        
        // 构造提交数据
        const submitData = {
          ...formData.value
        }
        
        // 如果是编辑模式且没有修改密码，则不提交密码字段
        if (props.user && !submitData.password) {
          delete submitData.password
        }
        
        try {
          if (props.user) {
            // 编辑用户
            await updateUser(props.user.id, submitData)
            ElMessage.success('更新成功')
          } else {
            // 创建用户
            await createUser(submitData)
            ElMessage.success('创建成功')
          }
          handleClose()
          emit('success')
        } catch (error) {
          console.error('Submit error:', error)
          ElMessage.error(error.response?.data?.message || '操作失败')
        }
      }
    })
  } catch (error) {
    console.error('Validation error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 