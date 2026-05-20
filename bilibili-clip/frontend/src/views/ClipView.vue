<template>
  <div class="clip-view">
    <el-row :gutter="24">
      <el-col :span="10">
        <el-card header="1. 输入视频链接">
          <UrlInput :loading="downloading" @submit="handleSubmit" />
          <div v-if="videoInfo" class="video-info">
            <img :src="videoInfo.thumbnail_url" class="thumbnail" />
            <div class="info-text">
              <h4>{{ videoInfo.title }}</h4>
              <span>时长: {{ formatDuration(videoInfo.duration) }}</span>
            </div>
          </div>
        </el-card>

        <el-card header="2. 分析进度" style="margin-top: 16px" v-if="taskId">
          <ProgressTracker :steps="progressSteps" :current-step="currentStep" />
          <el-button
            v-if="canAnalyze"
            type="primary"
            :loading="analyzing"
            @click="handleAnalyze"
            style="margin-top: 12px; width: 100%"
          >
            开始分析
          </el-button>
        </el-card>

        <el-card header="3. 片段列表" style="margin-top: 16px" v-if="segments.length">
          <div class="segment-list">
            <SegmentCard
              v-for="(seg, idx) in segments"
              :key="idx"
              :segment="seg"
              :index="idx"
              @remove="removeSegment(idx)"
            />
          </div>
          <div class="total-duration">
            总时长: {{ formatDuration(totalDuration) }}
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card header="4. 预览与导出" class="preview-card">
          <VideoPreview v-if="taskId && canPreview" :task-id="taskId" :segments="segments" />
          <div v-if="segments.length" class="timeline-section">
            <TimelineEditor
              :windows="windows"
              :segments="segments"
              :duration="videoInfo?.duration || 0"
              @update-segments="handleUpdateSegments"
            />
          </div>
          <ExportPanel
            v-if="segments.length"
            :task-id="taskId"
            :segments="segments"
            :exporting="exporting"
            @export="handleExport"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import UrlInput from '../components/UrlInput.vue'
import ProgressTracker from '../components/ProgressTracker.vue'
import SegmentCard from '../components/SegmentCard.vue'
import VideoPreview from '../components/VideoPreview.vue'
import TimelineEditor from '../components/TimelineEditor.vue'
import ExportPanel from '../components/ExportPanel.vue'
import { submitVideo, startAnalysis, getAnalysisResults, generateClip, getDownloadUrl } from '../api'

const taskId = ref('')
const videoInfo = ref(null)
const downloading = ref(false)
const analyzing = ref(false)
const exporting = ref(false)
const segments = ref([])
const windows = ref([])
const currentStep = ref('')

const progressSteps = ref([
  { key: 'download', label: '下载视频', status: 'pending' },
  { key: 'danmaku', label: '弹幕分析', status: 'pending' },
  { key: 'audio', label: '音频分析', status: 'pending' },
  { key: 'transcription', label: '语音识别', status: 'pending' },
  { key: 'ai_scoring', label: 'AI打分', status: 'pending' },
  { key: 'fusion', label: '融合评分', status: 'pending' },
])

const canAnalyze = computed(() => {
  return taskId.value && !analyzing.value && currentStep.value === 'downloaded'
})

const canPreview = computed(() => {
  return currentStep.value === 'downloaded' || currentStep.value === 'analyzed'
})

const totalDuration = computed(() => {
  return segments.value.reduce((sum, s) => sum + (s.end - s.start), 0)
})

async function handleSubmit(url) {
  downloading.value = true
  segments.value = []
  windows.value = []
  try {
    const { data } = await submitVideo(url)
    taskId.value = data.task_id
    videoInfo.value = data
    updateStep('download', 'running')
    listenDownloadProgress(data.task_id)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    downloading.value = false
  }
}

function listenDownloadProgress(id) {
  const sse = new EventSource(`/api/video/${id}/stream`)
  sse.addEventListener('progress', (event) => {
    const data = JSON.parse(event.data)
    if (data.status === 'downloaded') {
      updateStep('download', 'done')
      currentStep.value = 'downloaded'
      sse.close()
    } else if (data.status === 'error') {
      updateStep('download', 'error')
      ElMessage.error(data.message)
      sse.close()
    }
  })
  sse.onerror = () => sse.close()
}

async function handleAnalyze() {
  analyzing.value = true
  try {
    await startAnalysis(taskId.value)
    listenAnalysisProgress(taskId.value)
  } catch (e) {
    ElMessage.error('启动分析失败')
    analyzing.value = false
  }
}

function listenAnalysisProgress(id) {
  const sse = new EventSource(`/api/analysis/${id}/progress`)
  sse.addEventListener('progress', (event) => {
    const data = JSON.parse(event.data)
    if (data.step && data.step !== 'init') {
      updateStep(data.step, data.step === 'done' ? 'done' : 'running')
    }
    if (data.step === 'done') {
      currentStep.value = 'analyzed'
      sse.close()
      fetchResults(id)
    } else if (data.step === 'error') {
      ElMessage.error(data.message)
      sse.close()
      analyzing.value = false
    }
  })
  sse.onerror = () => { sse.close(); analyzing.value = false }
}

async function fetchResults(id) {
  try {
    const { data } = await getAnalysisResults(id)
    windows.value = data.windows
    segments.value = data.suggested_segments
    ElMessage.success(`分析完成，推荐 ${segments.value.length} 个片段`)
  } catch (e) {
    ElMessage.error('获取结果失败')
  } finally {
    analyzing.value = false
  }
}

function removeSegment(idx) {
  segments.value.splice(idx, 1)
}

function handleUpdateSegments(newSegments) {
  segments.value = newSegments
}

async function handleExport({ transition, quality }) {
  exporting.value = true
  try {
    const { data } = await generateClip(taskId.value, segments.value, transition, quality)
    const url = getDownloadUrl(taskId.value)
    const a = document.createElement('a')
    a.href = url
    a.download = 'highlight_clip.mp4'
    a.click()
    ElMessage.success('切片生成完成')
  } catch (e) {
    ElMessage.error('导出失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    exporting.value = false
  }
}

function updateStep(key, status) {
  const step = progressSteps.value.find(s => s.key === key)
  if (step) step.status = status
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.video-info {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}
.thumbnail {
  width: 160px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
}
.info-text h4 {
  margin: 0 0 8px;
  font-size: 14px;
}
.info-text span {
  color: #909399;
  font-size: 13px;
}
.segment-list {
  max-height: 300px;
  overflow-y: auto;
}
.total-duration {
  margin-top: 12px;
  text-align: center;
  font-weight: 600;
  color: #409eff;
}
.timeline-section {
  margin: 16px 0;
}
.preview-card {
  min-height: 400px;
}
</style>
