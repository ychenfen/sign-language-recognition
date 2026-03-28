<template>
  <el-card class="ai-chat-card">
    <template #header>
      <div class="card-header">
        <span>🤖 AI手语助手</span>
        <el-tag :type="serviceTagType" size="small">{{ serviceTagText }}</el-tag>
      </div>
    </template>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">👋</div>
        <h3>你好！我是手语学习助手</h3>
        <p>你可以问我关于手语的任何问题，比如：</p>
        <div class="quick-questions">
          <el-button
            v-for="q in quickQuestions"
            :key="q"
            size="small"
            @click="sendMessage(q)"
          >
            {{ q }}
          </el-button>
        </div>
      </div>

      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(msg.content)"></div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>

      <div v-if="isLoading" class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <el-input
        v-model="inputMessage"
        placeholder="输入你的问题..."
        @keyup.enter="sendCurrentMessage"
        :disabled="isLoading"
      >
        <template #append>
          <el-button
            type="primary"
            @click="sendCurrentMessage"
            :loading="isLoading"
            :icon="Send"
          >
            发送
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 功能按钮 -->
    <div class="chat-actions">
      <el-button size="small" @click="getLearningAdvice" :loading="adviceLoading">
        📚 学习建议
      </el-button>
      <el-button size="small" @click="clearHistory">
        🗑️ 清空对话
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Promotion as Send } from '@element-plus/icons-vue'
import { aiChat, checkHealth, getLearningAdvice as getAdvice } from '../api/gestureApi.js'

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const isConnected = ref(false)
const adviceLoading = ref(false)
const messagesContainer = ref(null)
let connectionTimer = null

const serviceTagType = computed(() => (isConnected.value ? 'success' : 'info'))
const serviceTagText = computed(() => (isConnected.value ? '服务可用' : '离线知识'))

const quickQuestions = [
  '点赞手势怎么做？',
  '数字1-5的手语',
  '学习手语有什么建议？',
  'OK手势怎么比划？'
]

// 检查API连接状态
async function checkConnection() {
  try {
    const result = await checkHealth()
    isConnected.value = result.status === 'ok'
  } catch (error) {
    isConnected.value = false
  }
}

// 格式化消息（支持简单markdown）
function formatMessage(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/(\d+)\./g, '<br>$1.')
}

// 获取当前时间
function getCurrentTime() {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 滚动到底部
async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 发送消息
async function sendMessage(message) {
  if (!message.trim()) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    time: getCurrentTime()
  })

  inputMessage.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    // 构建对话历史
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content
    }))

    const result = await aiChat(message, history.length > 0 ? history : null)

    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: result.reply || '抱歉，我没能理解你的问题。',
      time: getCurrentTime()
    })
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，服务暂时不可用，请稍后再试。',
      time: getCurrentTime()
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

// 发送当前输入的消息
function sendCurrentMessage() {
  sendMessage(inputMessage.value)
}

// 获取学习建议
async function getLearningAdvice() {
  adviceLoading.value = true
  try {
    // 这里可以传入用户已学习的手势
    const result = await getAdvice(['one', 'two', 'three'])

    if (result.message) {
      messages.value.push({
        role: 'assistant',
        content: `📚 **学习建议**\n\n${result.message}\n\n**推荐学习**: ${result.next_gestures?.join(', ') || '继续练习'}`,
        time: getCurrentTime()
      })
      await scrollToBottom()
    }
  } catch (error) {
    ElMessage.error('获取学习建议失败')
  } finally {
    adviceLoading.value = false
  }
}

// 清空对话历史
function clearHistory() {
  messages.value = []
  ElMessage.success('对话已清空')
}

onMounted(() => {
  checkConnection()
  // 定期检查连接状态
  connectionTimer = setInterval(checkConnection, 30000)
})

onUnmounted(() => {
  if (connectionTimer) {
    clearInterval(connectionTimer)
    connectionTimer = null
  }
})
</script>

<style scoped>
.ai-chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-messages {
  flex: 1;
  min-height: 300px;
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.welcome-message {
  text-align: center;
  padding: 20px;
  color: #666;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-message h3 {
  margin-bottom: 8px;
  color: #333;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
}

.message {
  display: flex;
  margin-bottom: 16px;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-content {
  max-width: 70%;
}

.message-text {
  background: #fff;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  line-height: 1.6;
}

.message.user .message-text {
  background: #409eff;
  color: #fff;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.message.user .message-time {
  text-align: left;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #ccc;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

.chat-input {
  margin-bottom: 12px;
}

.chat-actions {
  display: flex;
  gap: 8px;
}
</style>
