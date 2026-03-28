<template>
  <div class="sign-test">
    <!-- 测试模式选择 -->
    <div class="test-modes" v-if="!isTestStarted">
      <div class="page-header">
        <h2>选择测试模式</h2>
        <p class="subtitle">挑战自我，检验学习成果</p>
      </div>

      <div class="mode-grid">
        <!-- 基础测试 -->
        <div
          class="mode-card"
          :class="{ 'mode-basic': true }"
          :style="{ '--delay': '0s' }"
          @click="startTest('easy')"
        >
          <div class="card-watermark">基</div>
          <div class="card-content">
            <div class="card-badge">入门推荐</div>
            <h3>基础测试</h3>
            <p>适合初学者，包含简单的数字和问候语</p>
            <div class="card-meta">
              <span>10题</span>
              <span>单选题</span>
            </div>
          </div>
          <div class="card-hover-border"></div>
        </div>

        <!-- 进阶测试 -->
        <div
          class="mode-card mode-pro"
          :style="{ '--delay': '0.1s' }"
          @click="startTest('medium')"
        >
          <div class="card-watermark">进</div>
          <div class="card-content">
            <h3>进阶测试</h3>
            <p>包含日常交流用语，难度适中</p>
            <div class="card-meta">
              <span>15题</span>
              <span>单选题</span>
            </div>
          </div>
          <div class="card-hover-border"></div>
        </div>

        <!-- 挑战模式 -->
        <div
          class="mode-card mode-challenge"
          :style="{ '--delay': '0.2s' }"
          @click="startTest('hard')"
        >
          <div class="card-watermark">挑</div>
          <div class="card-content">
            <div class="card-badge challenge">高难度</div>
            <h3>挑战模式</h3>
            <p>综合所有词汇，限时作答</p>
            <div class="card-meta">
              <span>20题</span>
              <span>限时60秒/题</span>
            </div>
          </div>
          <div class="card-hover-border"></div>
        </div>

        <!-- 错题本 -->
        <div
          class="mode-card mode-review"
          :style="{ '--delay': '0.3s' }"
          @click="showWrongBook = true"
        >
          <div class="card-watermark">错</div>
          <div class="card-content">
            <h3>错题本练习</h3>
            <p>针对错题进行专项练习，巩固薄弱点</p>
            <div class="card-meta">
              <span>{{ wrongBookList.length }}题</span>
              <span>巩固提高</span>
            </div>
          </div>
          <div class="card-hover-border"></div>
        </div>
      </div>

      <!-- 成就展示 -->
      <div class="achievements-section">
        <div class="section-header">
          <h3>我的成就</h3>
          <span class="achievement-progress">{{ unlockedCount }}/{{ achievements.length }}</span>
        </div>
        <div class="achievement-grid">
          <div
            v-for="(ach, index) in achievements"
            :key="ach.id"
            :class="['achievement-card', { unlocked: ach.unlocked }]"
            :style="{ '--delay': (index * 0.05) + 's' }"
          >
            <div class="ach-icon">{{ ach.icon }}</div>
            <div class="ach-info">
              <span class="ach-name">{{ ach.name }}</span>
              <span class="ach-desc">{{ ach.description }}</span>
            </div>
            <div class="ach-status">
              <el-icon v-if="ach.unlocked" class="status-check"><Check /></el-icon>
              <el-icon v-else class="status-lock"><Lock /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试进行中 -->
    <div class="test-panel" v-else>
      <!-- 进度条 -->
      <div class="test-header">
        <div class="progress-info">
          <span class="progress-text">第 <strong>{{ currentIndex + 1 }}</strong> / {{ questions.length }} 题</span>
          <span v-if="testMode === 'hard'" :class="['timer', { warning: timeLeft <= 10 }]">
            <el-icon><Clock /></el-icon>
            剩余 {{ timeLeft }}s
          </span>
        </div>
        <el-progress
          :percentage="progressPercent"
          :stroke-width="6"
          :show-text="false"
          :color="progressColor"
        />
      </div>

      <!-- 题目 -->
      <div class="question-area">
        <div class="question-content">
          <h3>请选择下面手语图片对应的词汇</h3>
          <div class="sign-image">
            <img
              v-if="currentQuestion?.image"
              :src="currentQuestion.image"
              :alt="currentQuestion.answer"
              class="question-sign-image"
              @error="handleQuestionImageError"
            />
            <div v-else class="image-placeholder">暂无手语图片</div>
          </div>
        </div>

        <!-- 选项 -->
        <div class="options-grid">
          <div
            v-for="(option, index) in currentQuestion?.options"
            :key="index"
            :class="['option-item', {
              selected: selectedAnswer === option,
              correct: showResult && option === currentQuestion.answer,
              wrong: showResult && selectedAnswer === option && option !== currentQuestion.answer
            }]"
            @click="selectAnswer(option)"
          >
            <span class="option-label">{{ ['A', 'B', 'C', 'D'][index] }}</span>
            <span class="option-text">{{ option }}</span>
            <span class="option-indicator" v-if="showResult && option === currentQuestion.answer">
              <el-icon><Check /></el-icon>
            </span>
          </div>
        </div>

        <!-- 结果反馈 -->
        <transition name="fade">
          <div class="result-feedback" v-if="showResult">
            <div :class="['feedback-box', isCorrect ? 'correct' : 'wrong']">
              <el-icon class="feedback-icon">
                <component :is="isCorrect ? 'CircleCheck' : 'CircleClose'" />
              </el-icon>
              <span class="feedback-text">{{ isCorrect ? '回答正确！' : '回答错误' }}</span>
              <p v-if="!isCorrect" class="correct-answer">正确答案: {{ currentQuestion.answer }}</p>
            </div>
          </div>
        </transition>
      </div>

      <!-- 操作按钮 -->
      <div class="test-actions">
        <el-button @click="exitTest" size="large">
          <el-icon><Close /></el-icon>
          退出测试
        </el-button>
        <el-button type="primary" @click="nextQuestion" :disabled="!selectedAnswer" size="large">
          {{ currentIndex === questions.length - 1 ? '提交测试' : '下一题' }}
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 测试结果 -->
    <el-dialog v-model="showResultDialog" title="测试结果" width="480px" :close-on-click-modal="false" class="result-dialog">
      <div class="result-content">
        <div :class="['score-circle', getScoreLevel()]">
          <div class="score-inner">
            <span class="score">{{ score }}</span>
            <span class="total">/ {{ questions.length }}</span>
          </div>
          <svg class="score-ring" viewBox="0 0 120 120">
            <circle class="ring-bg" cx="60" cy="60" r="54" />
            <circle
              class="ring-progress"
              cx="60" cy="60" r="54"
              :style="{ strokeDashoffset: ringOffset }"
            />
          </svg>
        </div>

        <div class="result-stats">
          <div class="result-item">
            <span class="label">正确率</span>
            <span class="value">{{ Math.round((score / questions.length) * 100) }}%</span>
          </div>
          <div class="result-item">
            <span class="label">用时</span>
            <span class="value">{{ formatTime(usedTime) }}</span>
          </div>
          <div class="result-item">
            <span class="label">难度</span>
            <span class="value">{{ getDifficultyText(testMode) }}</span>
          </div>
        </div>

        <div :class="['result-message', getScoreLevel()]">
          {{ getResultMessage() }}
        </div>

        <transition name="bounce">
          <div class="new-achievement" v-if="newAchievement">
            <span class="achievement-label">获得新成就</span>
            <div class="achievement-badge">
              <span class="badge-icon">{{ newAchievement.icon }}</span>
              <span class="badge-name">{{ newAchievement.name }}</span>
            </div>
          </div>
        </transition>
      </div>
      <template #footer>
        <el-button @click="showResultDialog = false; isTestStarted = false" size="large">返回</el-button>
        <el-button type="primary" @click="restartTest" size="large">再测一次</el-button>
      </template>
    </el-dialog>

    <!-- 错题本 -->
    <el-dialog v-model="showWrongBook" title="错题本" width="600px" class="wrong-book-dialog">
      <div class="wrong-book-list" v-if="wrongBookList.length > 0">
        <div v-for="(item, index) in wrongBookList" :key="index" class="wrong-item">
          <div class="wrong-question">
            <span class="q-num">{{ index + 1 }}.</span>
            <span class="q-word">{{ item.answer }}</span>
          </div>
          <div class="wrong-info">
            <span class="user-answer">你的答案: <em>{{ item.userAnswer }}</em></span>
            <span class="wrong-count">错误 {{ item.wrongCount }} 次</span>
          </div>
          <el-button size="small" type="danger" plain @click="removeFromWrongBook(index)">
            <el-icon><Delete /></el-icon>
            移除
          </el-button>
        </div>
      </div>
      <el-empty v-else description="太棒了！没有错题" :image-size="100">
        <template #image>
          <div class="empty-icon">🎉</div>
        </template>
      </el-empty>
      <template #footer>
        <el-button @click="showWrongBook = false">关闭</el-button>
        <el-button type="primary" @click="practiceWrongBook" :disabled="wrongBookList.length === 0">
          开始练习
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Lock, Clock, Close, ArrowRight, Delete, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { getWords, userScopedKey } from '../data/appDataStore'

const isTestStarted = ref(false)
const testMode = ref('')
const questions = ref([])
const currentIndex = ref(0)
const selectedAnswer = ref(null)
const showResult = ref(false)
const isCorrect = ref(false)
const score = ref(0)
const showResultDialog = ref(false)
const showWrongBook = ref(false)
const wrongBookList = ref([])
const timeLeft = ref(60)
const usedTime = ref(0)
const newAchievement = ref(null)
let timer = null
let startTime = null

const achievements = ref([
  { id: 1, name: '初试牛刀', icon: '🎯', description: '完成首次测试', unlocked: false },
  { id: 2, name: '小有所成', icon: '⭐', description: '单次测试正确率达80%', unlocked: false },
  { id: 3, name: '精益求精', icon: '🏆', description: '单次测试全部正确', unlocked: false },
  { id: 4, name: '勤学不倦', icon: '📚', description: '累计完成10次测试', unlocked: false },
  { id: 5, name: '挑战达人', icon: '🔥', description: '通过挑战模式', unlocked: false },
  { id: 6, name: '知错能改', icon: '✨', description: '清空错题本', unlocked: false }
])

const MODE_CATEGORIES = {
  easy: ['基础词汇', '情绪表达'],
  medium: ['基础词汇', '情绪表达', '家庭称谓'],
  hard: null
}

const QUESTION_LIMITS = {
  easy: 10,
  medium: 15,
  hard: 20
}

const unlockedCount = computed(() => {
  return achievements.value.filter(a => a.unlocked).length
})

const progressPercent = computed(() => {
  return Math.round(((currentIndex.value + 1) / questions.value.length) * 100)
})

const progressColor = computed(() => {
  if (testMode.value === 'easy') return '#10b981'
  if (testMode.value === 'medium') return '#3b82f6'
  if (testMode.value === 'hard') return '#8b5cf6'
  return '#6366f1'
})

const ringOffset = computed(() => {
  const circumference = 2 * Math.PI * 54
  const percent = score.value / questions.value.length
  return circumference * (1 - percent)
})

const currentQuestion = computed(() => {
  return questions.value[currentIndex.value]
})

const getWordBank = () => {
  return getWords().filter(item => item.image)
}

const shuffleArray = (items = []) => {
  return [...items].sort(() => Math.random() - 0.5)
}

const getAllWords = () => {
  return getWordBank().map(item => item.word)
}

const getPoolByMode = (mode) => {
  const bank = getWordBank()
  if (mode === 'hard') {
    return bank
  }

  const categories = MODE_CATEGORIES[mode] || []
  return bank.filter(item => categories.includes(item.category))
}

const normalizeWrongBookItem = (item, index = 0) => {
  const bank = getWordBank()
  const correctAnswer = item.correctAnswer || item.answer || ''
  const matchedWord = bank.find(word => word.id === item.wordId || word.word === correctAnswer)

  return {
    wordId: item.wordId || matchedWord?.id || Date.now() + index,
    question: item.question || '请选择下面手语图片对应的词汇',
    answer: correctAnswer,
    correctAnswer,
    image: item.image || matchedWord?.image || '',
    category: item.category || matchedWord?.category || '错题',
    userAnswer: item.userAnswer || '',
    wrongCount: Number(item.wrongCount || 1)
  }
}

const getScoreLevel = () => {
  const accuracy = score.value / questions.value.length
  if (accuracy >= 0.9) return 'excellent'
  if (accuracy >= 0.7) return 'good'
  if (accuracy >= 0.5) return 'pass'
  return 'fail'
}

const generateQuestions = (mode) => {
  if (mode === 'wrongBook') {
    return wrongBookList.value.map(item => ({
      id: item.wordId,
      answer: item.correctAnswer || item.answer,
      image: item.image,
      category: item.category,
      options: generateOptions(item.answer, getAllWords())
    }))
  }

  const wordPool = getPoolByMode(mode)
  const questionCount = Math.min(QUESTION_LIMITS[mode] || wordPool.length, wordPool.length)

  return shuffleArray(wordPool).slice(0, questionCount).map(item => ({
    id: item.id,
    answer: item.word,
    image: item.image,
    category: item.category,
    options: generateOptions(item.word, getAllWords())
  }))
}

const generateOptions = (answer, pool) => {
  const options = new Set([answer])
  const otherWords = shuffleArray(pool.filter(word => word !== answer))

  while (options.size < 4 && otherWords.length > 0) {
    options.add(otherWords.shift())
  }

  return shuffleArray(Array.from(options))
}

const startTest = (mode) => {
  const generatedQuestions = generateQuestions(mode)
  if (generatedQuestions.length === 0) {
    ElMessage.warning(mode === 'wrongBook' ? '错题本暂时没有可练习的题目' : '当前题库不足，无法开始测试')
    return
  }

  testMode.value = mode
  questions.value = generatedQuestions
  currentIndex.value = 0
  selectedAnswer.value = null
  showResult.value = false
  score.value = 0
  usedTime.value = 0
  isTestStarted.value = true
  startTime = Date.now()

  if (mode === 'hard') {
    timeLeft.value = 60
    startTimer()
  }
}

const practiceWrongBook = () => {
  showWrongBook.value = false
  startTest('wrongBook')
}

const startTimer = () => {
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      if (!selectedAnswer.value) {
        selectedAnswer.value = ''
      }
      nextQuestion()
      timeLeft.value = 60
    }
  }, 1000)
}

const selectAnswer = (option) => {
  if (showResult.value) return
  selectedAnswer.value = option
  showResult.value = true
  isCorrect.value = option === currentQuestion.value.answer

  if (isCorrect.value) {
    score.value++
  } else {
    addToWrongBook(currentQuestion.value, option)
  }
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    selectedAnswer.value = null
    showResult.value = false
    isCorrect.value = false
    if (testMode.value === 'hard') {
      timeLeft.value = 60
    }
  } else {
    finishTest()
  }
}

const finishTest = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  usedTime.value = Math.round((Date.now() - startTime) / 1000)
  checkAchievements()
  showResultDialog.value = true
  saveTestRecord()
}

const checkAchievements = () => {
  newAchievement.value = null
  const accuracy = score.value / questions.value.length

  if (!achievements.value[0].unlocked) {
    achievements.value[0].unlocked = true
    newAchievement.value = achievements.value[0]
  }

  if (accuracy >= 0.8 && !achievements.value[1].unlocked) {
    achievements.value[1].unlocked = true
    newAchievement.value = achievements.value[1]
  }

  if (accuracy === 1 && !achievements.value[2].unlocked) {
    achievements.value[2].unlocked = true
    newAchievement.value = achievements.value[2]
  }

  if (testMode.value === 'hard' && accuracy >= 0.6 && !achievements.value[4].unlocked) {
    achievements.value[4].unlocked = true
    newAchievement.value = achievements.value[4]
  }

  saveAchievements()
}

const exitTest = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  isTestStarted.value = false
}

const restartTest = () => {
  showResultDialog.value = false
  startTest(testMode.value)
}

const addToWrongBook = (question, userAnswer) => {
  const existing = wrongBookList.value.find(item => item.answer === question.answer)
  if (existing) {
    existing.wrongCount++
    existing.userAnswer = userAnswer
    existing.image = question.image || existing.image
  } else {
    wrongBookList.value.push({
      wordId: question.id,
      question: '请选择下面手语图片对应的词汇',
      answer: question.answer,
      correctAnswer: question.answer,
      image: question.image,
      category: question.category,
      userAnswer,
      wrongCount: 1
    })
  }
  saveWrongBook()
}

const removeFromWrongBook = (index) => {
  wrongBookList.value.splice(index, 1)
  saveWrongBook()

  if (wrongBookList.value.length === 0 && !achievements.value[5].unlocked) {
    achievements.value[5].unlocked = true
    ElMessage.success('获得成就: 知错能改 ✨')
    saveAchievements()
  }
}

const formatTime = (seconds) => {
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return `${min}分${sec}秒`
}

const getDifficultyText = (mode) => {
  const map = { easy: '基础', medium: '进阶', hard: '挑战', wrongBook: '错题' }
  return map[mode] || ''
}

const getResultMessage = () => {
  const accuracy = score.value / questions.value.length
  if (accuracy === 1) return '太棒了！完美通关！'
  if (accuracy >= 0.8) return '非常优秀！继续保持！'
  if (accuracy >= 0.6) return '不错哦，再接再厉！'
  return '加油，多多练习！'
}

const saveWrongBook = () => {
  localStorage.setItem(userScopedKey('wrongBook'), JSON.stringify(wrongBookList.value))
}

const saveAchievements = () => {
  localStorage.setItem(userScopedKey('testAchievements'), JSON.stringify(achievements.value))
}

const saveTestRecord = () => {
  const records = JSON.parse(localStorage.getItem(userScopedKey('testRecords')) || '[]')
  records.push({
    mode: testMode.value,
    score: score.value,
    total: questions.value.length,
    time: usedTime.value,
    date: new Date().toLocaleString()
  })
  localStorage.setItem(userScopedKey('testRecords'), JSON.stringify(records.slice(-50)))

  if (records.length >= 10 && !achievements.value[3].unlocked) {
    achievements.value[3].unlocked = true
    saveAchievements()
  }
}

const handleQuestionImageError = (event) => {
  event.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320"><rect fill="%23eef2ff" width="320" height="320" rx="24"/><text x="160" y="155" text-anchor="middle" fill="%236366f1" font-size="24">手语图片加载失败</text><text x="160" y="190" text-anchor="middle" fill="%2394a3b8" font-size="16">请检查资源文件</text></svg>'
}

onMounted(() => {
  const savedWrongBook = localStorage.getItem(userScopedKey('wrongBook'))
  if (savedWrongBook) {
    try {
      const parsed = JSON.parse(savedWrongBook)
      wrongBookList.value = Array.isArray(parsed)
        ? parsed.map((item, index) => normalizeWrongBookItem(item, index))
        : []
    } catch (error) {
      wrongBookList.value = []
    }
  }

  const savedAchievements = localStorage.getItem(userScopedKey('testAchievements'))
  if (savedAchievements) {
    try {
      const parsed = JSON.parse(savedAchievements)
      achievements.value = Array.isArray(parsed) ? parsed : achievements.value
    } catch (error) {
      achievements.value = achievements.value
    }
  }
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.sign-test {
  padding: 32px;
  --color-basic: #10b981;
  --color-basic-bg: rgba(16, 185, 129, 0.04);
  --color-pro: #3b82f6;
  --color-pro-bg: rgba(59, 130, 246, 0.04);
  --color-challenge: #8b5cf6;
  --color-challenge-bg: rgba(139, 92, 246, 0.04);
  --color-review: #f97316;
  --color-review-bg: rgba(249, 115, 22, 0.04);
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h2 {
  font-size: 26px;
  color: #1e293b;
  margin: 0 0 8px;
  font-weight: 600;
}

.page-header .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* 测试模式卡片 - 去AI味重构 */
.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 48px;
}

.mode-card {
  position: relative;
  background: #fff;
  border: 1px solid transparent;
  border-radius: 16px;
  padding: 28px 24px;
  cursor: pointer;
  transition: all 0.25s ease;
  overflow: hidden;
  animation: staggerFadeIn 0.4s ease-out backwards;
  animation-delay: var(--delay);
}

@keyframes staggerFadeIn {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 水印文字 - 替代圆形图标 */
.card-watermark {
  position: absolute;
  top: -20px;
  right: -10px;
  font-size: 120px;
  font-weight: 800;
  opacity: 0.03;
  transition: all 0.3s ease;
  pointer-events: none;
  line-height: 1;
}

.mode-card:hover .card-watermark {
  opacity: 0.08;
  transform: scale(1.05);
}

/* 卡片主题色 - 浅背景 */
.mode-basic {
  background: var(--color-basic-bg);
}
.mode-basic .card-watermark { color: var(--color-basic); }

.mode-pro {
  background: var(--color-pro-bg);
}
.mode-pro .card-watermark { color: var(--color-pro); }

.mode-challenge {
  background: var(--color-challenge-bg);
}
.mode-challenge .card-watermark { color: var(--color-challenge); }

.mode-review {
  background: var(--color-review-bg);
}
.mode-review .card-watermark { color: var(--color-review); }

/* Hover边框效果 */
.card-hover-border {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  border: 2px solid transparent;
  transition: all 0.25s ease;
  pointer-events: none;
}

.mode-basic:hover .card-hover-border {
  border-color: var(--color-basic);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.12);
}

.mode-pro:hover .card-hover-border {
  border-color: var(--color-pro);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12);
}

.mode-challenge:hover .card-hover-border {
  border-color: var(--color-challenge);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.12);
}

.mode-review:hover .card-hover-border {
  border-color: var(--color-review);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.12);
}

.mode-card:hover {
  transform: translateY(-4px);
}

.card-content {
  position: relative;
  z-index: 1;
}

.card-badge {
  display: inline-block;
  padding: 4px 10px;
  background: var(--color-basic);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
  margin-bottom: 12px;
}

.card-badge.challenge {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
}

.card-content h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #1e293b;
  font-weight: 600;
}

.card-content p {
  margin: 0 0 16px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.card-meta {
  display: flex;
  gap: 16px;
}

.card-meta span {
  font-size: 12px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-meta span::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: currentColor;
}

/* 成就区域 - 毛玻璃未解锁 */
.achievements-section {
  background: #fafafa;
  border-radius: 16px;
  padding: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 17px;
  color: #1e293b;
  font-weight: 600;
}

.achievement-progress {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.achievement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.achievement-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 12px;
  transition: all 0.25s ease;
  animation: staggerFadeIn 0.4s ease-out backwards;
  animation-delay: var(--delay);
}

/* 未解锁 - 毛玻璃效果 */
.achievement-card:not(.unlocked) {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.achievement-card:not(.unlocked) .ach-icon {
  filter: grayscale(100%);
  opacity: 0.5;
}

.achievement-card:not(.unlocked) .ach-name,
.achievement-card:not(.unlocked) .ach-desc {
  opacity: 0.5;
}

/* 已解锁 */
.achievement-card.unlocked {
  background: #fff;
  border: 1px solid rgba(139, 92, 246, 0.15);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.06);
}

.ach-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-radius: 10px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.achievement-card.unlocked .ach-icon {
  background: linear-gradient(135deg, #ede9fe, #e0e7ff);
}

.ach-info {
  flex: 1;
  min-width: 0;
}

.ach-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.ach-desc {
  display: block;
  font-size: 12px;
  color: #64748b;
}

.ach-status {
  flex-shrink: 0;
}

.status-check {
  color: #10b981;
  font-size: 18px;
}

.status-lock {
  color: #cbd5e1;
  font-size: 16px;
}

/* 测试面板 */
.test-panel {
  max-width: 720px;
  margin: 0 auto;
}

.test-header {
  margin-bottom: 28px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-text {
  font-size: 14px;
  color: #64748b;
}

.progress-text strong {
  color: #1e293b;
  font-size: 18px;
}

.timer {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 14px;
  background: #f1f5f9;
  border-radius: 20px;
  transition: all 0.3s;
}

.timer.warning {
  color: #ef4444;
  background: #fef2f2;
  animation: shake 0.5s ease-in-out infinite;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  75% { transform: translateX(2px); }
}

.question-area {
  background: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
}

.question-content h3 {
  margin: 0 0 24px;
  font-size: 15px;
  color: #64748b;
  text-align: center;
  font-weight: 500;
}

.sign-image {
  display: flex;
  justify-content: center;
  margin-bottom: 28px;
}

.question-sign-image {
  width: min(100%, 280px);
  aspect-ratio: 1 / 1;
  border-radius: 20px;
  object-fit: contain;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid #e2e8f0;
  box-shadow: 0 12px 30px rgba(99, 102, 241, 0.08);
  padding: 16px;
}

.image-placeholder {
  width: min(100%, 280px);
  aspect-ratio: 1 / 1;
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  font-size: 18px;
  font-weight: 600;
  border: 1px dashed #c7d2fe;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: #fafafa;
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.option-item.selected {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.04);
}

.option-item.correct {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.04);
}

.option-item.wrong {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.04);
}

.option-label {
  width: 28px;
  height: 28px;
  background: #e2e8f0;
  color: #64748b;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.2s;
}

.option-item.selected .option-label {
  background: #6366f1;
  color: #fff;
}

.option-item.correct .option-label {
  background: #10b981;
  color: #fff;
}

.option-item.wrong .option-label {
  background: #ef4444;
  color: #fff;
}

.option-text {
  font-size: 15px;
  color: #1e293b;
  font-weight: 500;
  flex: 1;
}

.option-indicator {
  color: #10b981;
  font-size: 18px;
}

/* 结果反馈 */
.result-feedback {
  margin-top: 20px;
}

.feedback-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  border-radius: 12px;
  flex-wrap: wrap;
}

.feedback-box.correct {
  background: rgba(16, 185, 129, 0.08);
  color: #059669;
}

.feedback-box.wrong {
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
}

.feedback-icon {
  font-size: 22px;
}

.feedback-text {
  font-size: 15px;
  font-weight: 600;
}

.correct-answer {
  width: 100%;
  text-align: center;
  margin: 6px 0 0;
  font-size: 13px;
}

.test-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* 结果弹窗 */
.result-content {
  text-align: center;
  padding: 20px 0;
}

.score-circle {
  position: relative;
  width: 130px;
  height: 130px;
  margin: 0 auto 24px;
}

.score-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.score {
  font-size: 38px;
  font-weight: 700;
  color: #1e293b;
}

.total {
  font-size: 15px;
  color: #64748b;
}

.score-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: #f1f5f9;
  stroke-width: 8;
}

.ring-progress {
  fill: none;
  stroke: #6366f1;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 339.292;
  transition: stroke-dashoffset 1s ease-out;
}

.score-circle.excellent .ring-progress { stroke: #10b981; }
.score-circle.good .ring-progress { stroke: #3b82f6; }
.score-circle.pass .ring-progress { stroke: #f59e0b; }
.score-circle.fail .ring-progress { stroke: #ef4444; }

.result-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 20px;
}

.result-item {
  display: flex;
  flex-direction: column;
}

.result-item .label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.result-item .value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.result-message {
  font-size: 16px;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 20px;
  display: inline-block;
}

.result-message.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.result-message.good {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.result-message.pass {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.result-message.fail {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.new-achievement {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #faf5ff, #f5f3ff);
  border-radius: 12px;
  border: 1px solid rgba(139, 92, 246, 0.15);
}

.achievement-label {
  display: block;
  font-size: 11px;
  color: #7c3aed;
  margin-bottom: 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.achievement-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: #fff;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
}

.badge-icon {
  font-size: 18px;
}

.badge-name {
  font-size: 14px;
}

/* 错题本 */
.wrong-book-list {
  max-height: 400px;
  overflow-y: auto;
}

.wrong-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.2s;
}

.wrong-item:hover {
  background: #fafafa;
}

.wrong-item:last-child {
  border-bottom: none;
}

.wrong-question {
  display: flex;
  align-items: center;
  gap: 10px;
}

.q-num {
  color: #94a3b8;
  font-size: 14px;
}

.q-word {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.wrong-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  color: #64748b;
}

.user-answer em {
  color: #ef4444;
  font-style: normal;
  font-weight: 500;
}

.wrong-count {
  color: #94a3b8;
}

.empty-icon {
  font-size: 64px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s, transform 0.25s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.bounce-enter-active {
  animation: bounce-in 0.4s;
}

@keyframes bounce-in {
  0% { transform: scale(0.9); opacity: 0; }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); opacity: 1; }
}

/* 响应式 */
@media (max-width: 768px) {
  .sign-test {
    padding: 20px;
  }

  .mode-grid {
    grid-template-columns: 1fr;
  }

  .options-grid {
    grid-template-columns: 1fr;
  }

  .question-area {
    padding: 20px;
  }

  .result-stats {
    gap: 24px;
  }

  .achievement-grid {
    grid-template-columns: 1fr;
  }
}
</style>
