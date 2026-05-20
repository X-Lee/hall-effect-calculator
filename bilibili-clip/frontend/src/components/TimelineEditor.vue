<template>
  <div class="timeline-editor">
    <div class="timeline-bar" ref="barEl">
      <div
        v-for="(w, i) in windows"
        :key="i"
        class="window-block"
        :style="{
          left: (w.start / duration * 100) + '%',
          width: ((w.end - w.start) / duration * 100) + '%',
          backgroundColor: scoreColor(w.combined_score),
        }"
        :title="`${formatTime(w.start)}-${formatTime(w.end)} 分数:${(w.combined_score*100).toFixed(0)}`"
      />
      <div
        v-for="(seg, i) in segments"
        :key="'seg-' + i"
        class="segment-overlay"
        :style="{
          left: (seg.start / duration * 100) + '%',
          width: ((seg.end - seg.start) / duration * 100) + '%',
        }"
      />
    </div>
    <div class="timeline-labels">
      <span>0:00</span>
      <span>{{ formatTime(duration / 2) }}</span>
      <span>{{ formatTime(duration) }}</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  windows: { type: Array, default: () => [] },
  segments: { type: Array, default: () => [] },
  duration: { type: Number, default: 0 },
})

defineEmits(['update-segments'])

function scoreColor(score) {
  const r = Math.round(255 * score)
  const b = Math.round(255 * (1 - score))
  return `rgba(${r}, 50, ${b}, 0.6)`
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.timeline-editor {
  padding: 8px 0;
}
.timeline-bar {
  position: relative;
  height: 40px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}
.window-block {
  position: absolute;
  top: 0;
  height: 100%;
}
.segment-overlay {
  position: absolute;
  top: 0;
  height: 100%;
  border: 2px solid #409eff;
  border-radius: 3px;
  background: rgba(64, 158, 255, 0.15);
  pointer-events: none;
}
.timeline-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 11px;
  color: #909399;
}
</style>
