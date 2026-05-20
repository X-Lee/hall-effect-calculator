<template>
  <div class="url-input">
    <el-input
      v-model="url"
      placeholder="粘贴B站视频链接，如 https://www.bilibili.com/video/BVxxxxxx"
      size="large"
      :disabled="loading"
      @keyup.enter="handleSubmit"
    >
      <template #append>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          分析
        </el-button>
      </template>
    </el-input>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])
const url = ref('')

function handleSubmit() {
  const val = url.value.trim()
  if (!val) {
    ElMessage.warning('请输入视频链接')
    return
  }
  if (!val.includes('bilibili.com') && !val.includes('b23.tv') && !val.match(/^BV[\w]+$/)) {
    ElMessage.warning('请输入有效的B站视频链接')
    return
  }
  emit('submit', val)
}
</script>

<style scoped>
.url-input {
  width: 100%;
}
</style>
