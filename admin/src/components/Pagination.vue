<template>
  <div class="pagination">
    <button 
      :disabled="currentPage === 1"
      @click="$emit('page-change', currentPage - 1)"
    >
      上一页
    </button>
    
    <button 
      v-for="page in pageNumbers" 
      :key="page"
      :class="{ active: page === currentPage }"
      @click="$emit('page-change', page)"
    >
      {{ page }}
    </button>
    
    <button 
      :disabled="currentPage === totalPages"
      @click="$emit('page-change', currentPage + 1)"
    >
      下一页
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  }
})

defineEmits(['page-change'])

const pageNumbers = computed(() => {
  const pages = []
  for (let i = 1; i <= props.totalPages; i++) {
    pages.push(i)
  }
  return pages
})
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-top: 20px;
}

button {
  padding: 5px 10px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}
</style> 