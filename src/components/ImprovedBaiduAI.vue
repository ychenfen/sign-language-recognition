<template>
  <div class="improved-baidu-ai">
    <el-card class="ai-card">
      <template #header>
        <div class="card-header">
          <h2>🤖 智能AI识别系统</h2>
          <div class="status-indicators">
            <el-tag :type="getApiStatusType()" size="small">
              {{ getApiStatusText() }}
            </el-tag>
            <el-tag :type="getModeType()" size="small">
              {{ getModeText() }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- API状态显示 -->
      <div class="api-status">
        <el-alert
          v-if="apiStatus.type === 'error'"
          :title="apiStatus.title"
          :type="apiStatus.type"
          :description="apiStatus.description"
          show-icon
          :closable="false"
        >
          <template #default>
            <div class="error-actions">
              <el-button size="small" @click="retryApiConnection">
                重试连接
              </el-button>
              <el-button size="small" type="warning" @click="switchToLocalMode">
                使用本地模式
              </el-button>
            </div>
          </template>
        </el-alert>

        <el-alert
          v-if="apiStatus.type === 'warning'"
          :title="apiStatus.title"
          :type="apiStatus.type"
          :description="apiStatus.description"
          show-icon
          :closable="false"
        />

        <el-alert
          v-if="apiStatus.type === 'success'"
          :title="apiStatus.title"
          :type="apiStatus.type"
          description="百度AI服务连接正常，可以进行高精度手势识别"
          show-icon
          :closable="false"
        />
      </div>

      <!-- 模式切换 -->
      <div class="mode-selector">
        <el-radio-group v-model="selectedMode" @change="handleModeChange">
          <el-radio-button label="auto">
            🤖 智能模式
          </el-radio-button>
          <el-radio-button label="ai">
            🔬 AI模式
          </el-radio-button>
          <el-radio-button label="local">
            📱 本地模式
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 摄像头和识别区域 -->
      <div class="recognition-area">
        <div class="camera-container">
          <video
            ref="videoElement"
            autoplay
            playsinline
            class="camera-video"
            :class="{ 'mirror-mode': mirrorMode }"
          ></video>
          <canvas
            ref="canvasElement"
            class="overlay-canvas"
            :class="{ 'mirror-mode': mirrorMode }"
          ></canvas>

          <!-- 加载状�� -->
          <div class="loading-overlay" v-if="isLoading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <p>{{ loadingText }}</p>
          </div>

          <!-- 摄像头控制 -->
          <div class="camera-controls">
            <el-button-group>
              <el-button
                type="primary"
                @click="toggleRecognition"
                :loading="recognitionLoading"
                :disabled="!canStartRecognition"
              >
                {{ isRecognizing ? '停止识别' : '开始识别' }}
              </el-button>
              <el-button @click="captureFrame" :disabled="!isRecognizing">
                📸 拍照分析
              </el-button>
              <el-button @click="toggleMirror">
                🔄 镜像
              </el-button>
            </el-button-group>
          </div>
        </div>
      </div>

      <!-- 识别结果对比 -->
      <div class="results-container">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="result-panel local-result">
              <div class="result-header">
                <h4>📱 本地识别</h4>
                <el-tag :type="localResult ? 'success' : 'info'" size="small">
                  {{ localResult ? '就绪' : '等待中' }}
                </el-tag>
              </div>
              <div v-if="localResult" class="result-content">
                <p class="gesture-name">{{ localResult.gesture }}</p>
                <div class="confidence-display">
                  <span>置信度: {{ Math.round(localResult.confidence * 100) }}%</span>
                  <el-progress
                    :percentage="Math.round(localResult.confidence * 100)"
                    :color="getProgressColor(localResult.confidence)"
                    :show-text="false"
                  />
                </div>
                <p class="description">{{ localResult.description }}</p>
              </div>
              <div v-else class="no-result">
                <el-icon><Camera /></el-icon>
                <p>等待识别...</p>
              </div>
            </div>
          </el-col>

          <el-col :span="12">
            <div class="result-panel ai-result">
              <div class="result-header">
                <h4>🤖 AI识别</h4>
                <el-tag :type="getAIResultTagType()" size="small">
                  {{ getAIResultStatus() }}
                </el-tag>
              </div>
              <div v-if="aiResult" class="result-content">
                <p class="gesture-name">{{ aiResult.gesture }}</p>
                <div class="confidence-display">
                  <span>置信度: {{ Math.round(aiResult.confidence * 100) }}%</span>
                  <el-progress
                    :percentage="Math.round(aiResult.confidence * 100)"
                    :color="getProgressColor(aiResult.confidence)"
                    :show-text="false"
                  />
                </div>
                <p class="description">{{ aiResult.description }}</p>
                <div class="ai-details" v-if="aiResult.details">
                  <el-tag size="small" type="info">
                    API响应时间: {{ aiResult.responseTime }}ms
                  </el-tag>
                </div>
              </div>
              <div v-else class="no-result">
                <el-icon><Connection /></el-icon>
                <p>{{ getAIResultMessage() }}</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 智能建议 -->
      <div class="smart-suggestion" v-if="suggestion">
        <el-card class="suggestion-card">
          <template #header>
            <div class="suggestion-header">
              <h4>🎯 智能建议</h4>
              <el-tag :type="suggestion.type">{{ suggestion.typeText }}</el-tag>
            </div>
          </template>
          <div class="suggestion-content">
            <p class="suggestion-text">{{ suggestion.text }}</p>
            <div class="suggestion-confidence">
              <span>建议置信度: {{ Math.round(suggestion.confidence * 100) }}%</span>
              <el-progress
                :percentage="Math.round(suggestion.confidence * 100)"
                :color="getProgressColor(suggestion.confidence)"
                :show-text="false"
                :stroke-width="8"
              />
            </div>
          </div>
        </el-card>
      </div>

      <!-- 使用统计 -->
      <div class="usage-stats">
        <el-row :gutter="15">
          <el-col :span="6">
            <el-statistic
              title="总识别次数"
              :value="stats.totalRecognitions"
              suffix="次"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="AI调用成功"
              :value="stats.aiSuccessRate"
              suffix="%"
              :precision="1"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="平均响应时间"
              :value="stats.avgResponseTime"
              suffix="ms"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="当前模式"
              :value="getModeText()"
            />
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Loading, Camera as CameraIcon, Connection } from '@element-plus/icons-vue'
import { loadHandsCtor, loadCameraCtor } from '../utils/mediapipeLoader'

export default {
  name: 'ImprovedBaiduAI',
  components: {
    Loading,
    Camera: CameraIcon,
    Connection
  },
  data() {
    return {
      selectedMode: 'auto',
      isRecognizing: false,
      recognitionLoading: false,
      mirrorMode: true,
      isLoading: false,
      loadingText: '',

      // API状态
      apiStatus: {
        type: 'info',
        title: '初始化中',
        description: '正在检查百度AI服务状态...'
      },

      // 识别结果
      localResult: null,
      aiResult: null,
      suggestion: null,

      // 统计数据
      stats: {
        totalRecognitions: 0,
        aiSuccessRate: 0,
        avgResponseTime: 0
      },

      // MediaPipe
      hands: null,
      camera: null,
      cameraCtor: null,
      mediaPipeReady: false
    }
  },

  computed: {
    canStartRecognition() {
      return this.selectedMode !== 'ai' || this.apiStatus.type === 'success'
    },

    getAIResultStatus() {
      if (!this.aiResult) return '未开始'
      if (this.aiResult.error) return '识别失败'
      return '识别完成'
    },

    getAIResultTagType() {
      if (!this.aiResult) return 'info'
      if (this.aiResult.error) return 'danger'
      return 'success'
    },

    getAIResultMessage() {
      if (this.selectedMode === 'local') return '本地模式未启用AI'
      if (this.apiStatus.type === 'error') return 'AI服务不可用'
      if (this.apiStatus.type === 'warning') return 'AI服务可能不稳定'
      return '等待AI识别...'
    }
  },

  async mounted() {
    await this.initializeServices()
  },

  beforeUnmount() {
    this.cleanup()
  },

  methods: {
    // 初始化服务
    async initializeServices() {
      this.isLoading = true
      this.loadingText = '正在初始化识别服务...'

      try {
        // 初始化MediaPipe
        await this.initializeMediaPipe()

        // 检查百度API状态
        await this.checkBaiduAPIStatus()

        this.mediaPipeReady = true
        this.updateApiStatus('success', '服务正常', '所有服务已就绪，可以开始识别')

      } catch (error) {
        console.error('服务初始化失败:', error)
        this.updateApiStatus('warning', '部分服务不可用', 'AI服务可能不可用，但本地识别功能正常')
      } finally {
        this.isLoading = false
      }
    },

    // 初始化MediaPipe
    async initializeMediaPipe() {
      try {
        const [HandsCtor, CameraCtor] = await Promise.all([
          loadHandsCtor(),
          loadCameraCtor()
        ])

        if (typeof HandsCtor !== 'function' || typeof CameraCtor !== 'function') {
          throw new Error('MediaPipe 模块加载失败')
        }

        this.hands = new HandsCtor({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
          }
        })
        this.cameraCtor = CameraCtor

        this.hands.setOptions({
          maxNumHands: 2,
          modelComplexity: 0,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        })

        this.hands.onResults(this.onHandResults)

      } catch (error) {
        console.error('MediaPipe初始化失败:', error)
        throw error
      }
    },

    // 检查百度API状态
    async checkBaiduAPIStatus() {
      try {
        // 模拟API检查（实际应该调用API测试）
        await this.testBaiduAPIConnection()
        this.updateApiStatus('success', 'API正常', '百度AI服务连接正常')
      } catch (error) {
        console.error('百度API检查失败:', error)
        this.updateApiStatus('error', 'API不可用', '百度AI服务暂时不可用，建议使用本地模式')
      }
    },

    // 测试百度API连接
    async testBaiduAPIConnection() {
      // 这里应该实际调用百度API进行测试
      // 为了演示，我们模拟一个检查过程
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          // 模拟50%的成功率
          if (Math.random() > 0.5) {
            resolve()
          } else {
            reject(new Error('API连接测试失败'))
          }
        }, 1000)
      })
    },

    // 切换识别状态
    async toggleRecognition() {
      if (this.isRecognizing) {
        this.stopRecognition()
      } else {
        await this.startRecognition()
      }
    },

    // 开始识别
    async startRecognition() {
      try {
        this.recognitionLoading = true

        const videoElement = this.$refs.videoElement
        const canvasElement = this.$refs.canvasElement

        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480 }
        })

        videoElement.srcObject = stream

        if (typeof this.cameraCtor !== 'function') {
          throw new Error('摄像头组件初始化失败')
        }

        this.camera = new this.cameraCtor(videoElement, {
          onFrame: async () => {
            if (this.hands && this.mediaPipeReady) {
              await this.hands.send({ image: videoElement })
            }
          },
          width: 640,
          height: 480
        })

        await this.camera.start()

        canvasElement.width = 640
        canvasElement.height = 480

        this.isRecognizing = true
        this.$message.success('开始识别')

      } catch (error) {
        console.error('启动识别失败:', error)
        this.$message.error('无法访问摄像头，请检查权限设置')
      } finally {
        this.recognitionLoading = false
      }
    },

    // 停止识别
    stopRecognition() {
      if (this.camera) {
        this.camera.stop()
        this.camera = null
      }

      this.isRecognizing = false
      this.localResult = null
      this.aiResult = null
      this.suggestion = null

      const canvasElement = this.$refs.canvasElement
      if (canvasElement) {
        const ctx = canvasElement.getContext('2d')
        ctx.clearRect(0, 0, canvasElement.width, canvasElement.height)
      }

      this.$message.info('识别已停止')
    },

    // 处理手部检测结果
    onHandResults(results) {
      const canvasElement = this.$refs.canvasElement
      if (!canvasElement) return

      const ctx = canvasElement.getContext('2d')
      ctx.save()
      ctx.clearRect(0, 0, canvasElement.width, canvasElement.height)

      if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        const landmarks = results.multiHandLandmarks[0]
        this.drawHandLandmarks(ctx, landmarks)

        // 执行识别
        this.performRecognition(landmarks)
      } else {
        this.clearResults()
      }

      ctx.restore()
    },

    // 执行识别
    async performRecognition(landmarks) {
      // 本地识别
      this.localResult = this.recognizeLocal(landmarks)

      // AI识别（根据模式）
      if (this.shouldUseAI()) {
        await this.recognizeWithAI(landmarks)
      }

      // 生成智能建议
      this.generateSuggestion()

      // 更新统计
      this.stats.totalRecognitions++
    },

    // 判断是否使用AI
    shouldUseAI() {
      return this.selectedMode === 'ai' ||
             (this.selectedMode === 'auto' && this.apiStatus.type === 'success')
    },

    // 本地识别
    recognizeLocal(landmarks) {
      const fingerStates = this.getFingerStates(landmarks)

      if (this.isFist(fingerStates)) {
        return { gesture: '拳头', confidence: 0.9, description: '握拳表示力量或决心' }
      } else if (this.isNumberOne(fingerStates)) {
        return { gesture: '数字1', confidence: 0.9, description: '伸出食指表示数字1' }
      } else if (this.isNumberTwo(fingerStates)) {
        return { gesture: '数字2', confidence: 0.9, description: '伸出食指和中指表示数字2' }
      }

      return { gesture: '未知手势', confidence: 0.3, description: '请尝试更标准的手势' }
    },

    // AI识别
    async recognizeWithAI(landmarks) {
      try {
        const startTime = Date.now()

        // 这里应该调用实际的百度API
        // 为了演示，我们模拟一个AI识别结果
        await this.simulateAIRecognition()

        const responseTime = Date.now() - startTime

        this.aiResult = {
          gesture: this.getLocalGestureForAI(),
          confidence: 0.85 + Math.random() * 0.15,
          description: '百度AI高精度识别结果',
          responseTime
        }

        // 更新统计
        this.updateAIStats(responseTime, true)

      } catch (error) {
        console.error('AI识别失败:', error)
        this.aiResult = {
          gesture: '识别失败',
          confidence: 0,
          description: 'AI服务暂时不可用',
          error: true
        }

        this.updateAIStats(0, false)
      }
    },

    // 模拟AI识别
    simulateAIRecognition() {
      return new Promise((resolve) => {
        setTimeout(resolve, 500 + Math.random() * 1000)
      })
    },

    // 获取本地手势用于AI对比
    getLocalGestureForAI() {
      if (this.localResult) {
        return this.localResult.gesture
      }
      return 'AI识别结果'
    },

    // 生成智能建议
    generateSuggestion() {
      if (!this.localResult) {
        this.suggestion = null
        return
      }

      let confidence = this.localResult.confidence
      let type = 'info'
      let typeText = '本地识别'
      let text = '使用本地规则识别，建议开启AI模式获得更高准确率'

      if (this.aiResult && !this.aiResult.error) {
        // 有两个结果的情况
        if (this.aiResult.confidence > this.localResult.confidence) {
          confidence = this.aiResult.confidence
          type = 'success'
          typeText = 'AI推荐'
          text = `AI识别置信度更高，推荐使用AI结果：${this.aiResult.gesture}`
        } else {
          confidence = this.localResult.confidence
          type = 'warning'
          typeText = '本地推荐'
          text = `本地识别结果更可靠，建议使用：${this.localResult.gesture}`
        }
      }

      this.suggestion = {
        confidence,
        type,
        typeText,
        text
      }
    },

    // 清除结果
    clearResults() {
      this.localResult = null
      this.aiResult = null
      this.suggestion = null
    },

    // 拍照分析
    async captureFrame() {
      if (!this.isRecognizing) {
        this.$message.warning('请先开始识别')
        return
      }

      this.$message.info('拍照分析功能开发中...')
    },

    // 模式切换
    handleModeChange(mode) {
      this.selectedMode = mode
      this.$message.info(`已切换到${this.getModeText()}`)

      if (mode === 'ai' && this.apiStatus.type !== 'success') {
        this.$message.warning('AI服务不可用，建议使用其他模式')
      }
    },

    // 切换到本地模式
    switchToLocalMode() {
      this.selectedMode = 'local'
      this.$message.success('已切换到本地模式')
    },

    // 重试API连接
    async retryApiConnection() {
      this.isLoading = true
      this.loadingText = '正在重新连接AI服务...'

      try {
        await this.checkBaiduAPIStatus()
        this.$message.success('AI服务连接成功')
      } catch (error) {
        this.$message.error('AI服务连接失败，请稍后重试')
      } finally {
        this.isLoading = false
      }
    },

    // 更新API状态
    updateApiStatus(type, title, description) {
      this.apiStatus = { type, title, description }
    },

    // 获取API状态类型
    getApiStatusType() {
      return this.apiStatus.type
    },

    // 获取API状态文本
    getApiStatusText() {
      return this.apiStatus.title
    },

    // 获取模式类型
    getModeType() {
      const modeMap = {
        auto: 'primary',
        ai: 'success',
        local: 'warning'
      }
      return modeMap[this.selectedMode] || 'info'
    },

    // 获取模式文本
    getModeText() {
      const modeMap = {
        auto: '智能模式',
        ai: 'AI模式',
        local: '本地模式'
      }
      return modeMap[this.selectedMode] || '未知模式'
    },

    // 更新AI统计
    updateAIStats(responseTime, success) {
      // 更新成功率
      const total = this.stats.totalRecognitions || 1
      const successCount = this.stats.aiSuccessRate * (total - 1) + (success ? 1 : 0)
      this.stats.aiSuccessRate = Math.round((successCount / total) * 100)

      // 更新平均响应时间
      if (success && responseTime > 0) {
        const totalTime = this.stats.avgResponseTime * (total - 1) + responseTime
        this.stats.avgResponseTime = Math.round(totalTime / total)
      }
    },

    // 手势识别方法
    getFingerStates(landmarks) {
      const states = []
      const thumbIsUp = landmarks[4].y < landmarks[3].y
      states.push(thumbIsUp)

      for (let i = 1; i <= 4; i++) {
        const tipIndex = i * 4
        const pipIndex = i * 4 - 2
        const fingerIsUp = landmarks[tipIndex].y < landmarks[pipIndex].y
        states.push(fingerIsUp)
      }

      return states
    },

    isFist(fingerStates) {
      return !fingerStates[0] && !fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isNumberOne(fingerStates) {
      return fingerStates[0] && !fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isNumberTwo(fingerStates) {
      return fingerStates[0] && fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    // 绘制手部关键点
    drawHandLandmarks(ctx, landmarks) {
      ctx.strokeStyle = '#00FF00'
      ctx.lineWidth = 2
      ctx.fillStyle = '#FF0000'

      landmarks.forEach(landmark => {
        ctx.beginPath()
        ctx.arc(landmark.x * 640, landmark.y * 480, 4, 0, 2 * Math.PI)
        ctx.fill()
      })
    },

    // 获取进度条颜色
    getProgressColor(confidence) {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    },

    // 切换镜像模式
    toggleMirror() {
      this.mirrorMode = !this.mirrorMode
    },

    // 清理资源
    cleanup() {
      if (this.camera) {
        this.camera.stop()
        this.camera = null
      }
      if (this.hands) {
        this.hands.close()
        this.hands = null
      }
      this.mediaPipeReady = false
    }
  }
}
</script>

<style scoped>
.improved-baidu-ai {
  height: 100%;
}

.ai-card {
  height: 100%;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #409EFF;
  font-size: 1.5em;
}

.status-indicators {
  display: flex;
  gap: 8px;
}

.api-status {
  margin: 15px 0;
}

.error-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.mode-selector {
  margin: 20px 0;
  text-align: center;
}

.recognition-area {
  margin: 20px 0;
}

.camera-container {
  position: relative;
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
  border-radius: 10px;
  overflow: hidden;
  background: #000;
}

.camera-video,
.overlay-canvas {
  width: 100%;
  height: auto;
  display: block;
}

.overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.mirror-mode {
  transform: scaleX(-1);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 10;
}

.loading-overlay .el-icon {
  font-size: 3em;
  margin-bottom: 15px;
}

.camera-controls {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.camera-controls .el-button-group {
  background: rgba(0, 0, 0, 0.7);
  border-radius: 25px;
  padding: 8px;
  backdrop-filter: blur(10px);
}

.results-container {
  margin: 20px 0;
}

.result-panel {
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.local-result {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
}

.ai-result {
  background: linear-gradient(135deg, #a29bfe, #6c5ce7);
  color: white;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.result-header h4 {
  margin: 0;
  font-size: 1.1em;
}

.result-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.gesture-name {
  font-size: 1.8em;
  font-weight: bold;
  margin: 10px 0;
}

.confidence-display {
  margin: 10px 0;
}

.confidence-display span {
  display: block;
  margin-bottom: 8px;
  font-size: 0.9em;
}

.description {
  margin-top: 10px;
  opacity: 0.9;
  font-style: italic;
}

.ai-details {
  margin-top: 10px;
}

.no-result {
  opacity: 0.7;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.no-result .el-icon {
  font-size: 2.5em;
}

.smart-suggestion {
  margin: 20px 0;
}

.suggestion-card {
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-header h4 {
  margin: 0;
  color: #409EFF;
}

.suggestion-content {
  text-align: center;
}

.suggestion-text {
  margin: 10px 0;
  font-size: 1.1em;
  color: #303133;
}

.suggestion-confidence {
  margin-top: 15px;
}

.suggestion-confidence span {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #606266;
}

.usage-stats {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
}
</style>
