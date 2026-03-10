<template>
  <div class="admin-panel">
    <div class="admin-header">
      <h2>后台管理</h2>
      <p>管理平台用户、词汇、课程和社区内容</p>
    </div>

    <el-tabs v-model="activeTab" type="card" class="admin-tabs">
      <!-- 数据概览 -->
      <el-tab-pane label="数据概览" name="dashboard">
        <div class="dashboard-grid">
          <el-card class="stat-card">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalUsers }}</div>
              <div class="stat-label">注册用户</div>
            </div>
          </el-card>

          <el-card class="stat-card">
            <div class="stat-icon words">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalWords }}</div>
              <div class="stat-label">词汇数量</div>
            </div>
          </el-card>

          <el-card class="stat-card">
            <div class="stat-icon courses">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalCourses }}</div>
              <div class="stat-label">课程数量</div>
            </div>
          </el-card>

          <el-card class="stat-card">
            <div class="stat-icon posts">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalPosts }}</div>
              <div class="stat-label">社区帖子</div>
            </div>
          </el-card>
        </div>

        <el-card class="chart-card">
          <template #header>
            <span>平台活跃度统计</span>
          </template>
          <div class="activity-stats">
            <div class="activity-item">
              <span class="activity-label">今日访问</span>
              <span class="activity-value">{{ stats.todayVisits }}</span>
            </div>
            <div class="activity-item">
              <span class="activity-label">今日学习</span>
              <span class="activity-value">{{ stats.todayLearning }}</span>
            </div>
            <div class="activity-item">
              <span class="activity-label">今日测试</span>
              <span class="activity-value">{{ stats.todayTests }}</span>
            </div>
            <div class="activity-item">
              <span class="activity-label">新增用户</span>
              <span class="activity-value">{{ stats.newUsers }}</span>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <div class="table-header">
          <el-input
            v-model="userSearch"
            placeholder="搜索用户名"
            style="width: 200px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table :data="filteredUsers" style="width: 100%" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'" size="small">
                {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="registerTime" label="注册时间" width="120" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'active' ? 'success' : 'warning'" size="small">
                {{ scope.row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button
                v-if="scope.row.status === 'active'"
                size="small"
                type="warning"
                text
                @click="toggleUserStatus(scope.row)"
              >禁用</el-button>
              <el-button
                v-else
                size="small"
                type="success"
                text
                @click="toggleUserStatus(scope.row)"
              >启用</el-button>
              <el-button
                size="small"
                type="danger"
                text
                @click="deleteUser(scope.row)"
                :disabled="scope.row.role === 'admin'"
              >删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 词汇管理 -->
      <el-tab-pane label="词汇管理" name="words">
        <div class="table-header">
          <el-input
            v-model="wordSearch"
            placeholder="搜索词汇"
            style="width: 200px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="openWordDialog()">添加词汇</el-button>
        </div>

        <el-table :data="filteredWords" style="width: 100%" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="word" label="词汇" />
          <el-table-column prop="pinyin" label="拼音" />
          <el-table-column prop="category" label="分类" width="120" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" type="primary" text @click="openWordDialog(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" text @click="deleteWord(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 课程管理 -->
      <el-tab-pane label="课程管理" name="courses">
        <div class="table-header">
          <el-input
            v-model="courseSearch"
            placeholder="搜索课程"
            style="width: 200px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="openCourseDialog()">添加课程</el-button>
        </div>

        <el-table :data="filteredCourses" style="width: 100%" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="课程名称" />
          <el-table-column prop="category" label="分类" width="120" />
          <el-table-column prop="lessons" label="课时数" width="80">
            <template #default="scope">
              {{ scope.row.lessons?.length || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" type="primary" text @click="openCourseDialog(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" text @click="deleteCourse(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 社区管理 -->
      <el-tab-pane label="社区管理" name="community">
        <div class="table-header">
          <el-input
            v-model="postSearch"
            placeholder="搜索帖子"
            style="width: 200px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table :data="filteredPosts" style="width: 100%" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="author" label="作者" width="100" />
          <el-table-column prop="content" label="内容">
            <template #default="scope">
              <span class="post-preview">{{ scope.row.content?.slice(0, 50) }}{{ scope.row.content?.length > 50 ? '...' : '' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="likes" label="点赞" width="80" />
          <el-table-column prop="time" label="发布时间" width="150">
            <template #default="scope">
              {{ formatTime(scope.row.time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button size="small" type="danger" text @click="deletePost(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 敏感词管理 -->
      <el-tab-pane label="敏感词管理" name="sensitive">
        <div class="sensitive-section">
          <div class="sensitive-header">
            <span>敏感词列表</span>
            <el-button type="primary" size="small" @click="addSensitiveWord">添加</el-button>
          </div>

          <div class="sensitive-tags">
            <el-tag
              v-for="(word, index) in sensitiveWords"
              :key="index"
              closable
              @close="removeSensitiveWord(index)"
              type="danger"
              class="sensitive-tag"
            >
              {{ word }}
            </el-tag>
          </div>

          <el-input
            v-model="newSensitiveWord"
            placeholder="输入新的敏感词"
            style="width: 200px; margin-top: 16px"
            @keyup.enter="addSensitiveWord"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 词汇编辑对话框 -->
    <el-dialog v-model="wordDialogVisible" :title="editingWord.id ? '编辑词汇' : '添加词汇'" width="500px">
      <el-form :model="editingWord" label-width="80px">
        <el-form-item label="词汇">
          <el-input v-model="editingWord.word" placeholder="请输入词汇" />
        </el-form-item>
        <el-form-item label="拼音">
          <el-input v-model="editingWord.pinyin" placeholder="请输入拼音" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="editingWord.category" placeholder="请选择分类">
            <el-option label="问候用语" value="问候用语" />
            <el-option label="日常交流" value="日常交流" />
            <el-option label="情感表达" value="情感表达" />
            <el-option label="数字" value="数字" />
            <el-option label="时间日期" value="时间日期" />
            <el-option label="家庭称谓" value="家庭称谓" />
            <el-option label="动作行为" value="动作行为" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="editingWord.description" type="textarea" placeholder="请输入词汇说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="wordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWord">保存</el-button>
      </template>
    </el-dialog>

    <!-- 课程编辑对话框 -->
    <el-dialog v-model="courseDialogVisible" :title="editingCourse.id ? '编辑课程' : '添加课程'" width="500px">
      <el-form :model="editingCourse" label-width="80px">
        <el-form-item label="课程名称">
          <el-input v-model="editingCourse.title" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="editingCourse.category" placeholder="请选择分类">
            <el-option label="入门基础" value="入门基础" />
            <el-option label="问候交流" value="问候交流" />
            <el-option label="日常用语" value="日常用语" />
            <el-option label="情感表达" value="情感表达" />
            <el-option label="家庭称谓" value="家庭称谓" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input v-model="editingCourse.description" type="textarea" placeholder="请输入课程描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="courseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCourse">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Document, VideoPlay, ChatDotRound, Search } from '@element-plus/icons-vue'
import {
  getUsers as loadUsersFromStore,
  saveUsers as saveUsersToStore,
  getWords as loadWordsFromStore,
  saveWords as saveWordsToStore,
  getCourses as loadCoursesFromStore,
  saveCourses as saveCoursesToStore,
  getCommunityPosts as loadPostsFromStore,
  saveCommunityPosts as savePostsToStore,
  getSensitiveWords as loadSensitiveWordsFromStore,
  saveSensitiveWords as saveSensitiveWordsToStore
} from '../data/appDataStore'

const DEFAULT_SENSITIVE_WORDS = [
  '广告', '推销', '代购', '微信', 'QQ群',
  '色情', '暴力', '赌博', '诈骗',
  '政治', '反动', '谣言'
]

// 状态
const activeTab = ref('dashboard')
const userSearch = ref('')
const wordSearch = ref('')
const courseSearch = ref('')
const postSearch = ref('')
const newSensitiveWord = ref('')

// 对话框
const wordDialogVisible = ref(false)
const courseDialogVisible = ref(false)
const editingWord = ref({})
const editingCourse = ref({})

// 数据
const users = ref([])
const words = ref([])
const courses = ref([])
const posts = ref([])
const sensitiveWords = ref([])

// 统计数据
const stats = reactive({
  totalUsers: 0,
  totalWords: 0,
  totalCourses: 0,
  totalPosts: 0,
  todayVisits: 128,
  todayLearning: 45,
  todayTests: 23,
  newUsers: 5
})

// 过滤数据
const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  return users.value.filter(u =>
    u.username.toLowerCase().includes(userSearch.value.toLowerCase())
  )
})

const filteredWords = computed(() => {
  if (!wordSearch.value) return words.value
  return words.value.filter(w =>
    w.word.includes(wordSearch.value) ||
    String(w.pinyin || '').toLowerCase().includes(wordSearch.value.toLowerCase())
  )
})

const filteredCourses = computed(() => {
  if (!courseSearch.value) return courses.value
  return courses.value.filter(c =>
    c.title.includes(courseSearch.value)
  )
})

const filteredPosts = computed(() => {
  if (!postSearch.value) return posts.value
  return posts.value.filter(p =>
    p.content?.includes(postSearch.value) ||
    p.author?.includes(postSearch.value)
  )
})

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '未知'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

const refreshStats = () => {
  stats.totalUsers = users.value.length
  stats.totalWords = words.value.length
  stats.totalCourses = courses.value.length
  stats.totalPosts = posts.value.length
}

// 用户管理
const toggleUserStatus = (user) => {
  user.status = user.status === 'active' ? 'disabled' : 'active'
  saveUsers()
  ElMessage.success(`已${user.status === 'active' ? '启用' : '禁用'}用户 ${user.username}`)
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${user.username} 吗？`, '确认删除', {
      type: 'warning'
    })
    users.value = users.value.filter(u => u.id !== user.id)
    saveUsers()
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

const saveUsers = () => {
  saveUsersToStore(users.value)
  refreshStats()
}

// 词汇管理
const openWordDialog = (word = {}) => {
  editingWord.value = { ...word }
  wordDialogVisible.value = true
}

const saveWord = () => {
  if (!editingWord.value.word || !editingWord.value.pinyin) {
    ElMessage.warning('请填写完整信息')
    return
  }

  if (editingWord.value.id) {
    // 编辑
    const index = words.value.findIndex(w => w.id === editingWord.value.id)
    if (index > -1) {
      words.value[index] = { ...editingWord.value }
    }
  } else {
    // 添加
    words.value.push({
      ...editingWord.value,
      id: Date.now()
    })
  }

  saveWords()
  wordDialogVisible.value = false
  ElMessage.success('保存成功')
}

const deleteWord = async (word) => {
  try {
    await ElMessageBox.confirm(`确定要删除词汇 ${word.word} 吗？`, '确认删除', {
      type: 'warning'
    })
    words.value = words.value.filter(w => w.id !== word.id)
    saveWords()
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

const saveWords = () => {
  saveWordsToStore(words.value)
  refreshStats()
}

// 课程管理
const openCourseDialog = (course = {}) => {
  editingCourse.value = { ...course }
  courseDialogVisible.value = true
}

const saveCourse = () => {
  if (!editingCourse.value.title || !editingCourse.value.category) {
    ElMessage.warning('请填写完整信息')
    return
  }

  if (editingCourse.value.id) {
    const index = courses.value.findIndex(c => c.id === editingCourse.value.id)
    if (index > -1) {
      courses.value[index] = { ...editingCourse.value }
    }
  } else {
    courses.value.push({
      ...editingCourse.value,
      id: Date.now(),
      lessons: []
    })
  }

  saveCourses()
  courseDialogVisible.value = false
  ElMessage.success('保存成功')
}

const deleteCourse = async (course) => {
  try {
    await ElMessageBox.confirm(`确定要删除课程 ${course.title} 吗？`, '确认删除', {
      type: 'warning'
    })
    courses.value = courses.value.filter(c => c.id !== course.id)
    saveCourses()
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

const saveCourses = () => {
  saveCoursesToStore(courses.value)
  refreshStats()
}

// 帖子管理
const deletePost = async (post) => {
  try {
    await ElMessageBox.confirm('确定要删除这条帖子吗？', '确认删除', {
      type: 'warning'
    })
    posts.value = posts.value.filter(p => p.id !== post.id)
    savePosts()
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

const savePosts = () => {
  savePostsToStore(posts.value)
  refreshStats()
}

// 敏感词管理
const addSensitiveWord = () => {
  if (!newSensitiveWord.value.trim()) return
  if (sensitiveWords.value.includes(newSensitiveWord.value.trim())) {
    ElMessage.warning('该敏感词已存在')
    return
  }
  sensitiveWords.value.push(newSensitiveWord.value.trim())
  saveSensitiveWords()
  newSensitiveWord.value = ''
  ElMessage.success('添加成功')
}

const removeSensitiveWord = (index) => {
  sensitiveWords.value.splice(index, 1)
  saveSensitiveWords()
  ElMessage.success('删除成功')
}

const saveSensitiveWords = () => {
  saveSensitiveWordsToStore(sensitiveWords.value)
}

// 加载数据
const loadData = () => {
  users.value = loadUsersFromStore()
  words.value = loadWordsFromStore()
  courses.value = loadCoursesFromStore()
  posts.value = loadPostsFromStore()
  sensitiveWords.value = loadSensitiveWordsFromStore(DEFAULT_SENSITIVE_WORDS)
  refreshStats()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.admin-panel {
  padding: 24px;
}

.admin-header {
  margin-bottom: 24px;
}

.admin-header h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
  color: #303133;
}

.admin-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.admin-tabs {
  background: #fff;
}

/* 数据概览 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0;
  width: 100%;
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 24px;
  color: #fff;
}

.stat-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.words {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.courses {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.posts {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.chart-card {
  margin-bottom: 20px;
}

.activity-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.activity-item {
  text-align: center;
}

.activity-label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.activity-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #667eea;
}

/* 表格 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.post-preview {
  color: #606266;
  font-size: 13px;
}

/* 敏感词管理 */
.sensitive-section {
  padding: 16px 0;
}

.sensitive-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
  color: #303133;
}

.sensitive-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sensitive-tag {
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .activity-stats {
    flex-wrap: wrap;
    gap: 20px;
  }

  .activity-item {
    flex: 1;
    min-width: 80px;
  }

  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
