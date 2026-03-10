<template>
  <div class="gesture-recognition">
    <el-card class="recognition-card">
      <template #header>
        <div class="card-header">
          <h2>实时手势识别</h2>
          <div class="header-right">
            <el-tag :type="connectionStatus.type" size="small" effect="dark">
              {{ connectionStatus.text }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- 主要内容区域 -->
      <div class="main-content">
        <!-- 摄像头区域 -->
        <div class="camera-section">
          <div class="camera-container" :class="{ active: isRecognizing, 'has-result': recognitionResult }">
            <!-- 装饰边框 -->
            <div class="corner-decoration top-left"></div>
            <div class="corner-decoration top-right"></div>
            <div class="corner-decoration bottom-left"></div>
            <div class="corner-decoration bottom-right"></div>

            <!-- 扫描线动画 -->
            <div class="scan-line" v-if="isRecognizing"></div>

            <video
              ref="videoElement"
              autoplay
              playsinline
              class="camera-video"
            ></video>
            <canvas ref="canvasElement" style="display: none;"></canvas>

            <!-- 识别结果覆盖层 -->
            <transition name="result-fade">
              <div class="result-overlay" v-if="recognitionResult && isRecognizing">
                <div class="result-badge" :class="getConfidenceClass(recognitionResult.confidence)">
                  <span class="gesture-emoji">{{ getGestureIcon(recognitionResult.gesture) }}</span>
                  <div class="result-info">
                    <span class="gesture-name">{{ recognitionResult.name }}</span>
                    <div class="confidence-bar">
                      <div class="confidence-fill" :style="{ width: (recognitionResult.confidence * 100) + '%' }"></div>
                    </div>
                    <span class="confidence-text">{{ Math.round(recognitionResult.confidence * 100) }}%</span>
                  </div>
                </div>
              </div>
            </transition>

            <!-- 手部检测状态 -->
            <div class="detection-status" v-if="isRecognizing">
              <div class="status-dot" :class="{ detected: recognitionResult && recognitionResult.gesture !== 'no_hand' }"></div>
              <span>{{ recognitionResult && recognitionResult.gesture !== 'no_hand' ? '检测到手部' : '请将手放入画面' }}</span>
            </div>

            <!-- 加载状态 -->
            <div class="loading-overlay" v-if="isLoading">
              <div class="loading-spinner"></div>
              <p>正在启动摄像头...</p>
            </div>

            <!-- 未启动状态 -->
            <div class="idle-overlay" v-if="!isRecognizing && !isLoading">
              <div class="idle-icon">📷</div>
              <p>点击下方按钮开始识别</p>
            </div>
          </div>

          <!-- 控制按钮 -->
          <div class="control-buttons">
            <el-button
              :type="isRecognizing ? 'danger' : 'primary'"
              size="large"
              @click="toggleRecognition"
              :loading="isLoading"
              class="main-button"
            >
              <span class="button-icon">{{ isRecognizing ? '⏹️' : '▶️' }}</span>
              {{ isRecognizing ? '停止识别' : '开始识别' }}
            </el-button>

            <el-button-group class="secondary-buttons">
              <el-button @click="captureOnce" :disabled="!isRecognizing" title="单次识别">
                📸
              </el-button>
              <el-button @click="toggleSound" :type="soundEnabled ? 'primary' : 'default'" title="声音反馈">
                {{ soundEnabled ? '🔊' : '🔇' }}
              </el-button>
              <el-button @click="clearHistory" title="清空历史">
                🗑️
              </el-button>
            </el-button-group>
          </div>
        </div>

        <!-- 右侧信息面板 -->
        <div class="info-section">
          <!-- 当前识别结果 -->
          <div class="current-result" v-if="recognitionResult">
            <h3>当前识别</h3>
            <div class="result-card" :class="getConfidenceClass(recognitionResult.confidence)">
              <div class="result-icon">{{ getGestureIcon(recognitionResult.gesture) }}</div>
              <div class="result-details">
                <div class="result-name">{{ recognitionResult.name }}</div>
                <el-progress
                  :percentage="Math.round(recognitionResult.confidence * 100)"
                  :color="getProgressColor(recognitionResult.confidence)"
                  :stroke-width="12"
                />
              </div>
            </div>

            <!-- 手指状态可视化 -->
            <div class="finger-visual" v-if="recognitionResult.finger_states">
              <h4>手指状态</h4>
              <div class="fingers-container">
                <div
                  v-for="(state, index) in recognitionResult.finger_states"
                  :key="index"
                  :class="['finger-item', { active: state }]"
                >
                  <div class="finger-icon">{{ fingerIcons[index] }}</div>
                  <div class="finger-name">{{ fingerNames[index] }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 识别历史 -->
          <div class="history-section">
            <h3>识别历史 <span class="history-count">({{ gestureHistory.length }})</span></h3>
            <div class="history-list">
              <transition-group name="history-item">
                <div
                  v-for="(item, index) in gestureHistory"
                  :key="item.id"
                  class="history-item"
                >
                  <span class="history-icon">{{ getGestureIcon(item.gesture) }}</span>
                  <span class="history-name">{{ item.name }}</span>
                  <span class="history-time">{{ item.time }}</span>
                </div>
              </transition-group>
              <div v-if="gestureHistory.length === 0" class="empty-history">
                暂无识别记录
              </div>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="stats-section">
            <h3>统计</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">总识别</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.unique }}</div>
                <div class="stat-label">不同手势</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ mostFrequent }}</div>
                <div class="stat-label">最常见</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        :closable="true"
        @close="errorMessage = ''"
        class="error-alert"
      />

      <!-- 支持的手势 -->
      <div class="supported-gestures">
        <h4>支持的手势</h4>
        <div class="gesture-tags">
          <el-tag v-for="g in supportedGestures" :key="g.id" size="small" effect="plain">
            {{ g.icon }} {{ g.name }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { recognizeGesture, checkHealth } from '../api/gestureApi.js'

export default {
  name: 'OptimizedGestureRecognition',
  data() {
    return {
      isRecognizing: false,
      isLoading: false,
      recognitionResult: null,
      errorMessage: '',
      isConnected: false,
      mediaStream: null,
      recognitionInterval: null,
      soundEnabled: true,
      gestureHistory: [],
      historyIdCounter: 0,
      stats: {
        total: 0,
        unique: 0,
        gestureCounts: {}
      },
      fingerNames: ['拇指', '食指', '中指', '无名指', '小指'],
      fingerIcons: ['👍', '👆', '🖕', '💍', '🤙'],
      supportedGestures: [
        { id: 'zero', name: '零/拳头', icon: '✊' },
        { id: 'one', name: '一', icon: '☝️' },
        { id: 'two', name: '二', icon: '✌️' },
        { id: 'three', name: '三', icon: '🤟' },
        { id: 'four', name: '四', icon: '🖖' },
        { id: 'five', name: '五', icon: '🖐️' },
        { id: 'thumbs_up', name: '点赞', icon: '👍' },
        { id: 'ok', name: 'OK', icon: '👌' },
        { id: 'i_love_you', name: '我爱你', icon: '🤟' },
        { id: 'rock', name: '摇滚', icon: '🤘' }
      ],
      lastGesture: null
    }
  },

  computed: {
    connectionStatus() {
      if (this.isConnected) {
        return { type: 'success', text: 'API已连接' }
      }
      return { type: 'danger', text: 'API未连接' }
    },
    mostFrequent() {
      if (Object.keys(this.stats.gestureCounts).length === 0) return '-'
      const sorted = Object.entries(this.stats.gestureCounts).sort((a, b) => b[1] - a[1])
      return sorted[0] ? this.getGestureIcon(sorted[0][0]) : '-'
    }
  },

  async mounted() {
    await this.checkConnection()
  },

  beforeUnmount() {
    this.stopRecognition()
  },

  methods: {
    async checkConnection() {
      try {
        const result = await checkHealth()
        this.isConnected = result.status === 'ok'
      } catch (error) {
        this.isConnected = false
      }
    },

    getGestureIcon(gesture) {
      const icons = {
        zero: '✊', one: '☝️', two: '✌️', three: '🤟', four: '🖖',
        five: '🖐️', six: '🤙', seven: '🤞', eight: '👌', nine: '👆',
        thumbs_up: '👍', ok: '👌', i_love_you: '🤟', rock: '🤘', no_hand: '❓'
      }
      return icons[gesture] || '✋'
    },

    getProgressColor(confidence) {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    },

    getConfidenceClass(confidence) {
      if (confidence >= 0.8) return 'high-confidence'
      if (confidence >= 0.6) return 'medium-confidence'
      return 'low-confidence'
    },

    async toggleRecognition() {
      if (this.isRecognizing) {
        this.stopRecognition()
      } else {
        await this.startRecognition()
      }
    },

    async startRecognition() {
      this.isLoading = true
      this.errorMessage = ''

      try {
        await this.checkConnection()
        if (!this.isConnected) {
          this.errorMessage = '后端API未连接，请确保 Python 服务器已启动'
          return
        }

        this.mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
        })

        const videoElement = this.$refs.videoElement
        videoElement.srcObject = this.mediaStream
        await videoElement.play()

        this.isRecognizing = true
        this.playSound('start')

        // 每300ms识别一次，更流畅
        this.recognitionInterval = setInterval(() => {
          this.captureAndRecognize()
        }, 300)

      } catch (error) {
        this.handleCameraError(error)
      } finally {
        this.isLoading = false
      }
    },

    stopRecognition() {
      this.isRecognizing = false
      this.playSound('stop')

      if (this.recognitionInterval) {
        clearInterval(this.recognitionInterval)
        this.recognitionInterval = null
      }

      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop())
        this.mediaStream = null
      }

      const videoElement = this.$refs.videoElement
      if (videoElement) {
        videoElement.srcObject = null
      }
    },

    async captureOnce() {
      await this.captureAndRecognize()
    },

    async captureAndRecognize() {
      if (!this.isRecognizing) return

      const videoElement = this.$refs.videoElement
      const canvasElement = this.$refs.canvasElement

      if (!videoElement || !canvasElement) return

      try {
        const canvas = canvasElement
        canvas.width = videoElement.videoWidth || 640
        canvas.height = videoElement.videoHeight || 480
        const ctx = canvas.getContext('2d')
        ctx.drawImage(videoElement, 0, 0)

        const imageBase64 = canvas.toDataURL('image/jpeg', 0.8)
        const result = await recognizeGesture(imageBase64)

        if (result && !result.error) {
          this.recognitionResult = result

          // 检测到新手势时播放声音并记录
          if (result.gesture !== 'no_hand' && result.gesture !== this.lastGesture) {
            this.lastGesture = result.gesture
            this.playSound('detect')
            this.addToHistory(result)
          }
        }
      } catch (error) {
        console.error('识别错误:', error)
      }
    },

    addToHistory(result) {
      const now = new Date()
      const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`

      this.gestureHistory.unshift({
        id: ++this.historyIdCounter,
        gesture: result.gesture,
        name: result.name,
        time: timeStr
      })

      // 保留最近20条
      if (this.gestureHistory.length > 20) {
        this.gestureHistory.pop()
      }

      // 更新统计
      this.stats.total++
      if (!this.stats.gestureCounts[result.gesture]) {
        this.stats.gestureCounts[result.gesture] = 0
        this.stats.unique++
      }
      this.stats.gestureCounts[result.gesture]++
    },

    clearHistory() {
      this.gestureHistory = []
      this.stats = { total: 0, unique: 0, gestureCounts: {} }
      this.$message.success('历史已清空')
    },

    toggleSound() {
      this.soundEnabled = !this.soundEnabled
      this.$message.info(this.soundEnabled ? '声音已开启' : '声音已关闭')
    },

    playSound(type) {
      if (!this.soundEnabled) return

      // 使用Web Audio API播放简单音效
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)()
        const oscillator = audioContext.createOscillator()
        const gainNode = audioContext.createGain()

        oscillator.connect(gainNode)
        gainNode.connect(audioContext.destination)

        const frequencies = { start: 523, stop: 392, detect: 659 }
        oscillator.frequency.value = frequencies[type] || 440
        oscillator.type = 'sine'

        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1)

        oscillator.start(audioContext.currentTime)
        oscillator.stop(audioContext.currentTime + 0.1)
      } catch (e) {
        // 忽略音频错误
      }
    },

    handleCameraError(error) {
      let message = ''
      if (error.name === 'NotAllowedError') {
        message = '摄像头权限被拒绝，请点击地址栏锁图标允许访问摄像头'
      } else if (error.name === 'NotFoundError') {
        message = '未检测到摄像头设备'
      } else if (error.name === 'NotReadableError') {
        message = '摄像头被其他应用占用'
      } else {
        message = `摄像头错误: ${error.message}`
      }
      this.errorMessage = message
      this.$message.error(message)
    }
  }
}
</script>

<style scoped>
.gesture-recognition {
  height: 100%;
}

.recognition-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 1.3em;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

/* 摄像头区域 */
.camera-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.camera-container.active {
  box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.5), 0 10px 40px rgba(0, 0, 0, 0.3);
}

.camera-container.has-result {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.5), 0 10px 40px rgba(0, 0, 0, 0.3);
}

/* 角落装饰 */
.corner-decoration {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 3px solid rgba(103, 194, 58, 0.7);
  z-index: 10;
  pointer-events: none;
}

.corner-decoration.top-left {
  top: 10px;
  left: 10px;
  border-right: none;
  border-bottom: none;
}

.corner-decoration.top-right {
  top: 10px;
  right: 10px;
  border-left: none;
  border-bottom: none;
}

.corner-decoration.bottom-left {
  bottom: 10px;
  left: 10px;
  border-right: none;
  border-top: none;
}

.corner-decoration.bottom-right {
  bottom: 10px;
  right: 10px;
  border-left: none;
  border-top: none;
}

/* 扫描线动画 */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #67C23A, transparent);
  animation: scan 2s linear infinite;
  z-index: 5;
}

@keyframes scan {
  0% { top: 0; opacity: 1; }
  50% { opacity: 0.5; }
  100% { top: 100%; opacity: 1; }
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

/* 识别结果覆盖层 */
.result-overlay {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  z-index: 20;
}

.result-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 12px 18px;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.result-badge.high-confidence {
  border-color: #67C23A;
  box-shadow: 0 0 20px rgba(103, 194, 58, 0.3);
}

.result-badge.medium-confidence {
  border-color: #E6A23C;
  box-shadow: 0 0 20px rgba(230, 162, 60, 0.3);
}

.result-badge.low-confidence {
  border-color: #F56C6C;
}

.gesture-emoji {
  font-size: 2.5em;
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.result-info {
  flex: 1;
}

.gesture-name {
  display: block;
  font-size: 1.2em;
  font-weight: bold;
  color: #fff;
  margin-bottom: 6px;
}

.confidence-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #67C23A, #95d475);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.confidence-text {
  font-size: 0.9em;
  color: rgba(255, 255, 255, 0.8);
}

/* 检测状态 */
.detection-status {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 16px;
  border-radius: 20px;
  color: #fff;
  font-size: 0.9em;
  z-index: 15;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #F56C6C;
  animation: pulse 1.5s infinite;
}

.status-dot.detected {
  background: #67C23A;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 加载和空闲状态 */
.loading-overlay, .idle-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  z-index: 25;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #67C23A;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.idle-overlay .idle-icon {
  font-size: 4em;
  margin-bottom: 15px;
  opacity: 0.7;
}

/* 控制按钮 */
.control-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
}

.main-button {
  min-width: 160px;
  height: 48px;
  font-size: 1.1em;
  border-radius: 24px;
}

.button-icon {
  margin-right: 8px;
}

.secondary-buttons .el-button {
  font-size: 1.2em;
  padding: 10px 14px;
}

/* 右侧信息面板 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-section h3 {
  margin: 0 0 10px 0;
  font-size: 1em;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 5px;
}

.history-count {
  font-weight: normal;
  color: #909399;
}

/* 当前结果卡片 */
.result-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #fff;
}

.result-icon {
  font-size: 3em;
}

.result-details {
  flex: 1;
}

.result-name {
  font-size: 1.3em;
  font-weight: bold;
  margin-bottom: 8px;
}

/* 手指状态 */
.finger-visual {
  margin-top: 12px;
}

.finger-visual h4 {
  margin: 0 0 8px 0;
  font-size: 0.9em;
  color: #606266;
}

.fingers-container {
  display: flex;
  gap: 8px;
}

.finger-item {
  flex: 1;
  text-align: center;
  padding: 8px 4px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.finger-item.active {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.finger-icon {
  font-size: 1.5em;
}

.finger-name {
  font-size: 0.75em;
  margin-top: 4px;
}

/* 历史记录 */
.history-section {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #fff;
  border-radius: 8px;
  font-size: 0.9em;
}

.history-icon {
  font-size: 1.3em;
}

.history-name {
  flex: 1;
  color: #303133;
}

.history-time {
  color: #909399;
  font-size: 0.85em;
}

.empty-history {
  text-align: center;
  color: #909399;
  padding: 20px;
}

/* 历史动画 */
.history-item-enter-active {
  transition: all 0.3s ease;
}

.history-item-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

/* 统计 */
.stats-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 12px;
  padding: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.stat-item {
  text-align: center;
  padding: 10px;
  background: #fff;
  border-radius: 8px;
}

.stat-value {
  font-size: 1.5em;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 0.8em;
  color: #909399;
  margin-top: 4px;
}

/* 错误提示 */
.error-alert {
  margin-top: 15px;
}

/* 支持的手势 */
.supported-gestures {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.supported-gestures h4 {
  margin: 0 0 10px 0;
  font-size: 0.95em;
  color: #606266;
}

.gesture-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 动画 */
.result-fade-enter-active, .result-fade-leave-active {
  transition: all 0.3s ease;
}

.result-fade-enter-from, .result-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
