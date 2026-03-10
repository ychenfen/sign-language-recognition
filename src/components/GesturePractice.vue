<template>
  <el-card class="practice-card">
    <template #header>
      <div class="card-header">
        <span>✋ 手势练习</span>
        <el-tag :type="connectionStatus.type" size="small">
          {{ connectionStatus.text }}
        </el-tag>
      </div>
    </template>

    <!-- 练习模式选择 -->
    <div class="mode-selector" v-if="!isPracticing">
      <h3>选择练习模式</h3>
      <el-radio-group v-model="practiceMode" size="large">
        <el-radio-button value="free">自由练习</el-radio-button>
        <el-radio-button value="challenge">挑战模式</el-radio-button>
        <el-radio-button value="review">复习模式</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 手势选择 -->
    <div class="gesture-selector" v-if="!isPracticing">
      <h3>选择要练习的手势</h3>
      <div class="gesture-grid">
        <div
          v-for="gesture in gestures"
          :key="gesture.id"
          :class="['gesture-item', { selected: selectedGesture?.id === gesture.id }]"
          @click="selectGesture(gesture)"
        >
          <div class="gesture-icon">{{ getGestureIcon(gesture.id) }}</div>
          <div class="gesture-name">{{ gesture.name }}</div>
        </div>
      </div>

      <el-button
        type="primary"
        size="large"
        @click="startPractice"
        :disabled="!selectedGesture"
        class="start-btn"
      >
        开始练习
      </el-button>
    </div>

    <!-- 练习界面 -->
    <div class="practice-area" v-else>
      <!-- 目标手势 -->
      <div class="target-gesture">
        <h3>请做出这个手势：</h3>
        <div class="target-display">
          <span class="target-icon">{{ getGestureIcon(currentTarget.id) }}</span>
          <span class="target-name">{{ currentTarget.name }}</span>
        </div>
        <p class="target-desc">{{ currentTarget.description }}</p>
      </div>

      <!-- 摄像头区域 -->
      <div class="camera-area">
        <video ref="videoElement" autoplay playsinline></video>
        <canvas ref="canvasElement" style="display: none;"></canvas>

        <!-- 识别结果覆盖层 -->
        <div class="result-overlay" v-if="lastResult">
          <div :class="['result-badge', lastResult.correct ? 'correct' : 'incorrect']">
            {{ lastResult.correct ? '✓ 正确！' : '✗ 再试试' }}
          </div>
        </div>
      </div>

      <!-- 控制按钮 -->
      <div class="control-buttons">
        <el-button @click="captureAndVerify" :loading="isVerifying" type="primary" size="large">
          📸 拍照验证
        </el-button>
        <el-button @click="skipGesture" type="info" size="large">
          ⏭️ 跳过
        </el-button>
        <el-button @click="endPractice" type="danger" size="large">
          🛑 结束练习
        </el-button>
      </div>

      <!-- 反馈信息 -->
      <div class="feedback-area" v-if="feedback">
        <el-alert
          :title="feedback.message"
          :type="getFeedbackType(feedback.status)"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="feedback-details">
              <div class="stars">
                <span v-for="i in 3" :key="i" :class="{ active: i <= feedback.stars }">⭐</span>
              </div>
              <p v-if="feedback.tip" class="tip">💡 {{ feedback.tip }}</p>
            </div>
          </template>
        </el-alert>
      </div>

      <!-- 练习统计 -->
      <div class="practice-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="已完成" :value="stats.completed" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="正确" :value="stats.correct" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="准确率">
              <template #default>
                {{ stats.completed > 0 ? Math.round(stats.correct / stats.completed * 100) : 0 }}%
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="连续正确" :value="stats.streak" />
          </el-col>
        </el-row>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getGestures,
  verifyGesture,
  getPracticeFeedback,
  checkHealth
} from '../api/gestureApi.js'

const gestures = ref([])
const selectedGesture = ref(null)
const currentTarget = ref(null)
const practiceMode = ref('free')
const isPracticing = ref(false)
const isVerifying = ref(false)
const lastResult = ref(null)
const feedback = ref(null)
const isConnected = ref(false)

const videoElement = ref(null)
const canvasElement = ref(null)
let mediaStream = null

const stats = reactive({
  completed: 0,
  correct: 0,
  streak: 0
})

const connectionStatus = computed(() => {
  if (isConnected.value) {
    return { type: 'success', text: 'API已连接' }
  }
  return { type: 'warning', text: 'API未连接' }
})

const fallbackGestures = [
  { id: 'one', name: '一', description: '伸出食指', type: 'static' },
  { id: 'two', name: '二', description: '伸出食指和中指', type: 'static' },
  { id: 'three', name: '三', description: '伸出食指、中指、无名指', type: 'static' },
  { id: 'five', name: '五', description: '五指张开', type: 'static' },
  { id: 'thumbs_up', name: '点赞', description: '竖起大拇指', type: 'static' },
  { id: 'ok', name: 'OK', description: '拇指和食指形成圆圈', type: 'static' }
]

// 手势图标映射
const gestureIcons = {
  zero: '✊',
  one: '☝️',
  two: '✌️',
  three: '🤟',
  four: '🖖',
  five: '🖐️',
  six: '🤙',
  eight: '👌',
  thumbs_up: '👍',
  ok: '👌',
  i_love_you: '🤟',
  rock: '🤘'
}

function getGestureIcon(id) {
  return gestureIcons[id] || '✋'
}

function getFeedbackType(status) {
  const types = {
    excellent: 'success',
    good: 'success',
    pass: 'warning',
    retry: 'error'
  }
  return types[status] || 'info'
}

// 检查API连接
async function checkConnection() {
  try {
    const result = await checkHealth()
    isConnected.value = result.status === 'ok'
  } catch (error) {
    isConnected.value = false
  }
}

// 加载手势列表
async function loadGestures() {
  try {
    const result = await getGestures()
    const list = Array.isArray(result) ? result : []
    const normalized = list
      .filter(item => item && item.id)
      .filter(item => item.type !== 'dynamic')
      .map(item => ({
        ...item,
        name: item.name || item.word || item.id,
        description: item.description || '暂无描述'
      }))

    gestures.value = normalized.length > 0 ? normalized : fallbackGestures
    if (!selectedGesture.value || !gestures.value.some(item => item.id === selectedGesture.value.id)) {
      selectedGesture.value = gestures.value[0] || null
    }
  } catch (error) {
    gestures.value = fallbackGestures
    selectedGesture.value = gestures.value[0] || null
    ElMessage.warning('手势列表加载失败，已切换到本地默认列表')
  }
}

// 选择手势
function selectGesture(gesture) {
  selectedGesture.value = gesture
}

// 开始练习
async function startPractice() {
  if (!selectedGesture.value) {
    ElMessage.warning('请先选择一个手势')
    return
  }

  isPracticing.value = true
  currentTarget.value = selectedGesture.value

  // 重置统计
  stats.completed = 0
  stats.correct = 0
  stats.streak = 0

  // 启动摄像头
  await startCamera()
}

// 检查摄像头权限
async function checkCameraPermission() {
  try {
    if (navigator.permissions) {
      const result = await navigator.permissions.query({ name: 'camera' })
      return result.state
    }
    return 'prompt'
  } catch (error) {
    return 'prompt'
  }
}

// 处理摄像头错误
function handleCameraError(error) {
  let message = ''

  if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
    message = '摄像头权限被拒绝。请点击浏览器地址栏左侧的锁图标，允许访问摄像头后刷新页面重试。'
  } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
    message = '未检测到摄像头设备。请确保您的设备有摄像头并已正确连接。'
  } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
    message = '摄像头被其他应用占用。请关闭其他使用摄像头的应用后重试。'
  } else if (error.name === 'SecurityError') {
    message = '安全限制：请使用 HTTPS 或 localhost 访问本页面。'
  } else {
    message = `摄像头访问失败: ${error.message}`
  }

  ElMessage.error(message)
  return message
}

// 启动摄像头
async function startCamera() {
  try {
    // 检查权限状态
    const permissionStatus = await checkCameraPermission()
    if (permissionStatus === 'denied') {
      ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问摄像头')
      endPractice()
      return
    }

    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user'
      }
    })
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
    }
    ElMessage.success('摄像头已启动')
  } catch (error) {
    handleCameraError(error)
    endPractice()
  }
}

// 停止摄像头
function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
}

// 拍照并验证
async function captureAndVerify() {
  if (!videoElement.value || !canvasElement.value) return

  isVerifying.value = true
  lastResult.value = null
  feedback.value = null

  try {
    // 拍照
    const canvas = canvasElement.value
    const video = videoElement.value
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)

    const imageBase64 = canvas.toDataURL('image/jpeg', 0.8)

    // 调用验证API
    const result = await verifyGesture(imageBase64, currentTarget.value.id)

    lastResult.value = result
    stats.completed++

    if (result.correct) {
      stats.correct++
      stats.streak++
      ElMessage.success(result.message || '正确！')
    } else {
      stats.streak = 0
      ElMessage.warning(result.message || '再试试！')
    }

    // 获取AI反馈
    const feedbackResult = await getPracticeFeedback(
      currentTarget.value.id,
      result.correct,
      result.confidence || 0.5
    )
    feedback.value = feedbackResult

    // 如果正确，3秒后清除结果
    if (result.correct) {
      setTimeout(() => {
        lastResult.value = null
      }, 3000)
    }
  } catch (error) {
    ElMessage.error('验证失败：' + error.message)
  } finally {
    isVerifying.value = false
  }
}

// 跳过当前手势
function skipGesture() {
  // 随机选择下一个手势
  const otherGestures = gestures.value.filter(g => g.id !== currentTarget.value.id)
  if (otherGestures.length > 0) {
    const randomIndex = Math.floor(Math.random() * otherGestures.length)
    currentTarget.value = otherGestures[randomIndex]
  }
  lastResult.value = null
  feedback.value = null
}

// 结束练习
function endPractice() {
  isPracticing.value = false
  stopCamera()
  lastResult.value = null
  feedback.value = null

  if (stats.completed > 0) {
    const accuracy = Math.round(stats.correct / stats.completed * 100)
    ElMessage.success(`练习结束！完成 ${stats.completed} 个，准确率 ${accuracy}%`)
  }
}

onMounted(() => {
  checkConnection()
  loadGestures()
})

onUnmounted(() => {
  stopCamera()
})
</script>

<style scoped>
.practice-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mode-selector {
  text-align: center;
  margin-bottom: 24px;
}

.mode-selector h3 {
  margin-bottom: 16px;
  color: #333;
}

.gesture-selector h3 {
  margin-bottom: 16px;
  color: #333;
}

.gesture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.gesture-item {
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.gesture-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.gesture-item.selected {
  border-color: #409eff;
  background: #409eff;
  color: #fff;
}

.gesture-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.gesture-name {
  font-size: 14px;
}

.start-btn {
  width: 100%;
}

.practice-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.target-gesture {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #fff;
}

.target-gesture h3 {
  margin-bottom: 12px;
}

.target-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.target-icon {
  font-size: 48px;
}

.target-name {
  font-size: 24px;
  font-weight: bold;
}

.target-desc {
  margin-top: 8px;
  opacity: 0.9;
}

.camera-area {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
}

.camera-area video {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  transform: scaleX(-1);
}

.result-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.result-badge {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 24px;
  font-weight: bold;
  animation: fadeIn 0.3s ease;
}

.result-badge.correct {
  background: rgba(103, 194, 58, 0.9);
  color: #fff;
}

.result-badge.incorrect {
  background: rgba(245, 108, 108, 0.9);
  color: #fff;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

.control-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.feedback-area {
  margin-top: 12px;
}

.feedback-details {
  margin-top: 8px;
}

.stars {
  font-size: 20px;
}

.stars span {
  opacity: 0.3;
}

.stars span.active {
  opacity: 1;
}

.tip {
  margin-top: 8px;
  color: #666;
}

.practice-stats {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
}
</style>
