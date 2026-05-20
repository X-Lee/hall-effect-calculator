<template>
  <el-upload
    drag
    :auto-upload="false"
    :on-change="handleFileChange"
    :limit="1"
    accept=".csv,.xlsx,.xls"
    :file-list="fileList"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
    <template #tip>
      <div class="el-upload__tip">支持 CSV、Excel (.xlsx/.xls) 格式</div>
    </template>
  </el-upload>

  <div v-if="uploading" style="margin-top: 12px">
    <el-progress :percentage="100" status="success" :indeterminate="true" />
  </div>

  <div v-if="fileInfo" class="file-info">
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="行数">{{ fileInfo.row_count }}</el-descriptions-item>
      <el-descriptions-item label="总列数">{{ fileInfo.columns.length }}</el-descriptions-item>
      <el-descriptions-item label="数值列数">{{ fileInfo.numeric_columns.length }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadFile as apiUpload } from '../api'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['uploaded'])

const fileList = ref([])
const uploading = ref(false)
const fileInfo = ref(null)

async function handleFileChange(file) {
  if (!file.raw) return
  uploading.value = true
  try {
    const { data } = await apiUpload(file.raw)
    fileInfo.value = data
    emit('uploaded', data)
  } catch (e) {
    ElMessage.error('文件上传失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.file-info {
  margin-top: 16px;
}
</style>
