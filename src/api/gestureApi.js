/**
 * Gesture Recognition API Service
 * 连接Python Flask后端API
 */

const API_BASE_URL = 'http://localhost:5001/api'

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  const contentType = response.headers.get('content-type') || ''

  let data = {}
  try {
    if (contentType.includes('application/json')) {
      data = await response.json()
    } else {
      const text = await response.text()
      data = text ? { message: text } : {}
    }
  } catch (error) {
    data = {}
  }

  return {
    ok: response.ok,
    status: response.status,
    data
  }
}

/**
 * 健康检查
 */
export async function checkHealth() {
  try {
    const result = await requestJson('/health')
    if (result.ok) {
      return result.data
    }
    return {
      status: 'error',
      message: result.data?.error || result.data?.message || `服务异常（${result.status}）`
    }
  } catch (error) {
    console.error('Health check failed:', error)
    return { status: 'error', message: error.message }
  }
}

/**
 * 获取支持的手势列表
 */
export async function getGestures() {
  try {
    const result = await requestJson('/gestures')
    if (!result.ok) {
      return []
    }

    const data = result.data || {}
    if (Array.isArray(data.gestures)) {
      return data.gestures
    }
    if (Array.isArray(data.static_gestures)) {
      return data.static_gestures
    }
    return []
  } catch (error) {
    console.error('Failed to get gestures:', error)
    return []
  }
}

/**
 * 识别手势
 * @param {string} imageBase64 - Base64编码的图片
 */
export async function recognizeGesture(imageBase64) {
  try {
    // 移除data:image/xxx;base64,前缀
    const base64Data = imageBase64.replace(/^data:image\/\w+;base64,/, '')

    const result = await requestJson('/recognize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ image: base64Data })
    })

    if (result.ok) {
      return result.data
    }
    return {
      error: result.data?.error || result.data?.message || `识别失败（${result.status}）`,
      gesture: 'error'
    }
  } catch (error) {
    console.error('Recognition failed:', error)
    return { error: error.message, gesture: 'error' }
  }
}

/**
 * 验证手势是否正确
 * @param {string} imageBase64 - Base64编码的图片
 * @param {string} expectedGesture - 期望的手势ID
 */
export async function verifyGesture(imageBase64, expectedGesture) {
  try {
    const base64Data = imageBase64.replace(/^data:image\/\w+;base64,/, '')

    const result = await requestJson('/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: base64Data,
        expected: expectedGesture
      })
    })

    if (result.ok) {
      return result.data
    }
    return {
      error: result.data?.error || result.data?.message || `验证失败（${result.status}）`,
      correct: false
    }
  } catch (error) {
    console.error('Verification failed:', error)
    return { error: error.message, correct: false }
  }
}

/**
 * AI聊天
 * @param {string} message - 用户消息
 * @param {Array} history - 对话历史
 */
export async function aiChat(message, history = null) {
  try {
    const result = await requestJson('/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message, history })
    })

    if (result.ok) {
      return result.data
    }

    return {
      status: 'error',
      reply: result.data?.reply || result.data?.error || '抱歉，AI服务暂时不可用，请稍后再试。'
    }
  } catch (error) {
    console.error('AI chat failed:', error)
    return {
      status: 'error',
      reply: '抱歉，AI服务暂时不可用，请稍后再试。'
    }
  }
}

/**
 * 获取手势解释
 * @param {string} gestureId - 手势ID
 */
export async function getGestureExplanation(gestureId) {
  try {
    const result = await requestJson(`/ai/explain/${gestureId}`)
    if (result.ok) {
      return result.data
    }
    return {
      error: result.data?.error || result.data?.message || `获取解释失败（${result.status}）`
    }
  } catch (error) {
    console.error('Failed to get explanation:', error)
    return { error: error.message }
  }
}

/**
 * 获取学习建议
 * @param {Array} completedGestures - 已完成的手势ID列表
 */
export async function getLearningAdvice(completedGestures = []) {
  try {
    const result = await requestJson('/ai/suggestion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ completed_gestures: completedGestures })
    })

    if (result.ok) {
      return result.data
    }
    if (result.status === 404 || result.status === 405) {
      return getLocalLearningAdvice(completedGestures)
    }
    return {
      error: result.data?.error || result.data?.message || `获取建议失败（${result.status}）`
    }
  } catch (error) {
    console.error('Failed to get advice:', error)
    return getLocalLearningAdvice(completedGestures)
  }
}

/**
 * 获取练习反馈
 * @param {string} gestureId - 手势ID
 * @param {boolean} isCorrect - 是否正确
 * @param {number} confidence - 置信度
 */
export async function getPracticeFeedback(gestureId, isCorrect, confidence) {
  try {
    const result = await requestJson('/ai/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        gesture_id: gestureId,
        is_correct: isCorrect,
        confidence: confidence
      })
    })

    if (result.ok) {
      return result.data
    }
    if (result.status === 404 || result.status === 405) {
      return getLocalPracticeFeedback(gestureId, isCorrect, confidence)
    }
    return {
      error: result.data?.error || result.data?.message || `获取反馈失败（${result.status}）`,
      status: 'retry',
      message: '请调整手势后重试',
      stars: 0
    }
  } catch (error) {
    console.error('Failed to get feedback:', error)
    return getLocalPracticeFeedback(gestureId, isCorrect, confidence)
  }
}

/**
 * 获取视频流URL
 */
export function getStreamUrl() {
  return `${API_BASE_URL}/stream`
}

function getLocalLearningAdvice(completedGestures = []) {
  const completedCount = Array.isArray(completedGestures) ? completedGestures.length : 0
  if (completedCount < 3) {
    return {
      level: 'beginner',
      message: '建议先练习数字和问候类手势，每天坚持10分钟。',
      next_gestures: ['one', 'two', 'three', 'thumbs_up']
    }
  }
  if (completedCount < 8) {
    return {
      level: 'intermediate',
      message: '基础不错，可以加入OK、我爱你等复杂手势练习。',
      next_gestures: ['ok', 'six', 'i_love_you']
    }
  }
  return {
    level: 'advanced',
    message: '建议进入连续识别与场景化练习，提升稳定性与速度。',
    next_gestures: []
  }
}

function getLocalPracticeFeedback(gestureId, isCorrect, confidence = 0) {
  if (isCorrect && confidence >= 0.9) {
    return {
      status: 'excellent',
      message: '太棒了，动作非常标准。',
      stars: 3
    }
  }
  if (isCorrect && confidence >= 0.7) {
    return {
      status: 'good',
      message: '识别成功，继续保持。',
      stars: 2
    }
  }
  if (isCorrect) {
    return {
      status: 'pass',
      message: `已识别到 ${gestureId}，建议再把动作做得更清晰。`,
      stars: 1
    }
  }
  return {
    status: 'retry',
    message: '本次未通过，请调整手势角度和手指张开程度后再试。',
    stars: 0
  }
}

export default {
  checkHealth,
  getGestures,
  recognizeGesture,
  verifyGesture,
  aiChat,
  getGestureExplanation,
  getLearningAdvice,
  getPracticeFeedback,
  getStreamUrl
}
