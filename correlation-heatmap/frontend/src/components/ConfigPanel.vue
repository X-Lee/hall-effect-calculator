<template>
  <el-form label-position="top" size="default">
    <el-form-item>
      <template #label>
        <span>选择数值列</span>
        <el-button size="small" type="primary" @click="selectAll" style="margin-left: 12px">全选</el-button>
      </template>
      <el-checkbox-group v-model="config.columns">
        <el-checkbox
          v-for="col in numericColumns"
          :key="col"
          :label="col"
          :value="col"
        />
      </el-checkbox-group>
    </el-form-item>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="相关性方法">
          <el-select v-model="config.method">
            <el-option label="Pearson" value="pearson" />
            <el-option label="Spearman" value="spearman" />
            <el-option label="Kendall" value="kendall" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="配色方案">
          <el-select v-model="config.colormap">
            <el-option v-for="c in colormaps" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="标注格式">
          <el-select v-model="config.annot_format">
            <el-option label=".2f (0.85)" value=".2f" />
            <el-option label=".3f (0.853)" value=".3f" />
            <el-option label=".1f (0.9)" value=".1f" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">滞后相关性（可选）</el-divider>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="目标列（滞后变量）">
          <el-select v-model="config.target_column" clearable placeholder="不使用滞后">
            <el-option
              v-for="col in config.columns"
              :key="col"
              :label="col"
              :value="col"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="滞后模式">
          <el-radio-group v-model="config.lag_mode" :disabled="!config.target_column">
            <el-radio value="single">固定滞后</el-radio>
            <el-radio value="sweep">最优滞后搜索</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16" v-if="config.target_column">
      <el-col :span="8" v-if="config.lag_mode === 'single'">
        <el-form-item label="滞后期数">
          <el-input-number v-model="config.lag_periods" :min="0" :max="maxLag" />
        </el-form-item>
      </el-col>
      <template v-if="config.lag_mode === 'sweep'">
        <el-col :span="8">
          <el-form-item label="起始滞后">
            <el-input-number v-model="config.lag_range_start" :min="0" :max="config.lag_range_end" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="结束滞后">
            <el-input-number v-model="config.lag_range_end" :min="config.lag_range_start" :max="maxLag" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="热图滞后期数">
            <el-input-number v-model="config.lag_periods" :min="0" :max="maxLag" />
          </el-form-item>
        </el-col>
      </template>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="字体大小">
          <el-input-number v-model="config.font_size" :min="8" :max="24" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="图片宽度">
          <el-input-number v-model="config.figure_size[0]" :min="4" :max="20" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="图片高度">
          <el-input-number v-model="config.figure_size[1]" :min="4" :max="20" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="标题">
      <el-input v-model="config.title" placeholder="Correlation Matrix" />
    </el-form-item>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item>
          <el-checkbox v-model="config.show_values">显示数值</el-checkbox>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item>
          <el-checkbox v-model="config.show_significance">显著性标注</el-checkbox>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item>
          <el-checkbox v-model="config.mask_upper">遮盖上三角</el-checkbox>
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item>
      <el-button type="primary" @click="handleGenerate" :loading="loading" :disabled="config.columns.length < 2">
        生成热图
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getColormaps } from '../api'

const props = defineProps({
  numericColumns: { type: Array, default: () => [] },
  rowCount: { type: Number, default: 100 },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['generate'])

const colormaps = ref([])

const maxLag = computed(() => Math.max(0, Math.floor(props.rowCount * 0.5) - 3))

const config = reactive({
  columns: [],
  method: 'pearson',
  colormap: 'RdBu_r',
  show_values: true,
  show_significance: true,
  significance_levels: [0.001, 0.01, 0.05],
  figure_size: [10, 8],
  font_size: 12,
  title: 'Correlation Matrix',
  mask_upper: true,
  vmin: -1.0,
  vmax: 1.0,
  annot_format: '.2f',
  target_column: null,
  lag_periods: 0,
  lag_mode: 'single',
  lag_range_start: 0,
  lag_range_end: 10,
})

function selectAll() {
  config.columns = [...props.numericColumns]
}

function handleGenerate() {
  emit('generate', { ...config })
}

onMounted(async () => {
  try {
    const { data } = await getColormaps()
    colormaps.value = data.colormaps
  } catch {
    colormaps.value = ['RdBu_r', 'coolwarm', 'viridis', 'plasma', 'seismic']
  }
})
</script>
