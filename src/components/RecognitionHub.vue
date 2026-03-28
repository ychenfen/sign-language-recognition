<template>
  <div class="recognition-hub">
    <el-alert
      :title="modeTitle"
      :description="modeDescription"
      :type="backendAvailable == null ? 'info' : (backendAvailable ? 'success' : 'warning')"
      :closable="false"
      show-icon
      class="mode-alert"
    >
      <template #default>
        <div class="mode-actions">
          <span>{{ modeDescription }}</span>
          <el-button size="small" @click="refreshMode" :loading="checking">重新检测</el-button>
        </div>
      </template>
    </el-alert>

    <component v-if="activeComponent" :is="activeComponent" />
    <div v-else class="mode-loading">
      正在检测识别服务...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue'
import { checkHealth } from '../api/gestureApi'
import OptimizedGestureRecognition from './OptimizedGestureRecognition.vue'
import GestureRecognition from './GestureRecognition.vue'

const backendAvailable = ref(null)
const checking = ref(false)

const activeComponent = computed(() => (
  backendAvailable.value == null
    ? null
    : (backendAvailable.value ? markRaw(OptimizedGestureRecognition) : markRaw(GestureRecognition))
))

const modeTitle = computed(() => (
  backendAvailable.value == null
    ? '正在检测识别模式'
    : (backendAvailable.value ? '当前为后端识别模式' : '当前为浏览器本地识别模式')
))

const modeDescription = computed(() => (
  backendAvailable.value == null
    ? '正在检查后端服务，检测完成后再加载对应识别组件。'
    : (backendAvailable.value
        ? '后端服务已连接，将使用服务器识别结果。'
        : '后端未启动时会切到浏览器本地识别模式；若仍无法使用，请刷新页面并确认摄像头权限。')
))

const refreshMode = async () => {
  checking.value = true
  backendAvailable.value = null
  try {
    const health = await checkHealth()
    backendAvailable.value = health.status === 'ok'
  } catch (error) {
    backendAvailable.value = false
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  refreshMode()
})
</script>

<style scoped>
.recognition-hub {
  padding: 24px;
}

.mode-alert {
  margin-bottom: 20px;
}

.mode-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.mode-loading {
  padding: 24px;
  color: #64748b;
  text-align: center;
}

@media (max-width: 768px) {
  .recognition-hub {
    padding: 16px;
  }
}
</style>
