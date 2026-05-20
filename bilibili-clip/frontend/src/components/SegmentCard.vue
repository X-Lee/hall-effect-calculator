<template>
  <div class="segment-card">
    <div class="seg-header">
      <span class="seg-index">#{{ index + 1 }}</span>
      <span class="seg-time">{{ formatTime(segment.start) }} - {{ formatTime(segment.end) }}</span>
      <span class="seg-duration">({{ formatDuration(segment.end - segment.start) }})</span>
      <el-tag size="small" type="warning">{{ (segment.score * 100).toFixed(0) }}分</el-tag>
      <el-button type="danger" size="small" text @click="$emit('remove')">
        <el-icon><Delete /></el-icon>
      </el-button>
    </div>
    <div v-if="segment.transcript_preview" class="seg-transcript">
      {{ segment.transcript_preview }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  segment: { type: Object, required: true },
  index: { type: Number, required: true },
})

defineEmits(['remove'])

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function formatDuration(seconds) {
  return `${Math.floor(seconds)}s`
}
</script>

<style scoped>
.segment-card {
  padding: 10px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 8px;
}
.seg-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.seg-index {
  font-weight: 600;
  color: #409eff;
}
.seg-time {
  font-family: monospace;
  font-size: 13px;
}
.seg-duration {
  color: #909399;
  font-size: 12px;
}
.seg-transcript {
  margin-top: 6px;
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}
</style>
