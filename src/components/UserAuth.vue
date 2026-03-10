<template>
  <div class="user-auth">
    <el-card class="auth-card">
      <!-- 未登录状态 -->
      <template v-if="!isLoggedIn">
        <el-tabs v-model="activeTab" class="auth-tabs">
          <!-- 登录 -->
          <el-tab-pane label="登录" name="login">
            <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="auth-form">
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  prefix-icon="User"
                  size="large"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                  @keyup.enter="handleLogin"
                />
              </el-form-item>
              <el-form-item>
                <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="large" @click="handleLogin" :loading="loading" class="submit-btn">
                  登 录
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 注册 -->
          <el-tab-pane label="注册" name="register">
            <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" class="auth-form">
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  prefix-icon="User"
                  size="large"
                />
              </el-form-item>
              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱"
                  prefix-icon="Message"
                  size="large"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>
              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请确认密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="large" @click="handleRegister" :loading="loading" class="submit-btn">
                  注 册
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </template>

      <!-- 已登录状态 - 用户中心 -->
      <template v-else>
        <div class="user-center">
          <div class="user-header">
            <el-avatar :size="80" :src="currentUser.avatar">
              {{ currentUser.username.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="user-info">
              <h2>{{ currentUser.username }}</h2>
              <p class="user-email">{{ currentUser.email }}</p>
              <el-tag :type="getLevelType(currentUser.level)" size="small">
                Lv.{{ currentUser.level }} {{ getLevelName(currentUser.level) }}
              </el-tag>
            </div>
          </div>

          <!-- 用户统计 -->
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ currentUser.stats.totalPractice }}</div>
              <div class="stat-label">练习次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ currentUser.stats.correctRate }}%</div>
              <div class="stat-label">正确率</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ currentUser.stats.learningDays }}</div>
              <div class="stat-label">学习天数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ currentUser.stats.achievements }}</div>
              <div class="stat-label">成就数</div>
            </div>
          </div>

          <!-- 经验进度 -->
          <div class="exp-progress">
            <div class="exp-header">
              <span>经验值</span>
              <span>{{ currentUser.exp }} / {{ getNextLevelExp(currentUser.level) }}</span>
            </div>
            <el-progress
              :percentage="getExpPercentage()"
              :color="getLevelColor(currentUser.level)"
              :stroke-width="10"
            />
          </div>

          <!-- 功能菜单 -->
          <div class="user-menu">
            <el-button @click="showProfile = true" class="menu-btn">
              <el-icon><UserFilled /></el-icon>
              个人资料
            </el-button>
            <el-button @click="showFavorites = true" class="menu-btn">
              <el-icon><Star /></el-icon>
              我的收藏 ({{ favorites.length }})
            </el-button>
            <el-button @click="showHistory = true" class="menu-btn">
              <el-icon><Clock /></el-icon>
              学习历史
            </el-button>
            <el-button @click="showWrongBook = true" class="menu-btn">
              <el-icon><Document /></el-icon>
              错题本 ({{ wrongBook.length }})
            </el-button>
            <el-button @click="showAchievements = true" class="menu-btn">
              <el-icon><Trophy /></el-icon>
              我的成就
            </el-button>
            <el-button type="danger" @click="handleLogout" class="menu-btn logout-btn">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </div>
        </div>
      </template>
    </el-card>

    <!-- 收藏夹弹窗 -->
    <el-dialog v-model="showFavorites" title="我的收藏" width="600px">
      <div class="favorites-list" v-if="favorites.length > 0">
        <div v-for="item in favorites" :key="item.id" class="favorite-item">
          <span class="favorite-icon">{{ item.icon }}</span>
          <span class="favorite-name">{{ item.name }}</span>
          <span class="favorite-time">{{ item.time }}</span>
          <el-button type="danger" size="small" @click="removeFavorite(item.id)">取消收藏</el-button>
        </div>
      </div>
      <el-empty v-else description="暂无收藏" />
    </el-dialog>

    <!-- 学习历史弹窗 -->
    <el-dialog v-model="showHistory" title="学习历史" width="600px">
      <div class="history-list" v-if="learningHistory.length > 0">
        <div v-for="item in learningHistory" :key="item.id" class="history-item">
          <span class="history-icon">{{ item.icon }}</span>
          <div class="history-info">
            <span class="history-name">{{ item.name }}</span>
            <span class="history-detail">{{ item.result }} - {{ item.time }}</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无学习记录" />
    </el-dialog>

    <!-- 错题本弹窗 -->
    <el-dialog v-model="showWrongBook" title="错题本" width="700px">
      <div class="wrong-book" v-if="wrongBook.length > 0">
        <div v-for="item in wrongBook" :key="item.id" class="wrong-item">
          <div class="wrong-header">
            <span class="wrong-icon">{{ item.icon }}</span>
            <span class="wrong-name">{{ item.name }}</span>
            <el-tag type="danger" size="small">错误 {{ item.wrongCount }} 次</el-tag>
          </div>
          <div class="wrong-detail">
            <p>错误原因: {{ item.reason || '手势不准确' }}</p>
            <p>建议: {{ item.suggestion || '请参考标准手势重新练习' }}</p>
          </div>
          <div class="wrong-actions">
            <el-button type="primary" size="small" @click="practiceWrongItem(item)">重新练习</el-button>
            <el-button size="small" @click="removeFromWrongBook(item.id)">移除</el-button>
          </div>
        </div>
      </div>
      <el-empty v-else description="太棒了！没有错题" />
    </el-dialog>

    <!-- 成就弹窗 -->
    <el-dialog v-model="showAchievements" title="我的成就" width="700px">
      <div class="achievements-grid">
        <div
          v-for="achievement in achievements"
          :key="achievement.id"
          :class="['achievement-item', { unlocked: achievement.unlocked }]"
        >
          <div class="achievement-icon">{{ achievement.icon }}</div>
          <div class="achievement-info">
            <div class="achievement-name">{{ achievement.name }}</div>
            <div class="achievement-desc">{{ achievement.description }}</div>
            <div class="achievement-progress" v-if="!achievement.unlocked">
              <el-progress
                :percentage="achievement.progress"
                :stroke-width="6"
                :show-text="false"
              />
              <span>{{ achievement.current }}/{{ achievement.target }}</span>
            </div>
            <div class="achievement-time" v-else>
              {{ achievement.unlockedTime }}
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, UserFilled, Star, Clock, Document, Trophy, SwitchButton } from '@element-plus/icons-vue'

// 状态
const activeTab = ref('login')
const loading = ref(false)
const isLoggedIn = ref(false)
const currentUser = ref(null)
const showProfile = ref(false)
const showFavorites = ref(false)
const showHistory = ref(false)
const showWrongBook = ref(false)
const showAchievements = ref(false)

// 表单引用
const loginFormRef = ref(null)
const registerFormRef = ref(null)

// 登录表单
const loginForm = reactive({
  username: '',
  password: '',
  remember: true
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 验证规则
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 用户数据
const favorites = ref([])
const learningHistory = ref([])
const wrongBook = ref([])
const achievements = ref([
  { id: 1, name: '初来乍到', icon: '🎉', description: '完成首次登录', unlocked: false, progress: 0, current: 0, target: 1 },
  { id: 2, name: '勤奋学习', icon: '📚', description: '累计练习10次', unlocked: false, progress: 0, current: 0, target: 10 },
  { id: 3, name: '精益求精', icon: '🎯', description: '正确率达到80%', unlocked: false, progress: 0, current: 0, target: 80 },
  { id: 4, name: '持之以恒', icon: '🔥', description: '连续学习7天', unlocked: false, progress: 0, current: 0, target: 7 },
  { id: 5, name: '手语达人', icon: '🏆', description: '掌握所有手势', unlocked: false, progress: 0, current: 0, target: 10 },
  { id: 6, name: '完美主义', icon: '⭐', description: '单次练习全部正确', unlocked: false, progress: 0, current: 0, target: 1 },
  { id: 7, name: '知识渊博', icon: '🧠', description: '学习50个词汇', unlocked: false, progress: 0, current: 0, target: 50 },
  { id: 8, name: '社区之星', icon: '💬', description: '发布10篇帖子', unlocked: false, progress: 0, current: 0, target: 10 }
])

// 等级配置
const levelConfig = {
  1: { name: '入门学徒', exp: 100, color: '#909399' },
  2: { name: '初级学员', exp: 300, color: '#67C23A' },
  3: { name: '中级学员', exp: 600, color: '#409EFF' },
  4: { name: '高级学员', exp: 1000, color: '#E6A23C' },
  5: { name: '手语专家', exp: 1500, color: '#F56C6C' },
  6: { name: '手语大师', exp: 2500, color: '#9B59B6' }
}

// 方法
const getLevelType = (level) => {
  const types = ['info', 'success', 'primary', 'warning', 'danger', '']
  return types[level - 1] || 'info'
}

const getLevelName = (level) => {
  return levelConfig[level]?.name || '入门学徒'
}

const getLevelColor = (level) => {
  return levelConfig[level]?.color || '#909399'
}

const getNextLevelExp = (level) => {
  return levelConfig[level]?.exp || 100
}

const getExpPercentage = () => {
  if (!currentUser.value) return 0
  const nextExp = getNextLevelExp(currentUser.value.level)
  return Math.min(100, Math.round((currentUser.value.exp / nextExp) * 100))
}

// 登录
const handleLogin = async () => {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true

  // 模拟登录验证（实际项目中应调用后端API）
  setTimeout(() => {
    const users = JSON.parse(localStorage.getItem('users') || '[]')
    const user = users.find(u => u.username === loginForm.username && u.password === loginForm.password)

    if (user) {
      // 登录成功
      currentUser.value = user
      isLoggedIn.value = true

      // 更新登录时间
      user.lastLogin = new Date().toLocaleString()
      localStorage.setItem('users', JSON.stringify(users))

      if (loginForm.remember) {
        localStorage.setItem('currentUser', JSON.stringify(user))
      }

      // 加载用户数据
      loadUserData(user.username)

      // 更新成就：首次登录
      checkAchievement(1)

      ElMessage.success(`欢迎回来，${user.username}！`)
    } else {
      ElMessage.error('用户名或密码错误')
    }

    loading.value = false
  }, 500)
}

// 注册
const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true

  setTimeout(() => {
    const users = JSON.parse(localStorage.getItem('users') || '[]')

    // 检查用户名是否存在
    if (users.find(u => u.username === registerForm.username)) {
      ElMessage.error('用户名已存在')
      loading.value = false
      return
    }

    // 检查邮箱是否存在
    if (users.find(u => u.email === registerForm.email)) {
      ElMessage.error('邮箱已被注册')
      loading.value = false
      return
    }

    // 创建新用户
    const newUser = {
      id: Date.now(),
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      avatar: '',
      level: 1,
      exp: 0,
      stats: {
        totalPractice: 0,
        correctRate: 0,
        learningDays: 1,
        achievements: 0
      },
      createdAt: new Date().toLocaleString(),
      lastLogin: new Date().toLocaleString()
    }

    users.push(newUser)
    localStorage.setItem('users', JSON.stringify(users))

    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username

    // 清空注册表单
    registerForm.username = ''
    registerForm.email = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''

    loading.value = false
  }, 500)
}

// 退出登录
const handleLogout = () => {
  currentUser.value = null
  isLoggedIn.value = false
  localStorage.removeItem('currentUser')
  ElMessage.success('已退出登录')
}

// 加载用户数据
const loadUserData = (username) => {
  favorites.value = JSON.parse(localStorage.getItem(`${username}_favorites`) || '[]')
  learningHistory.value = JSON.parse(localStorage.getItem(`${username}_history`) || '[]')
  wrongBook.value = JSON.parse(localStorage.getItem(`${username}_wrongBook`) || '[]')

  // 加载成就进度
  const savedAchievements = JSON.parse(localStorage.getItem(`${username}_achievements`) || 'null')
  if (savedAchievements) {
    achievements.value = savedAchievements
  }
}

// 保存用户数据
const saveUserData = () => {
  if (!currentUser.value) return
  const username = currentUser.value.username
  localStorage.setItem(`${username}_favorites`, JSON.stringify(favorites.value))
  localStorage.setItem(`${username}_history`, JSON.stringify(learningHistory.value))
  localStorage.setItem(`${username}_wrongBook`, JSON.stringify(wrongBook.value))
  localStorage.setItem(`${username}_achievements`, JSON.stringify(achievements.value))
}

// 检查成就
const checkAchievement = (id) => {
  const achievement = achievements.value.find(a => a.id === id)
  if (achievement && !achievement.unlocked) {
    achievement.unlocked = true
    achievement.unlockedTime = new Date().toLocaleString()
    achievement.progress = 100

    if (currentUser.value) {
      currentUser.value.stats.achievements++
    }

    saveUserData()
    ElMessage.success(`恭喜获得成就：${achievement.name}！`)
  }
}

// 移除收藏
const removeFavorite = (id) => {
  favorites.value = favorites.value.filter(f => f.id !== id)
  saveUserData()
  ElMessage.success('已取消收藏')
}

// 移除错题
const removeFromWrongBook = (id) => {
  wrongBook.value = wrongBook.value.filter(w => w.id !== id)
  saveUserData()
  ElMessage.success('已从错题本移除')
}

// 重新练习错题
const practiceWrongItem = (item) => {
  showWrongBook.value = false
  ElMessage.info(`开始练习：${item.name}`)
  // 这里可以触发跳转到练习页面
}

// 初始化
onMounted(() => {
  // 检查是否有保存的登录状态
  const savedUser = localStorage.getItem('currentUser')
  if (savedUser) {
    currentUser.value = JSON.parse(savedUser)
    isLoggedIn.value = true
    loadUserData(currentUser.value.username)
  }
})

// 暴露方法供外部使用
defineExpose({
  isLoggedIn,
  currentUser,
  favorites,
  learningHistory,
  wrongBook,
  addFavorite: (item) => {
    if (!isLoggedIn.value) {
      ElMessage.warning('请先登录')
      return false
    }
    if (!favorites.value.find(f => f.id === item.id)) {
      favorites.value.unshift({ ...item, time: new Date().toLocaleString() })
      saveUserData()
      return true
    }
    return false
  },
  addHistory: (item) => {
    if (!isLoggedIn.value) return
    learningHistory.value.unshift({ ...item, time: new Date().toLocaleString() })
    if (learningHistory.value.length > 100) learningHistory.value.pop()
    saveUserData()
  },
  addToWrongBook: (item) => {
    if (!isLoggedIn.value) return
    const existing = wrongBook.value.find(w => w.id === item.id)
    if (existing) {
      existing.wrongCount++
    } else {
      wrongBook.value.unshift({ ...item, wrongCount: 1 })
    }
    saveUserData()
  },
  updateStats: (practiceResult) => {
    if (!isLoggedIn.value || !currentUser.value) return
    currentUser.value.stats.totalPractice++
    currentUser.value.exp += practiceResult.correct ? 10 : 2

    // 检查升级
    const nextExp = getNextLevelExp(currentUser.value.level)
    if (currentUser.value.exp >= nextExp && currentUser.value.level < 6) {
      currentUser.value.level++
      currentUser.value.exp -= nextExp
      ElMessage.success(`恭喜升级到 Lv.${currentUser.value.level} ${getLevelName(currentUser.value.level)}！`)
    }

    // 更新用户列表
    const users = JSON.parse(localStorage.getItem('users') || '[]')
    const userIndex = users.findIndex(u => u.id === currentUser.value.id)
    if (userIndex !== -1) {
      users[userIndex] = currentUser.value
      localStorage.setItem('users', JSON.stringify(users))
      localStorage.setItem('currentUser', JSON.stringify(currentUser.value))
    }

    // 检查成就
    if (currentUser.value.stats.totalPractice >= 10) checkAchievement(2)
  }
})
</script>

<style scoped>
.user-auth {
  height: 100%;
}

.auth-card {
  height: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.auth-tabs {
  padding: 20px 0;
}

.auth-form {
  padding: 20px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

/* 用户中心 */
.user-center {
  padding: 20px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.user-info h2 {
  margin: 0 0 5px 0;
  font-size: 1.5em;
}

.user-email {
  color: #909399;
  margin: 0 0 8px 0;
}

/* 统计 */
.user-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.8em;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 0.85em;
  color: #909399;
  margin-top: 5px;
}

/* 经验进度 */
.exp-progress {
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9em;
  color: #606266;
}

/* 菜单 */
.user-menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 20px;
}

.menu-btn {
  justify-content: flex-start;
  height: 44px;
}

.logout-btn {
  margin-top: 10px;
}

/* 收藏列表 */
.favorites-list, .history-list {
  max-height: 400px;
  overflow-y: auto;
}

.favorite-item, .history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.favorite-icon, .history-icon {
  font-size: 1.5em;
}

.favorite-name, .history-name {
  flex: 1;
  font-weight: 500;
}

.favorite-time, .history-detail {
  color: #909399;
  font-size: 0.85em;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 错题本 */
.wrong-book {
  max-height: 500px;
  overflow-y: auto;
}

.wrong-item {
  padding: 15px;
  margin-bottom: 15px;
  background: #fef0f0;
  border-radius: 8px;
  border-left: 4px solid #F56C6C;
}

.wrong-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.wrong-icon {
  font-size: 1.5em;
}

.wrong-name {
  flex: 1;
  font-weight: bold;
}

.wrong-detail {
  font-size: 0.9em;
  color: #606266;
  margin-bottom: 10px;
}

.wrong-detail p {
  margin: 5px 0;
}

.wrong-actions {
  display: flex;
  gap: 10px;
}

/* 成就 */
.achievements-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  max-height: 500px;
  overflow-y: auto;
}

.achievement-item {
  display: flex;
  gap: 12px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  opacity: 0.6;
  transition: all 0.3s;
}

.achievement-item.unlocked {
  opacity: 1;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border: 2px solid #67C23A;
}

.achievement-icon {
  font-size: 2.5em;
}

.achievement-info {
  flex: 1;
}

.achievement-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.achievement-desc {
  font-size: 0.85em;
  color: #909399;
  margin-bottom: 8px;
}

.achievement-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.achievement-progress span {
  font-size: 0.8em;
  color: #909399;
}

.achievement-time {
  font-size: 0.8em;
  color: #67C23A;
}
</style>
