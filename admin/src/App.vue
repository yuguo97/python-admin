<template>
  <div class="app-container">
    <router-view></router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

const router = useRouter()
const store = useStore()

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    store.commit('setToken', token)
    router.push('/users')
  } else {
    router.push('/login')
  }
})
</script>

<style>
.app-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style> 