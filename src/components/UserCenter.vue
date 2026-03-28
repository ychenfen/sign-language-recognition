<template>
  <div class="user-center">
    <!-- 未登录状态 -->
    <div v-if="!isLoggedIn" class="auth-container">
      <el-card class="auth-card">
        <template #header>
          <div class="card-header">
            <span>{{ isLogin ? '用户登录' : '用户注册' }}</span>
          </div>
        </template>

        <el-form :model="authForm" :rules="authRules" ref="authFormRef" label-width="80px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="authForm.username" placeholder="请输入用户名" />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="authForm.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>

          <el-form-item v-if="!isLogin" label="确认密码" prop="confirmPassword">
            <el-input v-model="authForm.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleAuth" :loading="authLoading" style="width: 100%">
              {{ isLogin ? '登录' : '注册' }}
            </el-button>
          </el-form-item>

          <div class="auth-switch">
            <span v-if="isLogin">还没有账号？</span>
            <span v-else>已有账号？</span>
            <el-link type="primary" @click="isLogin = !isLogin">
              {{ isLogin ? '立即注册' : '立即登录' }}
            </el-link>
          </div>
        </el-form>
      </el-card>
    </div>

    <!-- 已登录状态 -->
    <div v-else class="profile-container">
      <!-- 用户信息卡片 -->
      <el-card class="profile-card">
        <div class="profile-header">
          <el-avatar :size="80" class="profile-avatar">{{ currentUser.username?.charAt(0) }}</el-avatar>
          <div class="profile-info">
            <h2>{{ currentUser.username }}</h2>
            <p class="role-tag">
              <el-tag v-if="currentUser.role === 'admin'" type="danger" size="small">管理员</el-tag>
              <el-tag v-else type="info" size="small">普通用户</el-tag>
            </p>
            <p class="register-time">注册时间：{{ currentUser.registerTime || '未知' }}</p>
          </div>
        </div>

        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-value">{{ favorites.length }}</div>
            <div class="stat-label">收藏词汇</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ learningHistory.length }}</div>
            <div class="stat-label">学习记录</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ wrongBook.length }}</div>
            <div class="stat-label">错题数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ achievements.length }}</div>
            <div class="stat-label">成就</div>
          </div>
        </div>
      </el-card>

      <!-- 功能标签页 -->
      <el-card class="content-card">
        <el-tabs v-model="activeTab">
          <!-- 我的收藏 -->
          <el-tab-pane label="我的收藏" name="favorites">
            <div v-if="favorites.length === 0" class="empty-state">
              <el-empty description="暂无收藏的词汇">
                <el-button type="primary" @click="$emit('go-to', 'dictionary')">去收藏</el-button>
              </el-empty>
            </div>
            <div v-else class="favorites-list">
              <div v-for="word in favorites" :key="word.id" class="favorite-item">
                <div class="word-info">
                  <span class="word-name">{{ word.word || word.name }}</span>
                  <span class="word-pinyin">{{ word.pinyin }}</span>
                </div>
                <div class="word-actions">
                  <el-button size="small" type="danger" text @click="removeFavorite(word.id)">取消收藏</el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 学习记录 -->
          <el-tab-pane label="学习记录" name="history">
            <div v-if="learningHistory.length === 0" class="empty-state">
              <el-empty description="暂无学习记录">
                <el-button type="primary" @click="$emit('go-to', 'learn')">开始学习</el-button>
              </el-empty>
            </div>
            <div v-else class="history-list">
              <div v-for="(record, index) in learningHistory" :key="index" class="history-item">
                <div class="history-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="history-content">
                  <span class="history-title">{{ record.title || record.word }}</span>
                  <span class="history-type">{{ record.type === 'course' ? '课程学习' : '词汇学习' }}</span>
                </div>
                <div class="history-time">{{ formatTime(record.time) }}</div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 错题本 -->
          <el-tab-pane label="错题本" name="wrong">
            <div v-if="wrongBook.length === 0" class="empty-state">
              <el-empty description="暂无错题，继续保持">
                <el-button type="primary" @click="$emit('go-to', 'test')">去练习</el-button>
              </el-empty>
            </div>
            <div v-else>
              <div class="wrong-header">
                <span>共 {{ wrongBook.length }} 道错题</span>
                <el-button size="small" type="primary" @click="$emit('go-to', 'test')">错题练习</el-button>
              </div>
              <div class="wrong-list">
                <div v-for="(item, index) in wrongBook" :key="index" class="wrong-item">
                  <div class="wrong-question">
                    <span class="wrong-index">{{ index + 1 }}.</span>
                    <span>{{ item.question }}</span>
                  </div>
                  <div class="wrong-answer">
                    <span class="label">正确答案：</span>
                    <span class="correct">{{ item.correctAnswer }}</span>
                  </div>
                  <div class="wrong-your-answer">
                    <span class="label">你的答案：</span>
                    <span class="wrong-text">{{ item.userAnswer }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 学习进度 -->
          <el-tab-pane label="学习进度" name="progress">
            <div class="progress-section">
              <h4>词汇学习进度</h4>
              <el-progress
                :percentage="Math.round((learnedWordsCount / totalWordsCount) * 100)"
                :stroke-width="20"
                :text-inside="true"
              />
              <p class="progress-text">已学习 {{ learnedWordsCount }} / {{ totalWordsCount }} 个词汇</p>
            </div>

            <div class="progress-section">
              <h4>课程完成进度</h4>
              <el-progress
                :percentage="Math.round((completedCoursesCount / totalCoursesCount) * 100)"
                :stroke-width="20"
                :text-inside="true"
                status="success"
              />
              <p class="progress-text">已完成 {{ completedCoursesCount }} / {{ totalCoursesCount }} 门课程</p>
            </div>

            <div class="progress-section">
              <h4>测试统计</h4>
              <div class="test-stats">
                <div class="test-stat-item">
                  <span class="stat-num">{{ testStats.totalTests }}</span>
                  <span class="stat-name">测试次数</span>
                </div>
                <div class="test-stat-item">
                  <span class="stat-num">{{ testStats.avgScore }}%</span>
                  <span class="stat-name">平均正确率</span>
                </div>
                <div class="test-stat-item">
                  <span class="stat-num">{{ testStats.bestScore }}%</span>
                  <span class="stat-name">最高正确率</span>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 成就 -->
          <el-tab-pane label="我的成就" name="achievements">
            <div class="achievements-grid">
              <div
                v-for="achievement in allAchievements"
                :key="achievement.id"
                class="achievement-item"
                :class="{ unlocked: isAchievementUnlocked(achievement.id) }"
              >
                <div class="achievement-icon">{{ achievement.icon }}</div>
                <div class="achievement-info">
                  <span class="achievement-name">{{ achievement.name }}</span>
                  <span class="achievement-desc">{{ achievement.description }}</span>
                </div>
                <el-tag v-if="isAchievementUnlocked(achievement.id)" type="success" size="small">已解锁</el-tag>
                <el-tag v-else type="info" size="small">未解锁</el-tag>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- 退出登录 -->
      <div class="logout-section">
        <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import {
  ensureUserStorageInitialized,
  getFavorites,
  saveFavorites,
  getUsers,
  saveUsers,
  getWords,
  getCourses,
  userScopedKey
} from '../data/appDataStore'

const emit = defineEmits(['login-success', 'logout', 'go-to'])

// 状态
const isLoggedIn = ref(false)
const isLogin = ref(true)
const authLoading = ref(false)
const authFormRef = ref(null)
const activeTab = ref('favorites')
const currentUser = ref({})

// 表单数据
const authForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (!isLogin.value && value !== authForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const authRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度为2-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 用户数据
const favorites = ref([])
const learningHistory = ref([])
const wrongBook = ref([])
const achievements = ref([])
const learnedWordsCount = ref(0)
const totalWordsCount = ref(0)
const completedCoursesCount = ref(0)
const totalCoursesCount = ref(0)
const testStats = ref({
  totalTests: 0,
  avgScore: 0,
  bestScore: 0
})

// 所有成就
const allAchievements = [
  { id: 'first_test', name: '初试牛刀', icon: '🎯', description: '完成第一次测试' },
  { id: 'score_80', name: '小有所成', icon: '🌟', description: '测试正确率达到80%' },
  { id: 'score_100', name: '精益求精', icon: '👑', description: '测试正确率达到100%' },
  { id: 'test_10', name: '勤学不倦', icon: '📚', description: '完成10次测试' },
  { id: 'challenge_pass', name: '挑战达人', icon: '🏆', description: '通过挑战模式' },
  { id: 'wrong_clear', name: '知错能改', icon: '✨', description: '清空错题本' },
  { id: 'learn_10', name: '入门学徒', icon: '📖', description: '学习10个词汇' },
  { id: 'learn_30', name: '进阶学者', icon: '🎓', description: '学习30个词汇' },
  { id: 'learn_50', name: '手语达人', icon: '💪', description: '学习50个词汇' },
  { id: 'favorite_10', name: '收藏爱好者', icon: '❤️', description: '收藏10个词汇' }
]

const achievementIdByName = {
  '初试牛刀': 'first_test',
  '小有所成': 'score_80',
  '精益求精': 'score_100',
  '勤学不倦': 'test_10',
  '挑战达人': 'challenge_pass',
  '知错能改': 'wrong_clear'
}

// 检查成就是否解锁
const isAchievementUnlocked = (id) => {
  return achievements.value.some(a => a.id === id || achievementIdByName[a.name] === id)
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '未知'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

  return date.toLocaleDateString()
}

// 登录/注册处理
const handleAuth = async () => {
  if (!authFormRef.value) return

  await authFormRef.value.validate(async (valid) => {
    if (!valid) return

    authLoading.value = true

    try {
      // 模拟API请求延迟
      await new Promise(resolve => setTimeout(resolve, 500))

      // 获取已注册用户
      const users = getUsers()

      if (isLogin.value) {
        // 登录逻辑
        const user = users.find(u => u.username === authForm.username && u.password === authForm.password)

        if (user) {
          if (user.status === 'disabled') {
            ElMessage.error('该账号已被禁用，请联系管理员')
            return
          }

          currentUser.value = { ...user }
          isLoggedIn.value = true
          localStorage.setItem('currentUser', JSON.stringify(currentUser.value))
          ensureUserStorageInitialized(currentUser.value.username)
          emit('login-success', currentUser.value)
          ElMessage.success('登录成功')
          loadUserData()
        } else {
          ElMessage.error('用户名或密码错误')
        }
      } else {
        // 注册逻辑
        const exists = users.some(u => u.username === authForm.username)

        if (exists) {
          ElMessage.error('用户名已存在')
        } else {
          const newUser = {
            id: Date.now(),
            username: authForm.username,
            password: authForm.password,
            role: 'user',
            status: 'active',
            registerTime: new Date().toLocaleDateString()
          }

          users.push(newUser)
          saveUsers(users)
          ensureUserStorageInitialized(newUser.username)

          ElMessage.success('注册成功，请登录')
          isLogin.value = true
          authForm.username = ''
          authForm.password = ''
          authForm.confirmPassword = ''
        }
      }
    } finally {
      authLoading.value = false
    }
  })
}

// 退出登录
const handleLogout = () => {
  isLoggedIn.value = false
  currentUser.value = {}
  localStorage.removeItem('currentUser')
  emit('logout')
  ElMessage.success('已退出登录')
}

// 加载用户数据（所有 key 按当前登录用户隔离）
const loadUserData = () => {
  if (currentUser.value?.username) {
    ensureUserStorageInitialized(currentUser.value.username)
  }

  learningHistory.value = []
  wrongBook.value = []
  achievements.value = []
  learnedWordsCount.value = 0
  completedCoursesCount.value = 0
  totalWordsCount.value = getWords().length
  totalCoursesCount.value = getCourses().length
  testStats.value = {
    totalTests: 0,
    avgScore: 0,
    bestScore: 0
  }

  // 加载收藏（getFavorites 内部已按用户隔离）
  favorites.value = getFavorites()

  // 加载学习历史
  const savedHistory = localStorage.getItem(userScopedKey('learningHistory'))
  if (savedHistory) {
    try {
      const parsed = JSON.parse(savedHistory)
      learningHistory.value = Array.isArray(parsed) ? parsed.slice(0, 50) : []
    } catch (error) {
      learningHistory.value = []
    }
  }

  // 加载错题本
  const savedWrongBook = localStorage.getItem(userScopedKey('wrongBook'))
  if (savedWrongBook) {
    try {
      const parsed = JSON.parse(savedWrongBook)
      wrongBook.value = Array.isArray(parsed) ? parsed : []
    } catch (error) {
      wrongBook.value = []
    }
  }

  // 加载成就
  const savedAchievements = localStorage.getItem(userScopedKey('testAchievements'))
    || localStorage.getItem(userScopedKey('achievements'))
  if (savedAchievements) {
    try {
      const parsed = JSON.parse(savedAchievements)
      const achievementsList = Array.isArray(parsed) ? parsed : []
      achievements.value = achievementsList
        .filter(item => item && item.unlocked !== false)
        .map(item => ({
          ...item,
          id: item.id || achievementIdByName[item.name] || String(item.name || '')
        }))
    } catch (error) {
      achievements.value = []
    }
  }

  // 加载学习进度
  const historyWordCount = new Set(
    learningHistory.value.map(item => item.word || item.title || item.name).filter(Boolean)
  ).size

  const savedProgress = localStorage.getItem(userScopedKey('learningProgress'))
  if (savedProgress) {
    try {
      const progress = JSON.parse(savedProgress)
      learnedWordsCount.value = progress.learnedWords ?? historyWordCount
      completedCoursesCount.value = progress.completedCourses ?? 0
    } catch (error) {
      learnedWordsCount.value = historyWordCount
    }
  } else {
    learnedWordsCount.value = historyWordCount

    const videoProgress = localStorage.getItem(userScopedKey('videoLearningProgress'))
    if (videoProgress) {
      try {
        const parsed = JSON.parse(videoProgress)
        const completedLessons = Array.isArray(parsed.completedLessons) ? parsed.completedLessons.length : 0
        completedCoursesCount.value = Number(parsed?.stats?.completedCourses || 0)
        if (!completedCoursesCount.value && completedLessons > 0) {
          completedCoursesCount.value = Math.min(completedLessons, totalCoursesCount.value)
        }
      } catch (error) {
        completedCoursesCount.value = 0
      }
    }
  }

  // 加载测试统计
  const savedTestStats = localStorage.getItem(userScopedKey('testStats'))
  if (savedTestStats) {
    try {
      const parsed = JSON.parse(savedTestStats)
      testStats.value = {
        totalTests: Number(parsed.totalTests || 0),
        avgScore: Number(parsed.avgScore || 0),
        bestScore: Number(parsed.bestScore || 0)
      }
    } catch (error) {
      testStats.value = {
        totalTests: 0,
        avgScore: 0,
        bestScore: 0
      }
    }
  } else {
    try {
      const records = JSON.parse(localStorage.getItem(userScopedKey('testRecords')) || '[]')
      if (Array.isArray(records) && records.length > 0) {
        const total = records.length
        const scoreSum = records.reduce((sum, record) => {
          const ratio = Number(record.total) > 0 ? Number(record.score) / Number(record.total) : 0
          return sum + ratio
        }, 0)
        const bestRatio = records.reduce((best, record) => {
          const ratio = Number(record.total) > 0 ? Number(record.score) / Number(record.total) : 0
          return Math.max(best, ratio)
        }, 0)

        testStats.value = {
          totalTests: total,
          avgScore: Math.round(scoreSum / total * 100),
          bestScore: Math.round(bestRatio * 100)
        }
        localStorage.setItem(userScopedKey('testStats'), JSON.stringify(testStats.value))
      }
    } catch (error) {
      testStats.value = {
        totalTests: 0,
        avgScore: 0,
        bestScore: 0
      }
    }
  }
}

// 取消收藏
const removeFavorite = (wordId) => {
  favorites.value = favorites.value.filter(w => w.id !== wordId)
  saveFavorites(favorites.value)
  ElMessage.success('已取消收藏')
}

// 初始化
onMounted(() => {
  const savedUser = localStorage.getItem('currentUser')
  if (savedUser) {
    try {
      currentUser.value = JSON.parse(savedUser)
      isLoggedIn.value = true
      ensureUserStorageInitialized(currentUser.value.username)
      loadUserData()
    } catch (error) {
      localStorage.removeItem('currentUser')
    }
  }
})

// 监听登录状态变化
watch(isLoggedIn, (val) => {
  if (val) {
    loadUserData()
  }
})
</script>

<style scoped>
.user-center {
  padding: clamp(16px, 3vw, 24px);
}

/* 登录/注册 */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}

.auth-card {
  width: 400px;
}

.auth-card .card-header {
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.auth-switch {
  text-align: center;
  margin-top: 16px;
  color: #909399;
}

/* 用户资料 */
.profile-container {
  max-width: 900px;
  margin: 0 auto;
  width: min(100%, 900px);
}

.profile-card {
  margin-bottom: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.profile-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 32px;
}

.profile-info h2 {
  font-size: 24px;
  margin: 0 0 8px 0;
  color: #303133;
}

.role-tag {
  margin: 0 0 4px 0;
}

.register-time {
  color: #909399;
  font-size: 13px;
  margin: 4px 0 0 0;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 16px;
  padding-top: 20px;
}

.stat-item {
  text-align: center;
  min-width: 110px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #667eea;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* 内容卡片 */
.content-card {
  margin-bottom: 20px;
  overflow: hidden;
}

.content-card :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.content-card :deep(.el-tabs__nav-wrap) {
  overflow-x: auto;
  overflow-y: hidden;
}

.content-card :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.content-card :deep(.el-tabs__nav) {
  flex-wrap: nowrap;
}

.content-card :deep(.el-tabs__item) {
  white-space: nowrap;
}

.empty-state {
  padding: 40px 0;
}

/* 收藏列表 */
.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.word-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
  min-width: 0;
}

.word-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.word-pinyin {
  font-size: 13px;
  color: #909399;
}

/* 学习记录 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.history-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #667eea;
  color: #fff;
  border-radius: 8px;
  font-size: 18px;
}

.history-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-title {
  font-size: 15px;
  color: #303133;
}

.history-type {
  font-size: 12px;
  color: #909399;
}

.history-time {
  font-size: 13px;
  color: #909399;
}

/* 错题本 */
.wrong-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  color: #606266;
}

.wrong-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.wrong-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #f56c6c;
}

.wrong-question {
  font-size: 15px;
  color: #303133;
  margin-bottom: 12px;
}

.wrong-index {
  font-weight: 600;
  margin-right: 8px;
}

.wrong-answer,
.wrong-your-answer {
  font-size: 13px;
  margin-top: 8px;
}

.wrong-answer .label,
.wrong-your-answer .label {
  color: #909399;
}

.wrong-answer .correct {
  color: #67c23a;
  font-weight: 500;
}

.wrong-your-answer .wrong-text {
  color: #f56c6c;
}

/* 学习进度 */
.progress-section {
  margin-bottom: 32px;
}

.progress-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 15px;
}

.progress-text {
  margin: 8px 0 0 0;
  color: #909399;
  font-size: 13px;
}

.test-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  margin-top: 12px;
}

.test-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.test-stat-item .stat-num {
  font-size: 24px;
  font-weight: 600;
  color: #667eea;
}

.test-stat-item .stat-name {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* 成就 */
.achievements-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.achievement-item {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  opacity: 0.6;
  transition: all 0.3s;
}

.achievement-item.unlocked {
  opacity: 1;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid #667eea;
}

.achievement-icon {
  font-size: 32px;
}

.achievement-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.achievement-name {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.achievement-desc {
  font-size: 12px;
  color: #909399;
}

/* 退出登录 */
.logout-section {
  text-align: center;
  padding: 20px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .auth-card {
    width: 100%;
  }

  .user-center {
    padding: 16px;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
  }

  .stats-row {
    gap: 14px;
  }

  .stat-item {
    flex: 1;
    min-width: 80px;
  }

  .achievements-grid {
    grid-template-columns: 1fr;
  }

  .test-stats {
    flex-wrap: wrap;
    gap: 20px;
  }
}
</style>
