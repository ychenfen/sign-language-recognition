# 百度API问题解决方案

## 🔍 常见问题诊断

### 1. 百度API常见错误类型

#### A. 访问令牌问题
- **错误**: `access_token invalid`
- **原因**: Token过期或获取失败
- **解决**: 重新获取访问令牌

#### B. 配额问题
- **错误**: `Daily quota exceeded`
- **原因**: 每日调用次数超限
- **解决**: 等待第二天或升级套餐

#### C. 网络问题
- **错误**: `Network error`, `Timeout`
- **原因**: 网络连接问题或超时
- **解决**: 检查网络连接，增加超时时间

#### D. 图片格式问题
- **错误**: `Invalid image format`
- **原因**: 图片格式不支持或损坏
- **解决**: 检查图片格式和大小

#### E. 权限问题
- **错误**: `Permission denied`
- **原因**: API权限不足
- **解决**: 检查API权限配置

### 2. 当前项目中的潜在问题

#### A. CORS跨域问题
- 前端直接调用百度API可能遇到CORS限制
- 需要通过后端代理或使用JSONP

#### B. 敏感信息暴露
- API Key直接写在前端代码中
- 存在安全风险

#### C. 错误处理不完善
- 没有对各种API错误进行分类处理
- 用户体验不够友好

## ✅ 解决方案

### 方案1: 优化前端API调用

```javascript
// 改进的API调用逻辑
class BaiduAIService {
  constructor() {
    this.apiKey = '<YOUR_BAIDU_API_KEY>'
    this.secretKey = '<YOUR_BAIDU_SECRET_KEY>'
    this.accessToken = null
    this.tokenExpireTime = 0
    this.baseUrl = 'https://aip.baidubce.com/rest/2.0/image-classify/v1'
  }

  // 获取访问令牌
  async getAccessToken() {
    if (this.isTokenValid()) {
      return this.accessToken
    }

    try {
      const response = await fetch(
        `https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=${this.apiKey}&client_secret=${this.secretKey}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        }
      )

      const data = await response.json()

      if (data.access_token) {
        this.accessToken = data.access_token
        this.tokenExpireTime = Date.now() + (data.expires_in - 60) * 1000
        return this.accessToken
      } else {
        throw new Error(data.error_description || '获取访问令牌失败')
      }
    } catch (error) {
      console.error('获取访问令牌失败:', error)
      throw error
    }
  }

  // 手势分析API调用
  async analyzeGesture(imageData) {
    try {
      const token = await this.getAccessToken()
      const formData = new FormData()
      formData.append('image', imageData)

      const response = await fetch(
        `${this.baseUrl}/hand_analysis?access_token=${token}`,
        {
          method: 'POST',
          body: formData
        }
      )

      const data = await response.json()

      if (data.error_code) {
        throw new Error(this.getErrorMessage(data.error_code))
      }

      return this.parseResult(data)
    } catch (error) {
      console.error('手势分析失败:', error)
      throw error
    }
  }

  // 错误信息映射
  getErrorMessage(errorCode) {
    const errorMap = {
      4: 'Request parameter error',
      17: 'Daily quota exceeded',
      18: 'QPS exceeded',
      19: 'Request frequency exceeded',
      100: 'Invalid parameter',
      110: 'Access token invalid or no longer valid',
      111: 'Access token expired',
      282000: 'Internal server error',
      282003: 'Request parameter error',
      282005: 'Processing error',
      282006: 'Daily quota exceeded'
    }
    return errorMap[errorCode] || `Unknown error: ${errorCode}`
  }

  // 解析API结果
  parseResult(data) {
    return {
      gesture: this.mapGestureResult(data),
      confidence: 0.85,
      details: data
    }
  }

  // 映射手势结果
  mapGestureResult(data) {
    // 根据百度API返回的实际数据结构进行映射
    if (data.result && data.result.length > 0) {
      return data.result[0].name || '未知手势'
    }
    return '未知手势'
  }

  // 检查令牌是否有效
  isTokenValid() {
    return this.accessToken && Date.now() < this.tokenExpireTime
  }
}
```

### 方案2: 创建后端代理服务

```javascript
// 后端代理示例（Node.js）
const express = require('express')
const multer = require('multer')
const axios = require('axios')
const cors = require('cors')

const app = express()
const upload = multer()

app.use(cors())
app.use(express.json())

// 代理百度API
app.post('/api/baidu/hand-analysis', upload.single('image'), async (req, res) => {
  try {
    const token = await getBaiduToken()
    const formData = new FormData()
    formData.append('image', req.file.buffer, req.file.originalname)

    const response = await axios.post(
      `https://aip.baidubce.com/rest/2.0/image-classify/v1/hand_analysis?access_token=${token}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 10000
      }
    )

    res.json(response.data)
  } catch (error) {
    console.error('代理请求失败:', error)
    res.status(500).json({ error: error.message })
  }
})

// 获取百度访问令牌
async function getBaiduToken() {
  const response = await axios.post(
    'https://aip.baidubce.com/oauth/2.0/token',
    null,
    {
      params: {
        grant_type: 'client_credentials',
        client_id: '<YOUR_BAIDU_API_KEY>',
        client_secret: '<YOUR_BAIDU_SECRET_KEY>'
      }
    }
  )
  return response.data.access_token
}

app.listen(3002, () => {
  console.log('代理服务器运行在端口 3002')
})
```

### 方案3: 创建本地AI模型

```javascript
// 使用TensorFlow.js创建本地手势识别模型
import * as tf from '@tensorflow/tfjs'

class LocalGestureRecognition {
  constructor() {
    this.model = null
    this.isModelLoaded = false
  }

  // 加载预训练模型
  async loadModel() {
    try {
      this.model = await tf.loadLayersModel('/models/gesture-model.json')
      this.isModelLoaded = true
      console.log('本地手势识别模型加载成功')
    } catch (error) {
      console.error('模型加载失败:', error)
      // 使用简化规则作为备用
      this.isModelLoaded = false
    }
  }

  // 本地手势识别
  recognizeGesture(landmarks) {
    if (this.isModelLoaded) {
      return this.predictWithModel(landmarks)
    } else {
      return this.predictWithRules(landmarks)
    }
  }

  // 使用模型预测
  predictWithModel(landmarks) {
    // 将手部关键点转换为模型输入
    const input = this.preprocessLandmarks(landmarks)
    const prediction = this.model.predict(input)
    return this.parsePrediction(prediction)
  }

  // 使用规则预测（备用方案）
  predictWithRules(landmarks) {
    const fingerStates = this.getFingerStates(landmarks)

    if (this.isFist(fingerStates)) {
      return { gesture: '拳头', confidence: 0.9 }
    } else if (this.isThumbsUp(fingerStates)) {
      return { gesture: '点赞', confidence: 0.85 }
    }
    // ... 其他规则

    return { gesture: '未知手势', confidence: 0.3 }
  }
}
```

## 🚀 立即可行的解决方案

### 1. 改进前端错误处理

```javascript
// 在BaiduAIRecognition.vue中添加更好的错误处理
methods: {
  async recognizeWithBaiduAI(imageData) {
    try {
      // 显示加载状态
      this.aiLoading = true

      const result = await this.baiduAI.analyzeGesture(imageData)
      this.aiResult = result

      // 更新统计
      this.updateAPIStats(true)

    } catch (error) {
      console.error('百度AI识别失败:', error)

      // 显示用户友好的错误信息
      this.showErrorMessage(error)

      // 切换到备用方案
      this.useLocalRecognition()

      // 更新统计
      this.updateAPIStats(false)
    } finally {
      this.aiLoading = false
    }
  },

  showErrorMessage(error) {
    let message = 'AI识别服务暂时不可用'

    if (error.message.includes('quota exceeded')) {
      message = '今日AI调用次数已用完，请明天再试'
    } else if (error.message.includes('Network error')) {
      message = '网络连接异常，请检查网络设置'
    } else if (error.message.includes('invalid')) {
      message = 'API配置错误，请联系管理员'
    }

    this.$message.warning(message)
  },

  useLocalRecognition() {
    // 使用本地识别作为备用方案
    this.aiResult = {
      gesture: '本地识别',
      confidence: 0.7,
      description: '使用本地规则识别'
    }
  }
}
```

### 2. 创建离线模式

```javascript
// 添加离线模式支持
data() {
  return {
    isOnline: navigator.onLine,
    useOfflineMode: false
  }
},

mounted() {
  window.addEventListener('online', this.handleOnlineStatusChange)
  window.addEventListener('offline', this.handleOnlineStatusChange)
},

methods: {
  handleOnlineStatusChange() {
    this.isOnline = navigator.onLine

    if (!this.isOnline) {
      this.useOfflineMode = true
      this.$message.info('网络已断开，使用离线模式')
    } else {
      this.useOfflineMode = false
      this.$message.success('网络已连接')
    }
  }
}
```

## 📋 测试和验证步骤

### 1. API连接测试
```javascript
// 测试百度API连接
async function testBaiduAPI() {
  try {
    const service = new BaiduAIService()
    const token = await service.getAccessToken()
    console.log('API连接正常，Token获取成功')
    return true
  } catch (error) {
    console.error('API连接失败:', error)
    return false
  }
}
```

### 2. 功能完整性测试
1. **本地模式**: 确保本地识别功能正常
2. **AI模式**: 测试百度API调用
3. **混合模式**: 验证结果对比和建议
4. **错误处理**: 测试各种错误场景

## 💡 使用建议

### 立即可行的改进
1. **添加错误重试机制**: 网络错误时自动重试
2. **提供降级方案**: API失败时使用本地识别
3. **优化用户体验**: 显示友好的错误提示
4. **添加状态指示**: 清楚显示当前使用的是哪种模式

### 中长期优化
1. **实现后端代理**: 解决CORS和安全问题
2. **训练自定义模型**: 提高识别准确率
3. **添加更多AI服务**: 提供多样化的AI功能
4. **实现缓存机制**: 减少API调用次数

---

**总结**: 通过以上解决方案，可以有效解决百度API的各种问题，确保应用的稳定性和用户体验。建议优先实现错误处理和降级方案，然后逐步添加更高级的功能。