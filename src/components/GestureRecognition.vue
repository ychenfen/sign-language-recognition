<template>
  <div class="gesture-recognition">
    <el-card class="recognition-card">
      <template #header>
        <div class="card-header">
          <h2>🎯 实时手势识别</h2>
          <el-tag :type="isRecognizing ? 'success' : 'info'">
            {{ isRecognizing ? '识别中' : '已停止' }}
          </el-tag>
        </div>
      </template>

      <!-- 摄像头和画布区域 -->
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

        <!-- 摄像头控制按钮 -->
        <div class="camera-controls">
          <el-button-group>
            <el-button
              type="primary"
              @click="toggleRecognition"
              :loading="cameraLoading"
              :icon="isRecognizing ? 'VideoPause' : 'VideoPlay'"
            >
              {{ isRecognizing ? '停止识别' : '开始识别' }}
            </el-button>
            <el-button @click="toggleMirror">
              <el-icon><Refresh /></el-icon>
              镜像
            </el-button>
          </el-button-group>
        </div>
      </div>

      <!-- 识别结果显示 -->
      <div class="result-panel" v-if="recognitionResult">
        <div class="result-content">
          <div class="gesture-info">
            <h3>识别结果: <span class="gesture-name">{{ recognitionResult.gesture }}</span></h3>
            <div class="confidence-bar">
              <span>置信度: {{ Math.round(recognitionResult.confidence * 100) }}%</span>
              <el-progress
                :percentage="Math.round(recognitionResult.confidence * 100)"
                :color="getProgressColor(recognitionResult.confidence)"
                :show-text="false"
              />
            </div>
          </div>

          <div class="gesture-description" v-if="recognitionResult.description">
            <p>{{ recognitionResult.description }}</p>
          </div>
        </div>
      </div>

      <!-- 支持的手势列表 -->
      <div class="supported-gestures">
        <h4>📚 支持的手势</h4>
        <div class="gesture-grid">
          <div
            v-for="gesture in supportedGestures"
            :key="gesture.name"
            class="gesture-item"
            :class="{ active: recognitionResult?.gesture === gesture.name }"
          >
            <div class="gesture-icon">{{ gesture.icon }}</div>
            <div class="gesture-info">
              <span class="gesture-name">{{ gesture.name }}</span>
              <span class="gesture-description">{{ gesture.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Hands } from '@mediapipe/hands'
import { Camera } from '@mediapipe/camera_utils'

export default {
  name: 'GestureRecognition',
  data() {
    return {
      isRecognizing: false,
      cameraLoading: false,
      mirrorMode: true,
      recognitionResult: null,
      hands: null,
      camera: null,

      // 支持的手语词汇
      supportedGestures: [
        { name: '数字1', icon: '☝️', description: '伸出食指' },
        { name: '数字2', icon: '✌️', description: '伸出食指和中指' },
        { name: '数字3', icon: '🤟', description: '伸出前三指' },
        { name: '数字4', icon: '🖖', description: '伸出四指' },
        { name: '数字5', icon: '🖐️', description: '伸出五指' },
        { name: '点赞', icon: '👍', description: '拇指向上' },
        { name: 'OK', icon: '👌', description: '拇指和食指成圆圈' },
        { name: '你好', icon: '👋', description: '挥手动作' },
        { name: '拳头', icon: '✊', description: '握拳' },
        { name: '祈祷', icon: '🙏', description: '双手合十' },
        { name: '打不开', icon: '🔒', description: '握拳表示打不开' }
      ]
    }
  },

  async mounted() {
    await this.initializeHandDetection()
  },

  beforeUnmount() {
    this.cleanup()
  },

  methods: {
    // 初始化手部检测
    async initializeHandDetection() {
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

        console.log('✅ 手部检测初始化成功')
      } catch (error) {
        console.error('❌ 手部检测初始化失败:', error)
        this.$message.error('手部检测初始化失败，请刷新页面重试')
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
        this.cameraLoading = true

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

        // 设置画布尺寸
        canvasElement.width = 640
        canvasElement.height = 480

        this.isRecognizing = true
        this.$message.success('开始手势识别')

      } catch (error) {
        console.error('启动识别失败:', error)
        this.$message.error('无法访问摄像头，请检查权限设置')
      } finally {
        this.cameraLoading = false
      }
    },

    // 停止识别
    stopRecognition() {
      if (this.camera) {
        this.camera.stop()
        this.camera = null
      }

      this.isRecognizing = false
      this.recognitionResult = null

      // 清空画布
      const canvasElement = this.$refs.canvasElement
      const ctx = canvasElement.getContext('2d')
      ctx.clearRect(0, 0, canvasElement.width, canvasElement.height)

      this.$message.info('手势识别已停止')
    },

    // 处理��部检测结果
    onHandResults(results) {
      const canvasElement = this.$refs.canvasElement
      const ctx = canvasElement.getContext('2d')

      // 清空画布
      ctx.save()
      ctx.clearRect(0, 0, canvasElement.width, canvasElement.height)

      if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        for (const landmarks of results.multiHandLandmarks) {
          // 绘制手部关键点和连线
          this.drawHandLandmarks(ctx, landmarks)

          // 识别手势
          const gesture = this.recognizeGesture(landmarks)
          this.recognitionResult = gesture
        }
      } else {
        // 没有检测到手部时清空结果
        this.recognitionResult = null
      }

      ctx.restore()
    },

    // 绘制手部关键点
    drawHandLandmarks(ctx, landmarks) {
      // 绘制连线
      const connections = [
        [0, 1], [1, 2], [2, 3], [3, 4],     // 拇指
        [0, 5], [5, 6], [6, 7], [7, 8],     // 食指
        [0, 9], [9, 10], [10, 11], [11, 12], // 中指
        [0, 13], [13, 14], [14, 15], [15, 16], // 无名指
        [0, 17], [17, 18], [18, 19], [19, 20], // 小指
        [5, 9], [9, 13], [13, 17]            // 手掌
      ]

      ctx.strokeStyle = '#00FF00'
      ctx.lineWidth = 3

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
        ctx.arc(landmark.x * 640, landmark.y * 480, 6, 0, 2 * Math.PI)
        ctx.fill()
      })
    },

    // 识别手势
    recognizeGesture(landmarks) {
      const fingerStates = this.getFingerStates(landmarks)
      const handFeatures = this.extractHandFeatures(landmarks)

      // 基于规则识别手势
      const gestures = [
        { name: '数字1', check: () => this.isNumberOne(fingerStates), confidence: 0.95, description: '伸出食指表示数字1' },
        { name: '数字2', check: () => this.isNumberTwo(fingerStates), confidence: 0.95, description: '伸出食指和中指表示数字2' },
        { name: '数字3', check: () => this.isNumberThree(fingerStates), confidence: 0.95, description: '伸出前三指表示数字3' },
        { name: '数字4', check: () => this.isNumberFour(fingerStates), confidence: 0.95, description: '伸出四指表示数字4' },
        { name: '数字5', check: () => this.isNumberFive(fingerStates), confidence: 0.95, description: '伸出五指表示数字5' },
        { name: '点赞', check: () => this.isThumbsUp(fingerStates, handFeatures), confidence: 0.90, description: '拇指向上表示赞同或喜欢' },
        { name: 'OK', check: () => this.isOK(fingerStates, handFeatures), confidence: 0.85, description: '拇指和食指成圆圈表示OK' },
        { name: '你好', check: () => this.isWaving(landmarks), confidence: 0.80, description: '挥手表示打招呼' },
        { name: '拳头', check: () => this.isFist(fingerStates), confidence: 0.90, description: '握拳表示力量或决心' },
        { name: '祈祷', check: () => this.isPraying(landmarks), confidence: 0.85, description: '双手合十表示祈祷或感谢' },
        { name: '打不开', check: () => this.isFist(fingerStates), confidence: 0.9, description: '握拳表示无法打开' }
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
        description: '未识别到已知手势，请尝试做出标准手势'
      }
    },

    // 获取手指状态
    getFingerStates(landmarks) {
      const states = []

      // 拇指（特殊处理，因为方向不同）
      const thumbIsUp = landmarks[4].y < landmarks[3].y
      states.push(thumbIsUp)

      // 其他四指
      for (let i = 1; i <= 4; i++) {
        const tipIndex = i * 4
        const pipIndex = i * 4 - 2
        const fingerIsUp = landmarks[tipIndex].y < landmarks[pipIndex].y
        states.push(fingerIsUp)
      }

      return states
    },

    // 提取手部特征
    extractHandFeatures(landmarks) {
      const wrist = landmarks[0]
      const thumbTip = landmarks[4]
      const indexTip = landmarks[8]
      const middleTip = landmarks[12]

      return {
        wristPosition: { x: wrist.x, y: wrist.y },
        thumbPosition: { x: thumbTip.x, y: thumbTip.y },
        indexPosition: { x: indexTip.x, y: indexTip.y },
        middlePosition: { x: middleTip.x, y: middleTip.y },
        handArea: this.calculateHandArea(landmarks)
      }
    },

    // 计算手部区域大小
    calculateHandArea(landmarks) {
      let minX = 1, minY = 1, maxX = 0, maxY = 0
      landmarks.forEach(landmark => {
        minX = Math.min(minX, landmark.x)
        minY = Math.min(minY, landmark.y)
        maxX = Math.max(maxX, landmark.x)
        maxY = Math.max(maxY, landmark.y)
      })
      return (maxX - minX) * (maxY - minY)
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

    isNumberFour(fingerStates) {
      return fingerStates[0] && fingerStates[1] && fingerStates[2] &&
             fingerStates[3] && !fingerStates[4]
    },

    isNumberFive(fingerStates) {
      return fingerStates[0] && fingerStates[1] && fingerStates[2] &&
             fingerStates[3] && fingerStates[4]
    },

    isThumbsUp(fingerStates, features) {
      return fingerStates[0] && !fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4] &&
             features.thumbPosition.y < features.wristPosition.y
    },

    isOK(fingerStates, features) {
      return fingerStates[0] && fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4] &&
             this.isFingerTipsClose(features.thumbPosition, features.indexPosition)
    },

    isWaving(landmarks) {
      // 检测挥手动作（需要历史数据）
      // 这里简化处理，检测手腕位置较高
      const wrist = landmarks[0]
      return wrist.y < 0.3
    },

    isFist(fingerStates) {
      return !fingerStates[0] && !fingerStates[1] && !fingerStates[2] &&
             !fingerStates[3] && !fingerStates[4]
    },

    isPraying(landmarks) {
      // 简化处理：检测双手（需要检测到两只手）
      // 这里暂时返回false，实际需要检测两只手
      return false
    },

    // 检查指尖是否接近
    isFingerTipsClose(pos1, pos2) {
      const distance = Math.sqrt(
        Math.pow(pos1.x - pos2.x, 2) + Math.pow(pos1.y - pos2.y, 2)
      )
      return distance < 0.1
    },

    // 切换镜像模式
    toggleMirror() {
      this.mirrorMode = !this.mirrorMode
    },

    // 获取进度条颜色
    getProgressColor(confidence) {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    },

    // 清理资源
    cleanup() {
      if (this.camera) {
        this.camera.stop()
      }
      if (this.hands) {
        this.hands.close()
      }
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

.camera-container {
  position: relative;
  width: 100%;
  max-width: 640px;
  margin: 0 auto 20px;
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

.result-panel {
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
}

.result-content h3 {
  margin: 0 0 15px 0;
  font-size: 1.3em;
}

.gesture-name {
  color: #FFD700;
  font-weight: bold;
}

.confidence-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.confidence-bar span {
  min-width: 80px;
}

.gesture-description {
  margin-top: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  font-style: italic;
}

.supported-gestures {
  margin-top: 20px;
}

.supported-gestures h4 {
  margin-bottom: 15px;
  color: #409EFF;
}

.gesture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.gesture-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 2px solid #E4E7ED;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.gesture-item:hover {
  border-color: #409EFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.gesture-item.active {
  border-color: #67C23A;
  background: rgba(103, 194, 58, 0.1);
}

.gesture-icon {
  font-size: 1.5em;
}

.gesture-info {
  display: flex;
  flex-direction: column;
}

.gesture-name {
  font-weight: bold;
  color: #303133;
}

.gesture-description {
  font-size: 0.8em;
  color: #909399;
}
</style>