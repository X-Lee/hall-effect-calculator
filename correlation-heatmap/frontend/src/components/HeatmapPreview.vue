<template>
  <div v-if="imageUrl" class="preview-container">
    <img :src="imageUrl" alt="Heatmap Preview" class="heatmap-image" />
  </div>
  <el-empty v-else description="上传数据并配置参数后生成热图" />
</template>

<script setup>
defineProps({
  imageUrl: { type: String, default: '' },
})
</script>

<style scoped>
.preview-container {
  text-align: center;
}
.heatmap-image {
  max-width: 100%;
  height: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
</style>
