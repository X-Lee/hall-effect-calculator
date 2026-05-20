<template>
  <div class="progress-tracker">
    <el-steps :active="activeIndex" finish-status="success" simple>
      <el-step
        v-for="step in steps"
        :key="step.key"
        :title="step.label"
        :status="stepStatus(step)"
      />
    </el-steps>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: { type: Array, default: () => [] },
  currentStep: { type: String, default: '' },
})

const activeIndex = computed(() => {
  const idx = props.steps.findIndex(s => s.status === 'running')
  if (idx >= 0) return idx
  const doneIdx = props.steps.findLastIndex(s => s.status === 'done')
  return doneIdx >= 0 ? doneIdx + 1 : 0
})

function stepStatus(step) {
  if (step.status === 'done') return 'success'
  if (step.status === 'running') return 'process'
  if (step.status === 'error') return 'error'
  return 'wait'
}
</script>

<style scoped>
.progress-tracker {
  padding: 8px 0;
}
</style>
