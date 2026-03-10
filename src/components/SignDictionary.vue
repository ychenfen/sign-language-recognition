<template>
  <div class="sign-dictionary">
    <!-- 搜索区域 -->
    <div class="search-section glass-card">
      <div class="search-header">
        <h2 class="search-title">
          <span class="title-icon">📖</span>
          手语词典
        </h2>
        <p class="search-subtitle">搜索并学习常用手语词汇</p>
      </div>
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="输入汉字或拼音搜索手语..."
          size="large"
          clearable
          @input="handleSearch"
          class="glass-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="search-tips">
        <span class="tips-label">热门搜索：</span>
        <div class="hot-tags">
          <span
            v-for="tag in hotTags"
            :key="tag"
            class="hot-tag"
            @click="searchKeyword = tag; handleSearch()"
          >
            {{ tag }}
          </span>
        </div>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav glass-card">
      <div class="category-list">
        <div
          class="category-item"
          :class="{ active: currentCategory === '全部' }"
          @click="currentCategory = '全部'"
        >
          <span class="category-name">全部</span>
          <span class="category-count">{{ vocabulary.length }}</span>
        </div>
        <div
          v-for="cat in categories"
          :key="cat"
          class="category-item"
          :class="{ active: currentCategory === cat }"
          @click="currentCategory = cat"
        >
          <span class="category-name">{{ cat }}</span>
          <span class="category-count">{{ getCategoryCount(cat) }}</span>
        </div>
      </div>
    </div>

    <!-- 词汇统计 -->
    <div class="stats-bar">
      <div class="stats-info">
        <span class="stats-count">{{ filteredWords.length }}</span>
        <span class="stats-label">个词汇</span>
      </div>
      <div class="view-toggle">
        <el-button-group>
          <el-button
            :type="viewMode === 'grid' ? 'primary' : 'default'"
            @click="viewMode = 'grid'"
            size="small"
          >
            <el-icon><Grid /></el-icon>
          </el-button>
          <el-button
            :type="viewMode === 'list' ? 'primary' : 'default'"
            @click="viewMode = 'list'"
            size="small"
          >
            <el-icon><List /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 词汇列表 -->
    <TransitionGroup
      name="card-list"
      tag="div"
      :class="['vocabulary-grid', viewMode === 'list' ? 'list-view' : '']"
    >
      <div
        v-for="(word, index) in filteredWords"
        :key="word.id"
        class="word-card glass-card"
        :style="{ '--delay': index * 0.05 + 's' }"
        @click="showWordDetail(word)"
      >
        <div class="card-media">
          <div class="word-image">
            <img :src="word.image" :alt="word.word" @error="handleImageError" />
            <div class="image-overlay">
              <span class="view-btn">查看详情</span>
            </div>
          </div>
          <div class="video-badge" v-if="word.video">
            <el-icon><VideoPlay /></el-icon>
            <span>视频</span>
          </div>
        </div>
        <div class="card-content">
          <h3 class="word-name">{{ word.word }}</h3>
          <p class="word-pinyin">{{ word.pinyin }}</p>
          <div class="word-meta">
            <span class="category-tag" :class="getCategoryClass(word.category)">
              {{ word.category }}
            </span>
          </div>
        </div>
        <div class="card-actions">
          <button
            class="favorite-btn"
            :class="{ active: word.isFavorite }"
            @click.stop="toggleFavorite(word)"
          >
            <el-icon>
              <component :is="word.isFavorite ? StarFilled : Star" />
            </el-icon>
          </button>
        </div>
      </div>
    </TransitionGroup>

    <!-- 空状态 -->
    <div v-if="filteredWords.length === 0" class="empty-state glass-card">
      <div class="empty-icon">🔍</div>
      <h3>暂无匹配的词汇</h3>
      <p>试试其他关键词或分类</p>
      <el-button type="primary" @click="resetSearch">清除搜索</el-button>
    </div>

    <!-- 词汇详情弹窗 -->
    <Transition name="modal">
      <div v-if="detailVisible" class="modal-overlay" @click.self="detailVisible = false">
        <div class="word-detail-modal glass-card">
          <button class="modal-close" @click="detailVisible = false">
            <el-icon><Close /></el-icon>
          </button>

          <div class="detail-content" v-if="currentWord">
            <!-- 视频教学 -->
            <div class="detail-section video-section" v-if="currentWord.video">
              <div class="video-container">
                <video
                  ref="videoRef"
                  :src="currentWord.video"
                  controls
                  class="teaching-video"
                  preload="metadata"
                ></video>
              </div>
            </div>

            <!-- 基本信息 -->
            <div class="detail-header">
              <div class="detail-image">
                <img :src="currentWord.image" :alt="currentWord.word" @error="handleImageError" />
              </div>
              <div class="detail-info">
                <h2 class="detail-title">{{ currentWord.word }}</h2>
                <div class="detail-meta">
                  <span class="meta-item">
                    <span class="meta-label">拼音</span>
                    <span class="meta-value">{{ currentWord.pinyin }}</span>
                  </span>
                  <span class="meta-item">
                    <span class="meta-label">分类</span>
                    <span class="meta-value category-tag" :class="getCategoryClass(currentWord.category)">
                      {{ currentWord.category }}
                    </span>
                  </span>
                </div>
                <p class="detail-desc">{{ currentWord.description }}</p>
                <div class="detail-actions">
                  <el-button
                    :type="currentWord.isFavorite ? 'warning' : 'default'"
                    @click="toggleFavorite(currentWord)"
                    round
                  >
                    <el-icon><component :is="currentWord.isFavorite ? StarFilled : Star" /></el-icon>
                    {{ currentWord.isFavorite ? '已收藏' : '收藏' }}
                  </el-button>
                  <el-button type="primary" @click="playVideo" v-if="currentWord.video" round>
                    <el-icon><VideoPlay /></el-icon>
                    播放视频
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 动作分解 -->
            <div class="detail-section steps-section">
              <h3 class="section-title">
                <span class="title-icon">👋</span>
                动作分解
              </h3>
              <div class="steps-list">
                <div
                  v-for="(step, index) in currentWord.steps"
                  :key="index"
                  class="step-item"
                >
                  <div class="step-number">{{ index + 1 }}</div>
                  <div class="step-content">
                    <p>{{ step }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 使用场景 -->
            <div class="detail-section examples-section" v-if="currentWord.examples && currentWord.examples.length">
              <h3 class="section-title">
                <span class="title-icon">💬</span>
                使用场景
              </h3>
              <div class="examples-list">
                <div v-for="(example, index) in currentWord.examples" :key="index" class="example-item">
                  <span class="example-icon">•</span>
                  <p>{{ example }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Star, StarFilled, VideoPlay, Close, Grid, List } from '@element-plus/icons-vue'
import { getWords, getFavorites, saveFavorites } from '../data/appDataStore'

const searchKeyword = ref('')
const currentCategory = ref('全部')
const detailVisible = ref(false)
const currentWord = ref(null)
const videoRef = ref(null)
const viewMode = ref('grid')

const hotTags = ['谢谢', '爱', '帮助', '高兴', '爸爸']

const vocabulary = ref([])
const categories = computed(() => [...new Set(vocabulary.value.map(item => item.category))])

const loadVocabulary = () => {
  vocabulary.value = getWords().map(item => ({
    ...item,
    isFavorite: false
  }))
}

// 获取分类数量
const getCategoryCount = (category) => {
  return vocabulary.value.filter(w => w.category === category).length
}

// 获取分类样式类
const getCategoryClass = (category) => {
  const classMap = {
    '基础词汇': 'green',
    '情绪表达': 'pink',
    '家庭称谓': 'orange',
    '姓氏': 'blue'
  }
  return classMap[category] || 'purple'
}

// 过滤词汇
const filteredWords = computed(() => {
  let result = vocabulary.value

  // 按分类筛选
  if (currentCategory.value !== '全部') {
    result = result.filter(w => w.category === currentCategory.value)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(w =>
      w.word.includes(searchKeyword.value) ||
      w.pinyin.toLowerCase().includes(keyword) ||
      w.description.includes(searchKeyword.value)
    )
  }

  return result
})

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

// 重置搜索
const resetSearch = () => {
  searchKeyword.value = ''
  currentCategory.value = '全部'
}

// 显示词汇详情
const showWordDetail = (word) => {
  currentWord.value = word
  detailVisible.value = true
  // 记录学习历史
  addToHistory(word)
}

// 播放视频
const playVideo = () => {
  if (videoRef.value) {
    videoRef.value.play()
    videoRef.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

// 图片加载错误处理
const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23f0f0f0" width="100" height="100"/><text x="50" y="55" text-anchor="middle" fill="%23999" font-size="14">暂无图片</text></svg>'
}

// 切换收藏
const toggleFavorite = (word) => {
  word.isFavorite = !word.isFavorite

  if (word.isFavorite) {
    ElMessage.success('已添加到收藏')
    saveFavorite(word)
  } else {
    ElMessage.info('已取消收藏')
    removeFavorite(word.id)
  }
}

// 保存收藏
const saveFavorite = (word) => {
  const favorites = getFavorites()
  if (!favorites.find(f => f.id === word.id)) {
    favorites.push({
      id: word.id,
      word: word.word,
      name: word.word,
      pinyin: word.pinyin,
      category: word.category,
      time: new Date().toLocaleString()
    })
    saveFavorites(favorites)
  }
}

// 移除收藏
const removeFavorite = (wordId) => {
  const favorites = getFavorites().filter(f => f.id !== wordId)
  saveFavorites(favorites)
}

// 添加学习历史
const addToHistory = (word) => {
  let history = JSON.parse(localStorage.getItem('learningHistory') || '[]')
  // 移除重复
  history = history.filter(h => h.id !== word.id)
  // 添加到最前面
  history.unshift({
    id: word.id,
    word: word.word,
    title: word.word,
    name: word.word,
    pinyin: word.pinyin,
    type: 'word',
    category: word.category,
    time: new Date().toLocaleString()
  })
  // 只保留最近50条
  if (history.length > 50) history = history.slice(0, 50)
  localStorage.setItem('learningHistory', JSON.stringify(history))
}

// 加载收藏状态
onMounted(() => {
  loadVocabulary()
  const favorites = getFavorites()
  vocabulary.value.forEach(word => {
    word.isFavorite = favorites.some(f => f.id === word.id)
  })
})
</script>

<style scoped>
.sign-dictionary {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --glass-bg: rgba(255, 255, 255, 0.8);
  --glass-border: rgba(255, 255, 255, 0.5);
  --glass-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  --radius-card: 16px;
  --radius-sm: 8px;

  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

/* 毛玻璃卡片基础样式 */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  box-shadow: var(--glass-shadow);
}

/* 搜索区域 */
.search-section {
  max-width: 700px;
  margin: 0 auto 24px;
  padding: 32px;
  text-align: center;
  animation: fadeInDown 0.6s ease-out;
}

.search-header {
  margin-bottom: 24px;
}

.search-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
  -webkit-text-fill-color: initial;
}

.search-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.search-box {
  margin-bottom: 16px;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.1);
  padding: 4px 16px;
  transition: all 0.3s ease;
}

.search-box :deep(.el-input__wrapper:hover),
.search-box :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.2);
}

.search-tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tips-label {
  font-size: 13px;
  color: #909399;
}

.hot-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.hot-tag {
  padding: 4px 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 20px;
  font-size: 13px;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.hot-tag:hover {
  background: var(--primary-gradient);
  color: #fff;
  transform: translateY(-2px);
}

/* 分类导航 */
.category-nav {
  margin-bottom: 20px;
  padding: 16px 24px;
  overflow-x: auto;
  animation: fadeInUp 0.5s ease-out;
}

.category-list {
  display: flex;
  gap: 12px;
  min-width: max-content;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid transparent;
}

.category-item:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

.category-item.active {
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.category-name {
  font-size: 14px;
  font-weight: 500;
}

.category-count {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.3);
}

.category-item.active .category-count {
  background: rgba(255, 255, 255, 0.3);
}

/* 统计栏 */
.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 8px;
}

.stats-info {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stats-count {
  font-size: 24px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

/* 词汇网格 */
.vocabulary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.vocabulary-grid.list-view {
  grid-template-columns: 1fr;
}

.vocabulary-grid.list-view .word-card {
  display: flex;
  flex-direction: row;
  padding: 16px;
}

.vocabulary-grid.list-view .card-media {
  width: 120px;
  flex-shrink: 0;
}

.vocabulary-grid.list-view .word-image {
  height: 90px;
}

.vocabulary-grid.list-view .card-content {
  flex: 1;
  text-align: left;
  padding: 0 16px;
}

.vocabulary-grid.list-view .card-actions {
  position: relative;
  top: auto;
  right: auto;
}

/* 词汇卡片 */
.word-card {
  padding: 0;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  animation: fadeInUp 0.5s ease-out backwards;
  animation-delay: var(--delay);
}

.word-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.25);
}

.card-media {
  position: relative;
}

.word-image {
  width: 100%;
  height: 140px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf3 100%);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.word-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.4s ease;
}

.word-card:hover .word-image img {
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.word-card:hover .image-overlay {
  opacity: 1;
}

.view-btn {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 20px;
  border: 2px solid #fff;
  border-radius: 20px;
  transform: translateY(10px);
  transition: transform 0.3s ease;
}

.word-card:hover .view-btn {
  transform: translateY(0);
}

.video-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(102, 126, 234, 0.9);
  backdrop-filter: blur(4px);
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
}

.card-content {
  padding: 16px;
  text-align: center;
}

.word-name {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #303133;
}

.word-pinyin {
  font-size: 13px;
  color: #909399;
  margin: 0 0 12px;
}

.word-meta {
  display: flex;
  justify-content: center;
}

/* 分类标签颜色 */
.category-tag {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 500;
}

.category-tag.green {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
}

.category-tag.pink {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}

.category-tag.orange {
  background: rgba(230, 162, 60, 0.15);
  color: #e6a23c;
}

.category-tag.blue {
  background: rgba(64, 158, 255, 0.15);
  color: #409eff;
}

.category-tag.purple {
  background: rgba(118, 75, 162, 0.15);
  color: #764ba2;
}

.category-tag.cyan {
  background: rgba(0, 206, 209, 0.15);
  color: #00ced1;
}

.category-tag.yellow {
  background: rgba(255, 193, 7, 0.15);
  color: #d4a000;
}

.category-tag.red {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}

.category-tag.default {
  background: rgba(144, 147, 153, 0.15);
  color: #909399;
}

.card-actions {
  position: absolute;
  top: 10px;
  right: 10px;
}

.favorite-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #909399;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.favorite-btn:hover {
  transform: scale(1.1);
}

.favorite-btn.active {
  color: #f7ba2a;
  background: rgba(247, 186, 42, 0.15);
}

.favorite-btn.active:hover {
  animation: heartBeat 0.4s ease;
}

/* 空状态 */
.empty-state {
  max-width: 400px;
  margin: 60px auto;
  padding: 48px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  color: #303133;
  margin: 0 0 8px;
}

.empty-state p {
  font-size: 14px;
  color: #909399;
  margin: 0 0 24px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.word-detail-modal {
  width: 100%;
  max-width: 750px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 32px;
  background: rgba(255, 255, 255, 0.95);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.05);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #606266;
  transition: all 0.3s ease;
  z-index: 10;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #303133;
}

/* 详情内容 */
.detail-content {
  padding: 0;
}

.video-section {
  margin-bottom: 24px;
}

.video-container {
  background: #000;
  border-radius: var(--radius-card);
  overflow: hidden;
}

.teaching-video {
  width: 100%;
  max-height: 400px;
  display: block;
}

.detail-header {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  border-radius: var(--radius-card);
}

.detail-image {
  flex-shrink: 0;
  width: 160px;
  height: 160px;
  background: #fff;
  border-radius: var(--radius-card);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.detail-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.detail-info {
  flex: 1;
}

.detail-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.detail-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  font-size: 13px;
  color: #909399;
}

.meta-value {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.detail-desc {
  font-size: 14px;
  color: #606266;
  margin: 0 0 16px;
  line-height: 1.6;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

.detail-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 2px solid transparent;
  border-image: var(--primary-gradient) 1;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
}

.step-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  padding-top: 4px;
}

.step-content p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.example-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.1), transparent);
  border-left: 3px solid var(--primary-color);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.example-icon {
  color: var(--primary-color);
  font-weight: bold;
}

.example-item p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

@keyframes heartBeat {
  0%, 100% { transform: scale(1.1); }
  50% { transform: scale(1.3); }
}

/* 列表过渡动画 */
.card-list-enter-active,
.card-list-leave-active {
  transition: all 0.4s ease;
}

.card-list-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.card-list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.card-list-move {
  transition: transform 0.4s ease;
}

/* 模态框过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .word-detail-modal,
.modal-leave-to .word-detail-modal {
  transform: scale(0.9) translateY(20px);
}

/* 响应式 */
@media (max-width: 768px) {
  .sign-dictionary {
    padding: 16px;
  }

  .search-section {
    padding: 24px 16px;
  }

  .search-title {
    font-size: 24px;
  }

  .category-nav {
    padding: 12px 16px;
  }

  .vocabulary-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .word-image {
    height: 100px;
  }

  .card-content {
    padding: 12px;
  }

  .word-name {
    font-size: 16px;
  }

  .word-detail-modal {
    padding: 20px;
    margin: 10px;
  }

  .detail-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .detail-meta {
    justify-content: center;
  }

  .detail-actions {
    justify-content: center;
  }

  .vocabulary-grid.list-view .word-card {
    flex-direction: column;
  }

  .vocabulary-grid.list-view .card-media {
    width: 100%;
  }

  .vocabulary-grid.list-view .card-content {
    text-align: center;
    padding: 16px;
  }
}

/* 滚动条美化 */
.word-detail-modal::-webkit-scrollbar {
  width: 6px;
}

.word-detail-modal::-webkit-scrollbar-track {
  background: transparent;
}

.word-detail-modal::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.word-detail-modal::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}
</style>
