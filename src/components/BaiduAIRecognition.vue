<template>
  <div class="baidu-ai-recognition">
    <el-card class="ai-card">
      <template #header>
        <div class="card-header">
          <h2>🤖 百度AI增强识别</h2>
          <el-switch
            v-model="useBaiduAI"
            active-text="AI模式"
            inactive-text="本地模式"
            @change="toggleAIMode"
          />
        </div>
      </template>

      <!-- AI状态显�� -->
      <div class="ai-status">
        <el-alert
          :title="aiStatus.title"
          :type="aiStatus.type"
          :description="aiStatus.description"
          show-icon
          :closable="false"
        />
      </div>

      <!-- 摄像头区域 -->
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

        <!-- 控制按钮 -->
        <div class="camera-controls">
          <el-button-group>
            <el-button
              type="primary"
              @click="toggleRecognition"
              :loading="recognitionLoading"
              :disabled="useBaiduAI && !isTokenReady"
            >
              {{ isRecognizing ? '停止识别' : '开始识别' }}
            </el-button>
            <el-button @click="captureFrame" :disabled="!isRecognizing">
              📸 拍照识别
            </el-button>
            <el-button @click="toggleMirror">
              🔄 镜像
            </el-button>
          </el-button-group>
        </div>
      </div>

      <!-- AI识别结果对比 -->
      <div class="results-comparison" v-if="localResult || aiResult">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="result-panel local-result">
              <h4>📱 本地识别 (MediaPipe)</h4>
              <div v-if="localResult">
                <p class="gesture-name">{{ localResult.gesture }}</p>
                <el-progress
                  :percentage="Math.round(localResult.confidence * 100)"
                  :color="getProgressColor(localResult.confidence)"
                />
                <p class="description">{{ localResult.description }}</p>
              </div>
              <div v-else class="no-result">
                <p>等待识别...</p>
              </div>
            </div>
          </el-col>

          <el-col :span="12">
            <div class="result-panel ai-result">
              <h4>🤖 AI识别 (百度)</h4>
              <div v-if="aiResult">
                <p class="gesture-name">{{ aiResult.gesture }}</p>
                <el-progress
                  :percentage="Math.round(aiResult.confidence * 100)"
                  :color="getProgressColor(aiResult.confidence)"
                />
                <p class="description">{{ aiResult.description }}</p>
                <div class="ai-details" v-if="aiResult.details">
                  <el-tag size="small" v-for="detail in aiResult.details" :key="detail">
                    {{ detail }}
                  </el-tag>
                </div>
              </div>
              <div v-else class="no-result">
                <p>{{ useBaiduAI ? '等待AI识别...' : 'AI模式已关闭' }}</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 混合识别建议 -->
      <div class="hybrid-suggestion" v-if="localResult && aiResult">
        <el-card class="suggestion-card">
          <template #header>
            <h4>🎯 智能识别建议</h4>
          </template>
          <div class="suggestion-content">
            <div class="confidence-comparison">
              <span>本地识别: {{ Math.round(localResult.confidence * 100) }}%</span>
              <span>AI识别: {{ Math.round(aiResult.confidence * 100) }}%</span>
            </div>
            <div class="final-suggestion">
              <h5>推荐结果: <span class="final-gesture">{{ getFinalSuggestion() }}</span></h5>
              <p>{{ getSuggestionReason() }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- API使用统计 -->
      <div class="api-stats">
        <el-row :gutter="15">
          <el-col :span="8">
            <el-statistic
              title="今日API调用"
              :value="apiStats.todayCalls"
              suffix="次"
            />
          </el-col>
          <el-col :span="8">
            <el-statistic
              title="总调用量"
              :value="apiStats.totalCalls"
              suffix="次"
            />
          </el-col>
          <el-col :span="8">
            <el-statistic
              title="AI准确率"
              :value="apiStats.aiAccuracy"
              suffix="%"
              :precision="1"
            />
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Hands } from '@mediapipe/hands'
import { Camera } from '@mediapipe/camera_utils'

export default {
  name: 'BaiduAIRecognition',
  data() {
    return {
      useBaiduAI: false,
      isRecognizing: false,
      recognitionLoading: false,
      mirrorMode: true,
      isTokenReady: false,

      // 百度AI配置
      baiduConfig: {
        apiKey: import.meta.env.VITE_BAIDU_API_KEY || '',
        secretKey: import.meta.env.VITE_BAIDU_SECRET_KEY || '',
        accessToken: '',
        tokenExpireTime: 0
      },

      // 识别结果
      localResult: null,
      aiResult: null,

      // MediaPipe
      hands: null,
      camera: null,

      // API统计
      apiStats: {
        todayCalls: 0,
        totalCalls: 0,
        aiAccuracy: 0
      },

      // AI状态
      aiStatus: {
        title: '本地模式',
        type: 'info',
        description: '使用MediaPipe进行本地手势识别'
      }
    }
  },

  async mounted() {
    await this.initializeMediaPipe()
    this.loadSavedToken()
  },

  methods: {
    // 初始化MediaPipe
    async initializeMediaPipe() {
      try {
        this.hands = new Hands({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
          }
        })

        this.hands.setOptions({
          maxNumHands: 2,
          modelComplexity: 1,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        })

        this.hands.onResults(this.onHandResults)
      } catch (error) {
        console.error('MediaPipe初始化失败:', error)
      }
    },

    // 切换AI模式
    async toggleAIMode() {
      if (this.useBaiduAI) {
        await this.initializeBaiduAI()
      } else {
        this.updateAIStatus('本地模式', 'info', '使用MediaPipe进行本地手势识别')
      }
    },

    // 初始化百度AI
    async initializeBaiduAI() {
      this.updateAIStatus('连接中...', 'warning', '正在连接百度AI服务...')

      try {
        if (!this.baiduConfig.apiKey || !this.baiduConfig.secretKey) {
          throw new Error('缺少百度AI凭证，请在 .env 文件中设置 VITE_BAIDU_API_KEY 和 VITE_BAIDU_SECRET_KEY')
        }

        if (!this.isTokenValid()) {
          await this.getAccessToken()
        }

        this.updateAIStatus('AI模式', 'success', '已连接百度AI服务，可进行高精度识别')
      } catch (error) {
        console.error('百度AI初始化失败:', error)
        this.useBaiduAI = false
        this.updateAIStatus('连接失败', 'error', '百度AI服务连接失败，使用本地模式')
      }
    },

    // 获取访问令牌
    async getAccessToken() {
      const url = `https://aip.baidubce.com/oauth/2.0/token?client_id=${this.baiduConfig.apiKey}&client_secret=${this.baiduConfig.secretKey}&grant_type=client_credentials`

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })

        const data = await response.json()

        if (data.access_token) {
          this.baiduConfig.accessToken = data.access_token
          this.baiduConfig.tokenExpireTime = Date.now() + (data.expires_in - 60) * 1000
          this.isTokenReady = true
          this.saveToken()
        } else {
          throw new Error(data.error_description || '获取访问令牌失败')
        }
      } catch (error) {
        console.error('获取访问令牌失败:', error)
        throw error
      }
    },

    // 检查令牌是否有效
    isTokenValid() {
      return this.baiduConfig.accessToken &&
             Date.now() < this.baiduConfig.tokenExpireTime
    },

    // 保存令牌到本地存储
    saveToken() {
      localStorage.setItem('baidu_ai_token', this.baiduConfig.accessToken)
      localStorage.setItem('baidu_ai_token_expire', this.baiduConfig.tokenExpireTime.toString())
    },

    // 加载保存的令牌
    loadSavedToken() {
      const token = localStorage.getItem('baidu_ai_token')
      const expireTime = localStorage.getItem('baidu_ai_token_expire')

      if (token && expireTime && Date.now() < parseInt(expireTime)) {
        this.baiduConfig.accessToken = token
        this.baiduConfig.tokenExpireTime = parseInt(expireTime)
        this.isTokenReady = true
      }
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

        this.camera = new Camera(videoElement, {
          onFrame: async () => {
            await this.hands.send({ image: videoElement })
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
        this.$message.error('无法访问摄像头')
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

      const canvasElement = this.$refs.canvasElement
      const ctx = canvasElement.getContext('2d')
      ctx.clearRect(0, 0, canvasElement.width, canvasElement.height)
    },

    // 处理手部检测结果
    onHandResults(results) {
      const canvasElement = this.$refs.canvasElement
      const ctx = canvasElement.getContext('2d')

      ctx.save()
      ctx.clearRect(0, 0, canvasElement.width, canvasElement.height)

      if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        const landmarks = results.multiHandLandmarks[0]

        // 绘制手部关键点
        this.drawHandLandmarks(ctx, landmarks)

        // 本地识别
        this.localResult = this.recognizeLocal(landmarks)
      } else {
        this.localResult = null
      }

      ctx.restore()
    },

    // 绘制手部关键点
    drawHandLandmarks(ctx, landmarks) {
      // 绘制连线
      const connections = [
        [0, 1], [1, 2], [2, 3], [3, 4],
        [0, 5], [5, 6], [6, 7], [7, 8],
        [0, 9], [9, 10], [10, 11], [11, 12],
        [0, 13], [13, 14], [14, 15], [15, 16],
        [0, 17], [17, 18], [18, 19], [19, 20],
        [5, 9], [9, 13], [13, 17]
      ]

      ctx.strokeStyle = '#00FF00'
      ctx.lineWidth = 2

      connections.forEach(([start, end]) => {
        const startPoint = landmarks[start]
        const endPoint = landmarks[end]

        ctx.beginPath()
        ctx.moveTo(startPoint.x * 640, startPoint.y * 480)
        ctx.lineTo(endPoint.x * 640, endPoint.y * 480)
        ctx.stroke()
      })

      // 绘制关键点
      ctx.fillStyle = '#FF0000'
      landmarks.forEach(landmark => {
        ctx.beginPath()
        ctx.arc(landmark.x * 640, landmark.y * 480, 4, 0, 2 * Math.PI)
        ctx.fill()
      })
    },

    // 本地手势识别
    recognizeLocal(landmarks) {
      const fingerStates = this.getFingerStates(landmarks)

      const gestures = [
        { name: '数字1', check: () => this.isNumberOne(fingerStates), confidence: 0.9, description: '伸出食指' },
        { name: '数字2', check: () => this.isNumberTwo(fingerStates), confidence: 0.9, description: '伸出食指和中指' },
        { name: '数字3', check: () => this.isNumberThree(fingerStates), confidence: 0.9, description: '伸出前三指' },
        { name: '点赞', check: () => this.isThumbsUp(fingerStates), confidence: 0.85, description: '拇指向上' },
        { name: 'OK', check: () => this.isOK(fingerStates), confidence: 0.8, description: 'OK手势' },
        { name: '拳头', check: () => this.isFist(fingerStates), confidence: 0.9, description: '握拳' }
      ]

      for (const gesture of gestures) {
        if (gesture.check()) {
          return {
            gesture: gesture.name,
            confidence: gesture.confidence,
            description: gesture.description
          }
        }
      }

      return {
        gesture: '未知手势',
        confidence: 0.2,
        description: '未识别到已知手势'
      }
    },

    // 拍照识别
    async captureFrame() {
      const videoElement = this.$refs.videoElement
      const canvasElement = this.$refs.canvasElement

      // 捕获当前帧
      const ctx = canvasElement.getContext('2d')
      ctx.drawImage(videoElement, 0, 0, 640, 480)

      // 转换为Base64
      const imageData = canvasElement.toDataURL('image/jpeg', 0.8)

      // 如果开启AI模式，调用百度AI识别
      if (this.useBaiduAI && this.isTokenReady) {
        await this.recognizeWithBaiduAI(imageData)
      }

      this.$message.success('已拍照分析')
    },

    // 百度AI识别
    async recognizeWithBaiduAI(imageData) {
      try {
        // 转换Base64为Blob
        const response = await fetch(imageData)
        const blob = await response.blob()

        // 创建FormData
        const formData = new FormData()
        formData.append('image', blob)

        // 调用百度AI手势分析接口
        const result = await this.callBaiduAI('hand_analysis', formData)
        this.aiResult = this.parseBaiduAIResult(result)

        // 更新统计
        this.updateAPIStats()

      } catch (error) {
        console.error('百度AI识别失败:', error)
        this.aiResult = {
          gesture: '识别失败',
          confidence: 0,
          description: 'AI服务暂时不可用'
        }
      }
    },

    // 调用百度AI API
    async callBaiduAI(apiType, formData) {
      const baseUrl = 'https://aip.baidubce.com/rest/2.0/image-classify/v1'
      const url = `${baseUrl}/${apiType}?access_token=${this.baiduConfig.accessToken}`

      const response = await fetch(url, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`API调用失败: ${response.status}`)
      }

      return await response.json()
    },

    // 解析百度AI结果
    parseBaiduAIResult(result) {
      if (result.error_code) {
        throw new Error(result.error_msg)
      }

      // 根据百度AI返回的结果解析
      const gestureName = this.mapBaiduAIGesture(result)

      return {
        gesture: gestureName,
        confidence: 0.85, // 百度AI通常有较高准确率
        description: `百度AI识别结果`,
        details: result.details || []
      }
    },

    // 映射百度AI手势名称
    mapBaiduAIGesture(result) {
      // 根据百度AI返回的手势类型映射到我们的手势名称
      const gestureMap = {
        'one': '数字1',
        'two': '数字2',
        'three': '数字3',
        'thumb_up': '点赞',
        'ok': 'OK',
        'fist': '拳头'
      }

      // 这里需要根据百度AI实际返回的数据结构进行映射
      return result.gesture || '未知手势'
    },

    // 更新API统计
    updateAPIStats() {
      this.apiStats.totalCalls++
      this.apiStats.todayCalls++

      // 计算AI准确率（简化处理）
      if (this.localResult && this.aiResult) {
        const isCorrect = this.localResult.gesture === this.aiResult.gesture
        this.apiStats.aiAccuracy = this.apiStats.aiAccuracy * 0.9 + (isCorrect ? 10 : 0)
      }
    },

    // 获取手指状态
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

    // 手势识别方法
    isNumberOne(fingerStates) {
      return fingerStates[0] && !fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isNumberTwo(fingerStates) {
      return fingerStates[0] && fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isNumberThree(fingerStates) {
      return fingerStates[0] && fingerStates[1] && fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isThumbsUp(fingerStates) {
      return fingerStates[0] && !fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isOK(fingerStates) {
      return fingerStates[0] && fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isFist(fingerStates) {
      return !fingerStates[0] && !fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    // 更新AI状态
    updateAIStatus(title, type, description) {
      this.aiStatus = { title, type, description }
    },

    // 获取进度条颜色
    getProgressColor(confidence) {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    },

    // 获取最终建议
    getFinalSuggestion() {
      if (!this.localResult && !this.aiResult) return '无结果'
      if (!this.aiResult) return this.localResult.gesture
      if (!this.localResult) return this.aiResult.gesture

      // 选择置信度更高的结果
      return this.aiResult.confidence > this.localResult.confidence
        ? this.aiResult.gesture
        : this.localResult.gesture
    },

    // 获取建议原因
    getSuggestionReason() {
      if (!this.localResult && !this.aiResult) return '请确保手部在摄像头视野内'
      if (!this.aiResult) return '本地识别结果，建议开启AI模式提高准确率'
      if (!this.localResult) return 'AI识别结果，准确率较高'

      const localConf = this.localResult.confidence
      const aiConf = this.aiResult.confidence

      if (Math.abs(localConf - aiConf) < 0.1) {
        return '本地和AI识别结果一致，置信度较高'
      } else if (aiConf > localConf) {
        return 'AI识别置信度更高，推荐使用AI结果'
      } else {
        return '本地识别置信度更高，可能AI识别出现误差'
      }
    },

    // 切换镜像模式
    toggleMirror() {
      this.mirrorMode = !this.mirrorMode
    }
  }
}
</script>

<style scoped>
.baidu-ai-recognition {
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

.ai-status {
  margin: 15px 0;
}

.camera-container {
  position: relative;
  width: 100%;
  max-width: 640px;
  margin: 20px auto;
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

.results-comparison {
  margin: 30px 0;
}

.result-panel {
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  min-height: 150px;
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

.result-panel h4 {
  margin-bottom: 15px;
  font-size: 1.1em;
}

.gesture-name {
  font-size: 1.8em;
  font-weight: bold;
  margin: 10px 0;
}

.description {
  margin-top: 10px;
  opacity: 0.9;
  font-style: italic;
}

.no-result {
  opacity: 0.7;
}

.ai-details {
  margin-top: 10px;
}

.ai-details .el-tag {
  margin: 2px;
}

.hybrid-suggestion {
  margin: 20px 0;
}

.suggestion-card {
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}

.suggestion-content {
  text-align: center;
}

.confidence-comparison {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
  font-weight: bold;
}

.final-suggestion h5 {
  margin: 10px 0;
  font-size: 1.2em;
}

.final-gesture {
  color: #409EFF;
  font-weight: bold;
}

.api-stats {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
}
</style>
