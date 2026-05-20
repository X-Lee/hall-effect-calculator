<template>
  <div class="heatmap-view">
    <el-row :gutter="24" :class="['top-row', { 'equal-height': !imageUrl && !fileData }]">
      <el-col :span="10">
        <el-card header="1. 上传数据" class="full-height-card">
          <FileUpload @uploaded="handleUploaded" />
        </el-card>

        <el-card header="2. 配置参数" style="margin-top: 16px" v-if="fileData">
          <ConfigPanel
            :numeric-columns="fileData.numeric_columns"
            :row-count="fileData.row_count"
            :loading="generating"
            @generate="handleGenerate"
          />
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card header="3. 热图预览" class="full-height-card">
          <HeatmapPreview :image-url="imageUrl" />
          <ExportPanel :task-id="taskId" :lag-config="lastConfig" />

          <template v-if="lagSweepResults && lagSweepResults.length">
            <el-divider content-position="left">最优滞后搜索结果</el-divider>
            <el-table :data="lagSweepResults" size="small" stripe border>
              <el-table-column prop="feature" label="影响因素" />
              <el-table-column prop="best_lag" label="最优滞后期" width="110" align="center" />
              <el-table-column label="最强相关系数" width="130" align="center">
                <template #default="{ row }">
                  {{ row.best_correlation.toFixed(4) }}
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import FileUpload from '../components/FileUpload.vue'
import ConfigPanel from '../components/ConfigPanel.vue'
import HeatmapPreview from '../components/HeatmapPreview.vue'
import ExportPanel from '../components/ExportPanel.vue'
import { generateHeatmap } from '../api'

const fileData = ref(null)
const imageUrl = ref('')
const taskId = ref('')
const generating = ref(false)
const lagSweepResults = ref(null)
const lastConfig = ref(null)

function handleUploaded(data) {
  fileData.value = data
  imageUrl.value = ''
  taskId.value = ''
  lagSweepResults.value = null
  lastConfig.value = null
}

async function handleGenerate(config) {
  generating.value = true
  lagSweepResults.value = null
  const fullConfig = { file_id: fileData.value.file_id, ...config }
  try {
    const { data } = await generateHeatmap(fullConfig)
    imageUrl.value = data.image_base64
    taskId.value = data.task_id
    lagSweepResults.value = data.lag_sweep_results || null
    lastConfig.value = fullConfig
    ElMessage.success('热图生成成功')
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.top-row {
  display: flex;
  align-items: flex-start;
}
.top-row.equal-height {
  align-items: stretch;
}
.top-row.equal-height > .el-col {
  display: flex;
}
.top-row.equal-height > .el-col > .full-height-card {
  width: 100%;
  display: flex;
  flex-direction: column;
}
.top-row.equal-height > .el-col > .full-height-card :deep(.el-card__body) {
  flex: 1;
}
</style>
