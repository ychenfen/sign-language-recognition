/**
 * Gesture Recognition API Service
 * 优先走 Flask 后端；当后端不可用时，为前端提供本地知识兜底。
 */

import { signVocabulary, matchesVocabularyKeyword, normalizeSearchText } from '../data/signResources'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

const EXTRA_GESTURE_KNOWLEDGE = [
  {
    id: 'thumbs_up',
    title: '点赞',
    pinyin: 'diǎn zàn',
    description: '表示赞同、鼓励、夸奖或确认。',
    keywords: ['点赞', '比赞', '竖大拇指'],
    steps: [
      '握拳，四指自然收拢。',
      '拇指向上竖起，保持手背朝外或侧向镜头。',
      '手腕放松，动作停稳 1 到 2 秒。'
    ],
    examples: ['夸别人做得好时可以使用', '识别时尽量让拇指和其他手指区分清楚']
  },
  {
    id: 'ok',
    title: 'OK',
    pinyin: 'o k',
    description: '表示“可以、没问题、很好”。',
    keywords: ['ok', 'OK', 'ok手势', '手势ok'],
    steps: [
      '拇指和食指轻触成圆圈。',
      '中指、无名指、小指自然伸直。',
      '手型不要压得太扁，圆圈和三根伸直手指要清晰可见。'
    ],
    examples: ['确认事情没问题时使用', '练习时注意圆圈不要完全闭死']
  },
  {
    id: 'numbers_1_5',
    title: '数字 1-5',
    description: '建议按从单指到五指的顺序逐个练习，先保证手指展开清楚，再提高速度。',
    keywords: ['数字1-5', '数字一到五', '数字12345', '1-5', '一到五'],
    steps: [
      '1：伸出食指，其余手指收拢。',
      '2：伸出食指和中指，保持分开。',
      '3：伸出拇指、食指、中指。',
      '4：除拇指外四指伸开。',
      '5：五指自然张开，掌心朝前。'
    ],
    examples: ['练习时每个数字保持 2 到 3 秒', '识别时尽量把整只手放在画面中央']
  }
]

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

function buildStepText(steps = []) {
  return steps.map((step, index) => `${index + 1}. ${step}`).join('\n')
}

function buildExampleText(examples = []) {
  if (!Array.isArray(examples) || examples.length === 0) {
    return ''
  }
  return `\n\n使用场景：\n${examples.map(example => `- ${example}`).join('\n')}`
}

function buildKnowledgeReply(entry) {
  if (!entry) return ''

  const header = `**${entry.title || entry.word}**`
  const pinyin = entry.pinyin ? `\n拼音：${entry.pinyin}` : ''
  const description = entry.description ? `\n说明：${entry.description}` : ''
  const steps = Array.isArray(entry.steps) && entry.steps.length > 0
    ? `\n\n动作提示：\n${buildStepText(entry.steps)}`
    : ''
  const examples = buildExampleText(entry.examples)
  return `${header}${pinyin}${description}${steps}${examples}`.trim()
}

function findSpecialKnowledge(message, normalizedMessage) {
  if (
    /数字\s*[1一]\s*[-到至]\s*[5五]/.test(message) ||
    normalizedMessage.includes('数字15') ||
    normalizedMessage.includes('数字12345')
  ) {
    return EXTRA_GESTURE_KNOWLEDGE.find(item => item.id === 'numbers_1_5')
  }

  return EXTRA_GESTURE_KNOWLEDGE.find(item =>
    item.keywords.some(keyword => normalizedMessage.includes(normalizeSearchText(keyword)))
  ) || null
}

function findVocabularyByMessage(message, normalizedMessage) {
  const directMatches = signVocabulary
    .filter(item => normalizedMessage.includes(normalizeSearchText(item.word)))
    .sort((left, right) => right.word.length - left.word.length)

  if (directMatches.length > 0) {
    return directMatches[0]
  }

  return signVocabulary.find(item => matchesVocabularyKeyword(item, message)) || null
}

function buildLearningReply() {
  return [
    '**手语入门建议**',
    '',
    '1. 先练基础高频词，例如“谢谢、帮助、爸爸、妈妈”。',
    '2. 每次只练 3 到 5 个词，先对照图片和视频把手型做标准。',
    '3. 练习时面对镜子或摄像头，重点看手指张开是否清楚。',
    '4. 学完单词后，马上放进短句里重复，例如“谢谢你”“请帮助我”。'
  ].join('\n')
}

function buildRecognitionHelpReply() {
  return [
    '识别页先看顶部模式提示：',
    '1. 后端模式需要 Python 服务已启动。',
    '2. 浏览器本地模式需要允许摄像头权限。',
    '3. 如果页面已经切到浏览器模式但仍不可用，先刷新页面，再确认浏览器没有拦截摄像头。'
  ].join('\n')
}

function getLocalChatReply(message) {
  const normalizedMessage = normalizeSearchText(message)
  if (!normalizedMessage) return ''

  if (
    message.includes('学习建议') ||
    message.includes('怎么学') ||
    message.includes('如何学') ||
    message.includes('入门') ||
    message.includes('初学')
  ) {
    return buildLearningReply()
  }

  const specialKnowledge = findSpecialKnowledge(message, normalizedMessage)
  if (specialKnowledge) {
    return buildKnowledgeReply(specialKnowledge)
  }

  const vocabularyEntry = findVocabularyByMessage(message, normalizedMessage)
  if (vocabularyEntry) {
    return buildKnowledgeReply(vocabularyEntry)
  }

  if (message.includes('识别') && message.includes('不能用')) {
    return buildRecognitionHelpReply()
  }

  return '我可以直接回答常见手语词汇、点赞、OK、数字 1-5 和学习建议。你也可以直接问“谢谢怎么做”或“奶奶的手势是什么”。'
}

function getLocalGestureExplanation(gestureId) {
  const normalizedGestureId = normalizeSearchText(gestureId)
  const specialKnowledge = EXTRA_GESTURE_KNOWLEDGE.find(item =>
    normalizeSearchText(item.id).includes(normalizedGestureId) ||
    normalizeSearchText(item.title).includes(normalizedGestureId)
  )

  if (specialKnowledge) {
    return {
      gesture: gestureId,
      explanation: buildKnowledgeReply(specialKnowledge),
      source: 'local'
    }
  }

  const vocabularyEntry = signVocabulary.find(item =>
    normalizeSearchText(item.word) === normalizedGestureId ||
    normalizeSearchText(item.pinyin) === normalizedGestureId
  )

  if (vocabularyEntry) {
    return {
      gesture: gestureId,
      explanation: buildKnowledgeReply(vocabularyEntry),
      source: 'local'
    }
  }

  return {
    gesture: gestureId,
    explanation: '暂时没有找到对应手势的本地解释，可以换成中文词汇名称再试。',
    source: 'local'
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
  const localReply = getLocalChatReply(message)
  const hasSpecificLocalKnowledge = localReply && !localReply.includes('我可以直接回答常见手语词汇')

  if (hasSpecificLocalKnowledge) {
    return {
      status: 'ok',
      reply: localReply,
      source: 'local'
    }
  }

  try {
    const result = await requestJson('/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message, history })
    })

    if (result.ok && result.data?.reply) {
      return result.data
    }

    return {
      status: 'error',
      reply: localReply || result.data?.reply || result.data?.error || '抱歉，AI 服务暂时不可用，请稍后再试。'
    }
  } catch (error) {
    console.error('AI chat failed:', error)
    return {
      status: 'error',
      reply: localReply || '抱歉，AI 服务暂时不可用，请稍后再试。'
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
    if (result.status === 404 || result.status === 405) {
      return getLocalGestureExplanation(gestureId)
    }
    return {
      error: result.data?.error || result.data?.message || `获取解释失败（${result.status}）`
    }
  } catch (error) {
    console.error('Failed to get explanation:', error)
    return getLocalGestureExplanation(gestureId)
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
        confidence
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
      message: '建议先练习高频基础词和家庭称谓，每天坚持 10 到 15 分钟。',
      next_gestures: ['谢谢', '帮助', '爸爸', '妈妈']
    }
  }
  if (completedCount < 8) {
    return {
      level: 'intermediate',
      message: '可以开始把单词放进短句，并加入情绪表达类手势练习。',
      next_gestures: ['高兴', '难受', '奶奶', '姥爷']
    }
  }
  return {
    level: 'advanced',
    message: '建议进入场景化练习，例如问候、家庭介绍、情绪表达和连续识别。',
    next_gestures: ['爱', '对不起', '没关系']
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
