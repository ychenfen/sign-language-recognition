<template>
  <div class="sign-learning">
    <!-- 课程分类导航 -->
    <div class="course-nav">
      <div class="nav-header">
        <h2>手语学习</h2>
        <span class="subtitle">系统学习中国通用手语</span>
      </div>
      <div class="category-tabs">
        <div
          v-for="(course, index) in videoCourses"
          :key="course.id"
          :class="['category-item', { active: currentCourseId === course.id }]"
          :style="{ '--delay': index * 0.1 + 's' }"
          @click="selectCourse(course)"
        >
          <span class="cat-icon">{{ course.icon }}</span>
          <span class="cat-name">{{ course.title }}</span>
          <span class="cat-count">{{ course.lessons.length }}课时</span>
          <div class="category-glow" v-if="currentCourseId === course.id"></div>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- 课程列表 -->
      <div class="course-section" v-if="!currentLesson">
        <h3 class="section-title">
          <span class="title-icon">{{ selectedCourse?.icon || '📚' }}</span>
          {{ selectedCourse?.title || '全部课程' }}
          <span class="section-subtitle">{{ selectedCourse?.description }}</span>
        </h3>

        <div class="lessons-grid">
          <div
            v-for="(lesson, index) in displayedLessons"
            :key="lesson.id"
            class="lesson-card glass-card"
            :style="{ '--delay': index * 0.1 + 's' }"
            @click="playLesson(lesson)"
          >
            <div class="lesson-cover">
              <div class="cover-overlay"></div>
              <div class="play-icon">
                <el-icon size="48"><VideoPlay /></el-icon>
              </div>
              <div class="lesson-duration">
                <el-icon size="14"><VideoCameraFilled /></el-icon>
                {{ lesson.duration }}
              </div>
              <div class="completed-badge" v-if="isLessonCompleted(lesson.id)">
                <el-icon><Check /></el-icon> 已学习
              </div>
              <!-- 悬停时显示的按钮 -->
              <div class="hover-action">
                <span class="action-btn">立即学习</span>
              </div>
            </div>
            <div class="lesson-info">
              <h4>{{ lesson.title }}</h4>
              <p>{{ lesson.description }}</p>
              <div class="lesson-meta">
                <span class="meta-item">
                  <el-icon><Clock /></el-icon>
                  {{ lesson.duration }}
                </span>
                <span class="progress-dot" :class="{ completed: isLessonCompleted(lesson.id) }">
                  {{ isLessonCompleted(lesson.id) ? '已完成' : '未学习' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 视频播放面板 -->
      <div class="video-panel glass-panel" v-if="currentLesson">
        <div class="panel-header">
          <div class="lesson-title">
            <div class="title-badge">正在学习</div>
            <h3>{{ currentLesson.title }}</h3>
            <p>{{ currentLesson.description }}</p>
          </div>
          <el-button class="back-btn" @click="closePlayer">
            <el-icon><ArrowLeft /></el-icon>
            返回课程
          </el-button>
        </div>

        <!-- 视频播放区 -->
        <div class="video-section">
          <div class="video-container">
            <video
              ref="videoRef"
              :src="currentLesson.video"
              @timeupdate="onTimeUpdate"
              @ended="onVideoEnded"
              @loadedmetadata="onVideoLoaded"
              controls
              autoplay
            ></video>
          </div>
          <div class="video-controls glass-controls">
            <div class="control-left">
              <span class="control-label">播放速度</span>
              <div class="speed-buttons">
                <button
                  v-for="speed in [0.5, 0.75, 1, 1.25, 1.5]"
                  :key="speed"
                  :class="['speed-btn', { active: playbackRate === speed }]"
                  @click="changePlaybackRate(speed)"
                >
                  {{ speed }}x
                </button>
              </div>
            </div>
            <div class="control-right">
              <el-button
                v-if="hasPrevLesson"
                class="nav-btn"
                @click="playPrevLesson"
              >
                <el-icon><ArrowLeft /></el-icon> 上一课
              </el-button>
              <el-button
                v-if="hasNextLesson"
                class="nav-btn primary"
                @click="playNextLesson"
              >
                下一课 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 课程列表侧边栏 -->
        <div class="lesson-sidebar">
          <h4>
            <el-icon><List /></el-icon>
            课程目录
          </h4>
          <div class="lesson-list">
            <div
              v-for="(lesson, index) in selectedCourse?.lessons"
              :key="lesson.id"
              :class="['lesson-item', {
                active: currentLesson?.id === lesson.id,
                completed: isLessonCompleted(lesson.id)
              }]"
              @click="playLesson(lesson)"
            >
              <span class="lesson-num">{{ index + 1 }}</span>
              <span class="lesson-name">{{ lesson.title }}</span>
              <span class="lesson-status">
                <el-icon v-if="isLessonCompleted(lesson.id)" class="check-icon"><Check /></el-icon>
                <el-icon v-else-if="currentLesson?.id === lesson.id" class="playing-icon"><VideoPlay /></el-icon>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 学习统计 -->
    <div class="learning-stats glass-stats">
      <div class="stats-header">
        <span class="stats-icon">📊</span>
        <span>学习统计</span>
      </div>
      <div class="stats-content">
        <div class="stat-item" v-for="(stat, index) in statsData" :key="index">
          <div class="stat-ring">
            <svg viewBox="0 0 36 36">
              <path
                class="ring-bg"
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                class="ring-progress"
                :style="{ '--progress': stat.progress }"
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div class="stat-value">{{ stat.value }}</div>
          </div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, VideoPlay, Close, ArrowLeft, ArrowRight, Clock, List, VideoCameraFilled } from '@element-plus/icons-vue'
import { getCourses } from '../data/appDataStore'

const currentCourseId = ref(1)
const currentLesson = ref(null)
const playbackRate = ref(1)
const videoRef = ref(null)
const completedLessons = ref([])

const stats = ref({
  lessonsCompleted: 0,
  totalMinutes: 0,
  streak: 1
})

// 使用导入的课程数据
const videoCourses = ref([])

const loadCourses = () => {
  videoCourses.value = getCourses()
  if (videoCourses.value.length > 0 && !videoCourses.value.some(course => course.id === currentCourseId.value)) {
    currentCourseId.value = videoCourses.value[0].id
  }
}

// 当前选中的课程
const selectedCourse = computed(() => {
  return videoCourses.value.find(c => c.id === currentCourseId.value)
})

// 显示的课程列表
const displayedLessons = computed(() => {
  return selectedCourse.value?.lessons || []
})

// 完成进度百分比
const completionPercentage = computed(() => {
  const total = videoCourses.value.reduce((sum, course) => sum + course.lessons.length, 0)
  if (total === 0) return 0
  return Math.round((completedLessons.value.length / total) * 100)
})

// 统计数据
const statsData = computed(() => [
  { value: stats.value.lessonsCompleted, label: '已学课时', progress: completionPercentage.value },
  { value: stats.value.totalMinutes, label: '学习时长', progress: Math.min(stats.value.totalMinutes / 60 * 100, 100) },
  { value: stats.value.streak, label: '连续天数', progress: Math.min(stats.value.streak / 7 * 100, 100) },
  { value: completionPercentage.value + '%', label: '完成进度', progress: completionPercentage.value }
])

// 是否有上一课
const hasPrevLesson = computed(() => {
  if (!currentLesson.value || !selectedCourse.value) return false
  const currentIndex = selectedCourse.value.lessons.findIndex(l => l.id === currentLesson.value.id)
  return currentIndex > 0
})

// 是否有下一课
const hasNextLesson = computed(() => {
  if (!currentLesson.value || !selectedCourse.value) return false
  const currentIndex = selectedCourse.value.lessons.findIndex(l => l.id === currentLesson.value.id)
  return currentIndex < selectedCourse.value.lessons.length - 1
})

// 选择课程
const selectCourse = (course) => {
  currentCourseId.value = course.id
  currentLesson.value = null
}

// 播放课时
const playLesson = (lesson) => {
  currentLesson.value = lesson
}

// 关闭播放器
const closePlayer = () => {
  currentLesson.value = null
}

// 播放上一课
const playPrevLesson = () => {
  if (!selectedCourse.value || !currentLesson.value) return
  const currentIndex = selectedCourse.value.lessons.findIndex(l => l.id === currentLesson.value.id)
  if (currentIndex > 0) {
    currentLesson.value = selectedCourse.value.lessons[currentIndex - 1]
  }
}

// 播放下一课
const playNextLesson = () => {
  if (!selectedCourse.value || !currentLesson.value) return
  const currentIndex = selectedCourse.value.lessons.findIndex(l => l.id === currentLesson.value.id)
  if (currentIndex < selectedCourse.value.lessons.length - 1) {
    currentLesson.value = selectedCourse.value.lessons[currentIndex + 1]
  }
}

// 检查课时是否已完成
const isLessonCompleted = (lessonId) => {
  return completedLessons.value.includes(lessonId)
}

// 标记课时完成
const markLessonCompleted = (lessonId) => {
  if (!completedLessons.value.includes(lessonId)) {
    completedLessons.value.push(lessonId)
    stats.value.lessonsCompleted = completedLessons.value.length
    saveProgress()
  }
}

// 更改播放速度
const changePlaybackRate = (rate) => {
  playbackRate.value = rate
  if (videoRef.value) {
    videoRef.value.playbackRate = rate
  }
}

// 视频加载完成
const onVideoLoaded = () => {
  if (videoRef.value) {
    videoRef.value.playbackRate = playbackRate.value
  }
}

// 视频时间更新
const onTimeUpdate = () => {
  // 记录学习时长
  if (videoRef.value && !videoRef.value.paused) {
    // 每分钟更新一次统计
  }
}

// 视频播放完成
const onVideoEnded = () => {
  if (currentLesson.value) {
    markLessonCompleted(currentLesson.value.id)
    ElMessage.success({
      message: '本节课学习完成！',
      type: 'success',
      duration: 2000
    })

    // 自动播放下一课
    if (hasNextLesson.value) {
      setTimeout(() => {
        playNextLesson()
      }, 1500)
    }
  }
}

// 保存进度
const saveProgress = () => {
  const learningHistory = JSON.parse(localStorage.getItem('learningHistory') || '[]')
  const completedCourses = videoCourses.value.filter(course =>
    course.lessons.length > 0 && course.lessons.every(lesson => completedLessons.value.includes(lesson.id))
  ).length

  localStorage.setItem('videoLearningProgress', JSON.stringify({
    completedLessons: completedLessons.value,
    stats: stats.value,
    lastUpdate: new Date().toISOString()
  }))

  localStorage.setItem('learningProgress', JSON.stringify({
    learnedWords: learningHistory.length,
    completedCourses,
    completedLessons: completedLessons.value.length,
    lastUpdate: new Date().toISOString()
  }))
}

// 加载进度
const loadProgress = () => {
  const saved = localStorage.getItem('videoLearningProgress')
  if (saved) {
    const data = JSON.parse(saved)
    completedLessons.value = data.completedLessons || []
    stats.value = { ...stats.value, ...data.stats }
    return
  }

  const legacyProgress = localStorage.getItem('learningProgress')
  if (legacyProgress) {
    const parsed = JSON.parse(legacyProgress)
    if (Array.isArray(parsed.completedLessons)) {
      completedLessons.value = parsed.completedLessons
    }
  }
}

onMounted(() => {
  loadCourses()
  loadProgress()
})

watch(playbackRate, (newRate) => {
  if (videoRef.value) {
    videoRef.value.playbackRate = newRate
  }
})
</script>

<style scoped>
.sign-learning {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --glass-bg: rgba(255, 255, 255, 0.75);
  --glass-border: rgba(255, 255, 255, 0.5);
  --glass-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  --radius-card: 16px;
  --radius-sm: 8px;
  --color-primary: #667eea;
  --color-secondary: #764ba2;
  --color-success: #10b981;

  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7ff 0%, #f0e6ff 100%);
}

/* 课程导航 */
.course-nav {
  margin-bottom: 32px;
}

.nav-header {
  margin-bottom: 20px;
}

.nav-header h2 {
  margin: 0 0 4px;
  font-size: 28px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-header .subtitle {
  font-size: 14px;
  color: #6b7280;
}

.category-tabs {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding: 8px 4px;
}

.category-item {
  position: relative;
  padding: 20px 28px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 150px;
  animation: fadeInUp 0.5s ease-out forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.category-item:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
}

.category-item.active {
  background: var(--primary-gradient);
  color: #fff;
  border: none;
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
}

.category-glow {
  position: absolute;
  inset: -2px;
  border-radius: calc(var(--radius-card) + 2px);
  background: var(--primary-gradient);
  z-index: -1;
  opacity: 0.5;
  filter: blur(15px);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.05); }
}

.cat-icon {
  font-size: 32px;
  margin-bottom: 10px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.cat-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.cat-count {
  font-size: 12px;
  opacity: 0.75;
}

/* 主内容 */
.main-content {
  min-height: 400px;
}

.section-title {
  font-size: 20px;
  color: #1f2937;
  margin: 0 0 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 24px;
}

.section-subtitle {
  font-size: 14px;
  color: #6b7280;
  font-weight: 400;
}

/* 毛玻璃课程卡片 */
.lessons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: fadeInUp 0.5s ease-out forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

.glass-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 50px rgba(102, 126, 234, 0.25);
  border-color: var(--color-primary);
}

.lesson-cover {
  position: relative;
  height: 200px;
  background: var(--primary-gradient);
  overflow: hidden;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.3) 100%);
}

.play-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  transition: all 0.4s ease;
  border: 2px solid rgba(255,255,255,0.3);
}

.glass-card:hover .play-icon {
  transform: translate(-50%, -50%) scale(1.15);
  background: rgba(255, 255, 255, 0.35);
  box-shadow: 0 0 40px rgba(255,255,255,0.4);
}

.lesson-duration {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #fff;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.completed-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: var(--color-success);
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* 悬停显示的立即学习按钮 */
.hover-action {
  position: absolute;
  inset: 0;
  background: rgba(102, 126, 234, 0.7);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
}

.glass-card:hover .hover-action {
  opacity: 1;
}

.action-btn {
  padding: 14px 32px;
  background: #fff;
  color: var(--color-primary);
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  transform: translateY(20px);
  transition: all 0.3s ease;
}

.glass-card:hover .action-btn {
  transform: translateY(0);
}

.lesson-info {
  padding: 20px;
}

.lesson-info h4 {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
}

.lesson-info p {
  margin: 0 0 12px;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

.lesson-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #9ca3af;
}

.progress-dot {
  padding: 4px 10px;
  background: #f3f4f6;
  border-radius: 12px;
  color: #6b7280;
  font-size: 12px;
}

.progress-dot.completed {
  background: #d1fae5;
  color: var(--color-success);
}

/* 视频播放面板 */
.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  overflow: hidden;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
}

.title-badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--primary-gradient);
  color: #fff;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 10px;
}

.lesson-title h3 {
  margin: 0 0 8px;
  font-size: 22px;
  color: #1f2937;
  font-weight: 600;
}

.lesson-title p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

.back-btn {
  background: transparent;
  border: 1px solid #d1d5db;
  color: #6b7280;
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #f9fafb;
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.video-section {
  padding: 24px;
  background: #0f0f0f;
}

.video-container {
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

.video-container video {
  width: 100%;
  max-height: 520px;
  display: block;
}

.glass-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255,255,255,0.1);
}

.control-label {
  color: rgba(255,255,255,0.7);
  font-size: 14px;
  margin-right: 16px;
}

.control-left {
  display: flex;
  align-items: center;
}

.speed-buttons {
  display: flex;
  gap: 6px;
}

.speed-btn {
  padding: 8px 14px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.8);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
}

.speed-btn:hover {
  background: rgba(255,255,255,0.2);
}

.speed-btn.active {
  background: var(--primary-gradient);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.control-right {
  display: flex;
  gap: 12px;
}

.nav-btn {
  padding: 10px 20px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-btn:hover {
  background: rgba(255,255,255,0.2);
}

.nav-btn.primary {
  background: var(--primary-gradient);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.nav-btn.primary:hover {
  transform: translateX(4px);
}

/* 课程列表侧边栏 */
.lesson-sidebar {
  padding: 24px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
}

.lesson-sidebar h4 {
  margin: 0 0 20px;
  font-size: 16px;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.lesson-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: rgba(102, 126, 234, 0.05);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.lesson-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.lesson-item.active {
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.lesson-item.completed:not(.active) {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.2);
}

.lesson-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.lesson-item.active .lesson-num {
  background: rgba(255, 255, 255, 0.2);
}

.lesson-item.completed:not(.active) .lesson-num {
  background: var(--color-success);
  color: #fff;
}

.lesson-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lesson-status {
  flex-shrink: 0;
}

.check-icon {
  color: var(--color-success);
}

.playing-icon {
  animation: playPulse 1s ease-in-out infinite;
}

@keyframes playPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 学习统计 - 毛玻璃效果 */
.glass-stats {
  margin-top: 32px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  padding: 24px;
  box-shadow: var(--glass-shadow);
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.stats-icon {
  font-size: 20px;
}

.stats-content {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
}

.stat-item {
  text-align: center;
  min-width: 100px;
}

.stat-ring {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 12px;
}

.stat-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: #e5e7eb;
  stroke-width: 3;
}

.ring-progress {
  fill: none;
  stroke: url(#gradient);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 100;
  stroke-dashoffset: calc(100 - var(--progress, 0));
  transition: stroke-dashoffset 1s ease;
}

.stat-ring::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--primary-gradient);
  border-radius: 50%;
  opacity: 0.1;
}

.stat-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 20px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

/* 定义SVG渐变 */
.sign-learning::before {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  overflow: hidden;
}

/* 响应式 */
@media (max-width: 768px) {
  .sign-learning {
    padding: 16px;
  }

  .category-tabs {
    flex-wrap: nowrap;
    padding-bottom: 12px;
  }

  .category-item {
    min-width: 130px;
    padding: 16px 20px;
  }

  .lessons-grid {
    grid-template-columns: 1fr;
  }

  .lesson-cover {
    height: 180px;
  }

  .lesson-list {
    grid-template-columns: 1fr;
  }

  .glass-controls {
    flex-direction: column;
    gap: 16px;
  }

  .control-left, .control-right {
    width: 100%;
    justify-content: center;
  }

  .stats-content {
    justify-content: center;
  }

  .stat-item {
    min-width: 45%;
  }
}
</style>
