<template>
  <div class="settings-view">
    <el-card header="API 配置">
      <el-form label-width="140px" :model="form">
        <el-form-item label="Anthropic API Key">
          <el-input
            v-model="form.anthropic_api_key"
            type="password"
            show-password
            placeholder="sk-ant-..."
          />
          <div class="hint" v-if="apiKeySet">已配置</div>
        </el-form-item>

        <el-divider content-position="left">Whisper 语音识别</el-divider>

        <el-form-item label="模型大小">
          <el-select v-model="form.whisper_model">
            <el-option label="tiny (最快, 效果一般)" value="tiny" />
            <el-option label="base (快速)" value="base" />
            <el-option label="small (平衡)" value="small" />
            <el-option label="medium (推荐, 中文效果好)" value="medium" />
            <el-option label="large (最准, 最慢)" value="large" />
          </el-select>
        </el-form-item>

        <el-form-item label="运行设备">
          <el-select v-model="form.whisper_device">
            <el-option label="自动检测" value="auto" />
            <el-option label="CPU" value="cpu" />
            <el-option label="GPU (CUDA)" value="cuda" />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">分析权重</el-divider>

        <el-form-item label="弹幕密度">
          <el-slider v-model="form.weight_danmaku" :min="0" :max="100" :step="5" show-input />
        </el-form-item>
        <el-form-item label="音频能量">
          <el-slider v-model="form.weight_audio" :min="0" :max="100" :step="5" show-input />
        </el-form-item>
        <el-form-item label="AI语义">
          <el-slider v-model="form.weight_ai" :min="0" :max="100" :step="5" show-input />
        </el-form-item>

        <el-divider content-position="left">切片参数</el-divider>

        <el-form-item label="目标时长(秒)">
          <el-input-number v-model="form.target_duration" :min="60" :max="600" :step="30" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../api'

const form = ref({
  anthropic_api_key: '',
  whisper_model: 'medium',
  whisper_device: 'auto',
  weight_danmaku: 40,
  weight_audio: 30,
  weight_ai: 30,
  target_duration: 150,
})

const apiKeySet = ref(false)
const saving = ref(false)

onMounted(async () => {
  try {
    const { data } = await getSettings()
    apiKeySet.value = data.anthropic_api_key_set
    form.value.whisper_model = data.whisper_model
    form.value.whisper_device = data.whisper_device
    form.value.weight_danmaku = Math.round((data.weights?.danmaku || 0.4) * 100)
    form.value.weight_audio = Math.round((data.weights?.audio || 0.3) * 100)
    form.value.weight_ai = Math.round((data.weights?.ai || 0.3) * 100)
    form.value.target_duration = data.target_duration
  } catch (e) {
    // ignore
  }
})

async function handleSave() {
  saving.value = true
  const total = form.value.weight_danmaku + form.value.weight_audio + form.value.weight_ai
  try {
    const payload = {
      whisper_model: form.value.whisper_model,
      whisper_device: form.value.whisper_device,
      weights: {
        danmaku: form.value.weight_danmaku / total,
        audio: form.value.weight_audio / total,
        ai: form.value.weight_ai / total,
      },
      target_duration: form.value.target_duration,
    }
    if (form.value.anthropic_api_key) {
      payload.anthropic_api_key = form.value.anthropic_api_key
    }
    await updateSettings(payload)
    ElMessage.success('配置已保存')
    apiKeySet.value = apiKeySet.value || !!form.value.anthropic_api_key
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-view {
  max-width: 700px;
}
.hint {
  color: #67c23a;
  font-size: 12px;
  margin-top: 4px;
}
</style>
