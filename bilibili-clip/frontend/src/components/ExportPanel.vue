<template>
  <div class="export-panel">
    <el-space wrap>
      <el-select v-model="transition" size="small" style="width: 120px">
        <el-option label="直接拼接" value="cut" />
        <el-option label="交叉淡入" value="crossfade" />
        <el-option label="淡入淡出" value="fade" />
      </el-select>
      <el-select v-model="quality" size="small" style="width: 100px">
        <el-option label="快速" value="fast" />
        <el-option label="平衡" value="balanced" />
        <el-option label="高质量" value="high" />
      </el-select>
      <el-button type="primary" :loading="exporting" @click="handleExport">
        生成切片
      </el-button>
    </el-space>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  taskId: { type: String, required: true },
  segments: { type: Array, default: () => [] },
  exporting: { type: Boolean, default: false },
})

const emit = defineEmits(['export'])

const transition = ref('cut')
const quality = ref('balanced')

function handleExport() {
  emit('export', { transition: transition.value, quality: quality.value })
}
</script>

<style scoped>
.export-panel {
  margin-top: 16px;
  text-align: center;
}
</style>