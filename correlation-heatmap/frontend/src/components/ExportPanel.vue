<template>
  <div v-if="taskId" class="export-panel">
    <el-space>
      <el-button type="success" @click="download('png')">下载 PNG (300 DPI)</el-button>
      <el-button type="warning" @click="download('pdf')">下载 PDF</el-button>
      <el-button
        v-if="lagConfig && lagConfig.target_column && lagConfig.lag_periods > 0"
        type="info"
        @click="downloadLagData"
        :loading="exporting"
      >
        导出滞后数据
      </el-button>
    </el-space>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getExportUrl, exportLagData } from '../api'

const props = defineProps({
  taskId: { type: String, default: '' },
  lagConfig: { type: Object, default: null },
})

const exporting = ref(false)

function download(format) {
  const url = getExportUrl(props.taskId, format, 300)
  const a = document.createElement('a')
  a.href = url
  a.download = `heatmap.${format}`
  a.click()
}

async function downloadLagData() {
  if (!props.lagConfig) return
  exporting.value = true
  try {
    const { data } = await exportLagData(props.lagConfig)
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `lag_data_${props.lagConfig.target_column}_lag${props.lagConfig.lag_periods}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('导出失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.export-panel {
  margin-top: 16px;
  text-align: center;
}
</style>
