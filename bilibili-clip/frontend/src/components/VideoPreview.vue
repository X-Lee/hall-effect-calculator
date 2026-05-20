<template>
  <div class="video-preview">
    <video
      ref="videoEl"
      :src="previewUrl"
      controls
      class="video-player"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getPreviewUrl } from '../api'

const props = defineProps({
  taskId: { type: String, required: true },
  segments: { type: Array, default: () => [] },
})

const previewUrl = computed(() => getPreviewUrl(props.taskId))
</script>

<style scoped>
.video-preview {
  width: 100%;
}
.video-player {
  width: 100%;
  max-height: 360px;
  border-radius: 8px;
  background: #000;
}
</style>
