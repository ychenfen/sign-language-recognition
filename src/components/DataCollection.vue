<template>
  <div class="data-collection">
    <el-card class="collection-card">
      <template #header>
        <div class="card-header">
          <h2>📊 数据收集中心</h2>
          <el-tag type="warning">训练AI模型</el-tag>
        </div>
      </template>

      <!-- 收集状态显示 -->
      <div class="collection-status">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="已收集样本" :value="totalCollectedSamples" suffix="个" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="支持手势" :value="availableGestures.length" suffix="种" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="今日收集" :value="todayCollected" suffix="个" />
          </el-col>
        </el-row>
      </div>

      <!-- 手势选择区域 -->
      <div class="gesture-selection">
        <h3>🎯 选择要录制的手势</h3>
        <div class="gesture-buttons">
          <el-button
            v-for="gesture in availableGestures"
            :key="gesture.name"
            @click="selectGesture(gesture.name)"
            :type="selectedGesture === gesture.name ? 'primary' : 'default'"
            :size="currentGesture === gesture.name ? 'large' : 'medium'"
            :disabled="isRecording"
          >
            <span class="gesture-emoji">{{ gesture.emoji }}</span>
            {{ gesture.name }}
          </el-button>
        </div>
      </div>

      <!-- 录制控制面板 -->
      <div class="recording-panel" v-if="selectedGesture">
        <el-alert
          :title="isRecording ? `正在录制: ${selectedGesture}` : `准备录制: ${selectedGesture}`"
          :type="isRecording ? 'warning' : 'info'"
          :description="getRecordingInstructions()"
          show-icon
          :closable="false"
        />

        <div class="recording-controls">
          <div class="control-buttons">
            <el-button
              type="primary"
              @click="startRecording"
              :disabled="isRecording || !selectedGesture"
              :icon="VideoPlay"
              size="large"
            >
              开始录制
            </el-button>
            <el-button
              type="danger"
              @click="stopRecording"
              :disabled="!isRecording"
              :icon="VideoPause"
              size="large"
            >
              停止录制
            </el-button>
            <el-button
              type="success"
              @click="saveData"
              :disabled="collectedData.length === 0"
              :icon="Download"
              size="large"
            >
              下载数据
            </el-button>
          </div>

          <div class="recording-info" v-if="isRecording">
            <el-progress
              type="circle"
              :percentage="Math.min((recordedFrames / targetFrames) * 100, 100)"
              :color="getProgressColor()"
              :width="80"
            />
            <div class="info-text">
              <p><strong>已录制:</strong> {{ recordedFrames }} / {{ targetFrames }} 帧</p>
              <p><strong>录制时间:</strong> {{ recordingTime }}s</p>
              <p><strong>质量评估:</strong> {{ getQualityAssessment() }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 收集进度图表 -->
      <div class="progress-chart">
        <h3>📈 收集进度</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>各手势收集数量</h4>
              <div class="progress-bars">
                <div
                  v-for="gesture in availableGestures"
                  :key="gesture.name"
                  class="gesture-progress"
                >
                  <span class="gesture-label">{{ gesture.emoji }} {{ gesture.name }}</span>
                  <el-progress
                    :percentage="getGestureProgress(gesture.name)"
                    :color="getGestureProgressColor(gesture.name)"
                    :format="() => `${getGestureSampleCount(gesture.name)}/${targetSamplesPerGesture}`"
                  />
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>今日收集趋势</h4>
              <div class="trend-info">
                <p>上午: <strong>{{ morningSamples }}</strong> 个样本</p>
                <p>下午: <strong>{{ afternoonSamples }}</strong> 个样本</p>
                <p>晚上: <strong>{{ eveningSamples }}</strong> 个样本</p>
                <el-divider />
                <p>总计: <strong>{{ todayCollected }}</strong> 个样本</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 数据预览 -->
      <div class="data-preview" v-if="collectedData.length > 0">
        <h3>🔍 数据预览</h3>
        <el-table :data="dataPreview" style="width: 100%" height="200">
          <el-table-column prop="gesture" label="手势" width="120" />
          <el-table-column prop="sampleCount" label="样本数" width="100" />
          <el-table-column prop="avgConfidence" label="平均置信度" width="120">
            <template #default="scope">
              <el-tag :type="getConfidenceTagType(scope.row.avgConfidence)">
                {{ (scope.row.avgConfidence * 100).toFixed(1) }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastUpdated" label="最后更新" />
        </el-table>
      </div>

      <!-- 导出选项 -->
      <div class="export-options">
        <h3>💾 数据导出</h3>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-button
              type="primary"
              @click="exportJSON"
              :disabled="collectedData.length === 0"
              :icon="Download"
              block
            >
              导出JSON格式
            </el-button>
          </el-col>
          <el-col :span="8">
            <el-button
              type="success"
              @click="exportCSV"
              :disabled="collectedData.length === 0"
              :icon="Download"
              block
            >
              导出CSV格式
            </el-button>
          </el-col>
          <el-col :span="8">
            <el-button
              type="warning"
              @click="uploadToServer"
              :disabled="collectedData.length === 0"
              :icon="Upload"
              block
            >
              上传到服务器
            </el-button>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { VideoPlay, VideoPause, Download, Upload } from '@element-plus/icons-vue'

export default {
  name: 'DataCollection',
  components: {
    VideoPlay,
    VideoPause,
    Download,
    Upload
  },
  data() {
    return {
      selectedGesture: null,
      currentGesture: null,
      isRecording: false,
      recordedFrames: 0,
      targetFrames: 100,
      targetSamplesPerGesture: 50,
      recordingStartTime: null,
      recordingTime: 0,
      collectedData: [],
      recordingTimer: null,

      // 可用的手势列表
      availableGestures: [
        { name: '数字1', emoji: '☝️', description: '伸出食指' },
        { name: '数字2', emoji: '✌️', description: '伸出食指和中指' },
        { name: '数字3', emoji: '🤟', description: '伸出前三指' },
        { name: '数字4', emoji: '🖖', description: '伸出四指' },
        { name: '数字5', emoji: '🖐️', description: '伸出五指' },
        { name: '点赞', emoji: '👍', description: '拇指向上' },
        { name: 'OK', emoji: '👌', description: '拇指和食指成圆圈' },
        { name: '你好', emoji: '👋', description: '挥手动作' },
        { name: '拳头', emoji: '✊', description: '握拳' }
      ]
    }
  },

  computed: {
    totalCollectedSamples() {
      return this.collectedData.length
    },

    todayCollected() {
      const today = new Date().toDateString()
      return this.collectedData.filter(item =>
        new Date(item.timestamp).toDateString() === today
      ).length
    },

    morningSamples() {
      return this.getSamplesByTimeRange(6, 12)
    },

    afternoonSamples() {
      return this.getSamplesByTimeRange(12, 18)
    },

    eveningSamples() {
      return this.getSamplesByTimeRange(18, 24)
    },

    dataPreview() {
      const gestureStats = {}

      this.collectedData.forEach(item => {
        if (!gestureStats[item.gesture]) {
          gestureStats[item.gesture] = {
            gesture: item.gesture,
            sampleCount: 0,
            totalConfidence: 0,
            lastUpdated: new Date(item.timestamp).toLocaleString()
          }
        }
        gestureStats[item.gesture].sampleCount++
        gestureStats[item.gesture].totalConfidence += item.confidence || 0.8
      })

      return Object.values(gestureStats).map(stat => ({
        ...stat,
        avgConfidence: stat.totalConfidence / stat.sampleCount
      }))
    }
  },

  methods: {
    selectGesture(gesture) {
      this.selectedGesture = gesture
    },

    getRecordingInstructions() {
      if (!this.selectedGesture) return '请先选择要录制的手势'

      const gesture = this.availableGestures.find(g => g.name === this.selectedGesture)
      return `请做出"${gesture.description}"的手势，保持姿势稳定，确保摄像头能够清晰捕捉到您的手部动作。录制完成后系统会自动停止。`
    },

    startRecording() {
      if (!this.selectedGesture) {
        this.$message.warning('请先选择要录制的手势')
        return
      }

      this.currentGesture = this.selectedGesture
      this.isRecording = true
      this.recordedFrames = 0
      this.recordingStartTime = Date.now()

      // 启动计时器
      this.recordingTimer = setInterval(() => {
        this.recordingTime = Math.floor((Date.now() - this.recordingStartTime) / 1000)

        // 模拟数据收集
        if (this.recordedFrames < this.targetFrames) {
          this.collectSample()
        } else {
          this.stopRecording()
        }
      }, 100)

      this.$message.success(`开始录制: ${this.currentGesture}`)
    },

    stopRecording() {
      this.isRecording = false
      this.currentGesture = null
      this.recordingTime = 0

      if (this.recordingTimer) {
        clearInterval(this.recordingTimer)
        this.recordingTimer = null
      }

      this.$message.info('录制完成')
    },

    collectSample() {
      // 模拟收集手部数据
      const sample = {
        gesture: this.currentGesture,
        timestamp: Date.now(),
        landmarks: this.generateMockLandmarks(),
        confidence: 0.7 + Math.random() * 0.3, // 模拟置信度
        frameId: this.recordedFrames
      }

      this.collectedData.push(sample)
      this.recordedFrames++
    },

    generateMockLandmarks() {
      // 生成模拟的手部关键点数据
      const landmarks = []
      for (let i = 0; i < 21; i++) {
        landmarks.push({
          x: Math.random(),
          y: Math.random(),
          z: Math.random()
        })
      }
      return landmarks
    },

    getProgressColor() {
      const percentage = (this.recordedFrames / this.targetFrames) * 100
      if (percentage < 33) return '#F56C6C'
      if (percentage < 66) return '#E6A23C'
      return '#67C23A'
    },

    getQualityAssessment() {
      const avgConfidence = this.calculateAverageConfidence()
      if (avgConfidence >= 0.9) return '优秀'
      if (avgConfidence >= 0.8) return '良好'
      if (avgConfidence >= 0.7) return '一般'
      return '需要改进'
    },

    calculateAverageConfidence() {
      if (this.collectedData.length === 0) return 0

      const recentData = this.collectedData.slice(-10)
      const totalConfidence = recentData.reduce((sum, item) => sum + item.confidence, 0)
      return totalConfidence / recentData.length
    },

    getGestureProgress(gestureName) {
      const count = this.getGestureSampleCount(gestureName)
      return Math.min((count / this.targetSamplesPerGesture) * 100, 100)
    },

    getGestureSampleCount(gestureName) {
      return this.collectedData.filter(item => item.gesture === gestureName).length
    },

    getGestureProgressColor(gestureName) {
      const count = this.getGestureSampleCount(gestureName)
      const percentage = (count / this.targetSamplesPerGesture) * 100

      if (percentage >= 100) return '#67C23A'
      if (percentage >= 66) return '#E6A23C'
      return '#F56C6C'
    },

    getSamplesByTimeRange(startHour, endHour) {
      return this.collectedData.filter(item => {
        const hour = new Date(item.timestamp).getHours()
        return hour >= startHour && hour < endHour
      }).length
    },

    getConfidenceTagType(confidence) {
      if (confidence >= 0.9) return 'success'
      if (confidence >= 0.8) return 'warning'
      return 'danger'
    },

    saveData() {
      if (this.collectedData.length === 0) {
        this.$message.warning('没有可保存的数据')
        return
      }

      this.exportJSON()
    },

    exportJSON() {
      const dataStr = JSON.stringify(this.collectedData, null, 2)
      const blob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = `sign_language_data_${new Date().toISOString().slice(0, 10)}.json`
      a.click()

      URL.revokeObjectURL(url)
      this.$message.success('JSON数据已导出')
    },

    exportCSV() {
      if (this.collectedData.length === 0) {
        this.$message.warning('没有可导出的数据')
        return
      }

      // 转换为CSV格式
      const headers = ['gesture', 'timestamp', 'confidence', 'frameId']
      const csvContent = [
        headers.join(','),
        ...this.collectedData.map(item =>
          `${item.gesture},${item.timestamp},${item.confidence},${item.frameId}`
        )
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = `sign_language_data_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()

      URL.revokeObjectURL(url)
      this.$message.success('CSV数据已导出')
    },

    uploadToServer() {
      // 模拟上传到服务器
      this.$message.info('正在上传数据到服务器...')

      setTimeout(() => {
        this.$message.success('数据上传成功！')
      }, 2000)
    }
  }
}
</script>

<style scoped>
.data-collection {
  height: 100%;
}

.collection-card {
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
  color: #E6A23C;
  font-size: 1.5em;
}

.collection-status {
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
}

.gesture-selection h3 {
  margin-bottom: 15px;
  color: #303133;
}

.gesture-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.gesture-emoji {
  font-size: 1.2em;
  margin-right: 5px;
}

.recording-panel {
  margin: 20px 0;
  padding: 20px;
  background: #FFF9E6;
  border-radius: 10px;
  border: 2px solid #E6A23C;
}

.recording-controls {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.recording-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.info-text p {
  margin: 5px 0;
  font-size: 0.9em;
}

.progress-chart {
  margin: 30px 0;
}

.progress-chart h3 {
  margin-bottom: 20px;
  color: #409EFF;
}

.chart-container {
  padding: 15px;
  background: #F5F7FA;
  border-radius: 8px;
}

.chart-container h4 {
  margin-bottom: 15px;
  color: #606266;
}

.gesture-progress {
  margin-bottom: 10px;
}

.gesture-label {
  display: inline-block;
  width: 120px;
  font-size: 0.9em;
}

.trend-info p {
  margin: 8px 0;
  color: #606266;
}

.data-preview {
  margin: 20px 0;
}

.data-preview h3 {
  margin-bottom: 15px;
  color: #409EFF;
}

.export-options {
  margin: 20px 0;
  padding: 20px;
  background: #F0F9FF;
  border-radius: 10px;
  border: 2px solid #409EFF;
}

.export-options h3 {
  margin-bottom: 15px;
  color: #409EFF;
}
</style>