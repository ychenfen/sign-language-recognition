<template>
  <div class="community">
    <!-- 页面头部 -->
    <div class="community-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <span class="title-icon">💬</span>
            手语学习社区
          </h1>
          <p class="page-desc">分享学习心得，交流手语技巧</p>
        </div>
        <el-button
          class="post-btn"
          @click="showPostDialog = true"
          :disabled="!isLoggedIn"
        >
          <span class="btn-icon">✍️</span>
          发布帖子
        </el-button>
      </div>

      <!-- 统计信息 -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-value">{{ posts.length }}</span>
          <span class="stat-label">帖子</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ totalComments }}</span>
          <span class="stat-label">评论</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ totalLikes }}</span>
          <span class="stat-label">点赞</span>
        </div>
      </div>
    </div>

    <!-- 未登录提示 -->
    <div class="login-notice" v-if="!isLoggedIn">
      <span class="notice-icon">👋</span>
      <span class="notice-text">登录后可发帖、评论和点赞</span>
      <el-button class="notice-btn" size="small" @click="$emit('go-login')">
        立即登录
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar glass-bar">
      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          :class="['filter-tab', { active: sortBy === tab.key }]"
          @click="sortBy = tab.key"
          :disabled="tab.key === 'my' && !isLoggedIn"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>
      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input
          v-model="searchKeyword"
          type="text"
          class="search-input"
          placeholder="搜索帖子..."
        />
        <button v-if="searchKeyword" class="clear-btn" @click="searchKeyword = ''">
          <el-icon><Close /></el-icon>
        </button>
      </div>
    </div>

    <!-- 帖子列表 -->
    <div class="posts-container">
      <TransitionGroup name="post-list" tag="div" class="posts-list">
        <article
          v-for="(post, index) in filteredPosts"
          :key="post.id"
          class="post-card glass-card"
          :style="{ '--delay': index * 0.05 + 's' }"
        >
          <!-- 帖子头部 -->
          <header class="post-header">
            <div class="author-info">
              <div class="avatar-wrapper">
                <el-avatar :size="44" class="author-avatar">
                  {{ post.author.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="online-dot" v-if="post.author === currentUser"></span>
              </div>
              <div class="author-meta">
                <span class="author-name">{{ post.author }}</span>
                <span class="post-time">
                  <el-icon><Clock /></el-icon>
                  {{ post.time }}
                </span>
              </div>
            </div>
            <el-dropdown v-if="post.author === currentUser" trigger="click">
              <button class="more-btn">
                <el-icon><MoreFilled /></el-icon>
              </button>
              <template #dropdown>
                <el-dropdown-menu class="action-dropdown">
                  <el-dropdown-item @click="editPost(post)">
                    <el-icon><Edit /></el-icon>
                    编辑帖子
                  </el-dropdown-item>
                  <el-dropdown-item @click="deletePost(post.id)" class="danger">
                    <el-icon><Delete /></el-icon>
                    删除帖子
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </header>

          <!-- 帖子内容 -->
          <div class="post-body">
            <h2 class="post-title">{{ post.title }}</h2>
            <p class="post-content">{{ post.content }}</p>
            <div class="post-tags" v-if="post.tags && post.tags.length">
              <span
                v-for="tag in post.tags"
                :key="tag"
                :class="['tag', `tag-${getTagType(tag)}`]"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 帖子操作栏 -->
          <footer class="post-footer">
            <div class="action-group">
              <button
                :class="['action-btn', { active: post.liked }]"
                @click="toggleLike(post)"
              >
                <el-icon class="action-icon">
                  <component :is="post.liked ? 'StarFilled' : 'Star'" />
                </el-icon>
                <span class="action-count">{{ post.likes }}</span>
                <span class="action-label">点赞</span>
              </button>

              <button
                :class="['action-btn', { active: expandedPostId === post.id }]"
                @click="toggleComments(post.id)"
              >
                <el-icon class="action-icon"><ChatDotRound /></el-icon>
                <span class="action-count">{{ post.comments.length }}</span>
                <span class="action-label">评论</span>
              </button>

              <button class="action-btn" @click="sharePost(post)">
                <el-icon class="action-icon"><Share /></el-icon>
                <span class="action-label">分享</span>
              </button>
            </div>
          </footer>

          <!-- 评论区 -->
          <Transition name="expand">
            <section class="comments-section" v-if="expandedPostId === post.id">
              <!-- 评论输入框 -->
              <div class="comment-input-wrapper" v-if="isLoggedIn">
                <el-avatar :size="36" class="input-avatar">
                  {{ currentUser.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="input-box">
                  <input
                    v-model="newComment[post.id]"
                    type="text"
                    class="comment-input"
                    :placeholder="`@${currentUser} 写下你的评论...`"
                    @keyup.enter="submitComment(post.id)"
                  />
                  <button
                    class="send-btn"
                    :disabled="!newComment[post.id]"
                    @click="submitComment(post.id)"
                  >
                    发送
                  </button>
                </div>
              </div>

              <!-- 评论列表 -->
              <div class="comments-list">
                <TransitionGroup name="comment-list">
                  <div
                    v-for="comment in post.comments"
                    :key="comment.id"
                    class="comment-item"
                  >
                    <el-avatar :size="32" class="comment-avatar">
                      {{ comment.author.charAt(0).toUpperCase() }}
                    </el-avatar>
                    <div class="comment-body">
                      <div class="comment-header">
                        <span class="comment-author">{{ comment.author }}</span>
                        <span class="comment-time">{{ comment.time }}</span>
                      </div>
                      <p class="comment-text">{{ comment.content }}</p>
                      <div class="comment-actions">
                        <button class="comment-action" @click="likeComment(post.id, comment.id)">
                          <el-icon><Pointer /></el-icon>
                          <span>{{ comment.likes }}</span>
                        </button>
                        <button class="comment-action" @click="replyComment(post.id, comment)">
                          回复
                        </button>
                      </div>
                    </div>
                  </div>
                </TransitionGroup>

                <div class="empty-comments" v-if="post.comments.length === 0">
                  <span class="empty-icon">💭</span>
                  <span class="empty-text">暂无评论，来说两句吧</span>
                </div>
              </div>
            </section>
          </Transition>
        </article>
      </TransitionGroup>

      <!-- 空状态 -->
      <div class="empty-state" v-if="filteredPosts.length === 0">
        <span class="empty-icon-large">📭</span>
        <h3>暂无帖子</h3>
        <p>{{ searchKeyword ? '换个关键词试试' : '成为第一个发帖的人吧' }}</p>
        <el-button class="create-btn" @click="showPostDialog = true" v-if="isLoggedIn && !searchKeyword">
          发布帖子
        </el-button>
      </div>
    </div>

    <!-- 发帖弹窗 -->
    <el-dialog
      v-model="showPostDialog"
      :title="postForm.id ? '编辑帖子' : '发布帖子'"
      width="600px"
      class="post-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <div class="form-group">
          <label class="form-label">标题</label>
          <input
            v-model="postForm.title"
            type="text"
            class="form-input"
            placeholder="一句话概括你想分享的内容"
            maxlength="50"
          />
          <span class="char-count">{{ postForm.title.length }}/50</span>
        </div>

        <div class="form-group">
          <label class="form-label">内容</label>
          <textarea
            v-model="postForm.content"
            class="form-textarea"
            placeholder="分享你的手语学习心得..."
            rows="6"
            maxlength="1000"
          ></textarea>
          <span class="char-count">{{ postForm.content.length }}/1000</span>
        </div>

        <div class="form-group">
          <label class="form-label">标签</label>
          <div class="tag-select">
            <button
              v-for="tag in availableTags"
              :key="tag"
              :class="['tag-option', { selected: postForm.tags.includes(tag) }]"
              @click="toggleTag(tag)"
            >
              {{ tag }}
            </button>
          </div>
        </div>

        <!-- 敏感词提示 -->
        <div class="warning-alert" v-if="sensitiveWarning">
          <el-icon><Warning /></el-icon>
          <span>{{ sensitiveWarning }}</span>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="showPostDialog = false">取消</el-button>
          <el-button class="submit-btn" @click="submitPost" :loading="posting">
            {{ postForm.id ? '保存修改' : '发布' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Close, MoreFilled, Star, StarFilled, ChatDotRound,
  Share, Pointer, Clock, Edit, Delete, Warning
} from '@element-plus/icons-vue'
import {
  getCommunityPosts,
  saveCommunityPosts,
  getSensitiveWords
} from '../data/appDataStore'

// Props
const props = defineProps({
  isLoggedIn: { type: Boolean, default: false },
  currentUser: { type: String, default: '' }
})

// Emits
const emit = defineEmits(['go-login'])

// 状态
const showPostDialog = ref(false)
const posting = ref(false)
const sortBy = ref('latest')
const searchKeyword = ref('')
const expandedPostId = ref(null)
const sensitiveWarning = ref('')
const newComment = reactive({})

// 筛选标签
const filterTabs = [
  { key: 'latest', label: '最新', icon: '🕐' },
  { key: 'hot', label: '热门', icon: '🔥' },
  { key: 'my', label: '我的', icon: '👤' }
]

// 可用标签
const availableTags = ['学习心得', '求助', '分享', '讨论', '经验交流']

// 表单
const postForm = reactive({
  id: null,
  title: '',
  content: '',
  tags: []
})

const defaultSensitiveWords = [
  '广告', '推销', '代购', '微信', 'QQ群',
  '色情', '暴力', '赌博', '诈骗',
  '政治', '反动', '谣言'
]
const sensitiveWords = ref([])

// 帖子数据
const posts = ref([])

// 统计数据
const totalComments = computed(() => posts.value.reduce((sum, p) => sum + p.comments.length, 0))
const totalLikes = computed(() => posts.value.reduce((sum, p) => sum + p.likes, 0))

// 过滤后的帖子
const filteredPosts = computed(() => {
  let result = [...posts.value]

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(p =>
      p.title.toLowerCase().includes(keyword) ||
      p.content.toLowerCase().includes(keyword)
    )
  }

  if (sortBy.value === 'latest') {
    result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  } else if (sortBy.value === 'hot') {
    result.sort((a, b) => (b.likes + b.comments.length * 2) - (a.likes + a.comments.length * 2))
  } else if (sortBy.value === 'my' && props.currentUser) {
    result = result.filter(p => p.author === props.currentUser)
  }

  return result
})

// 获取标签类型
const getTagType = (tag) => {
  const types = {
    '学习心得': 'green',
    '求助': 'orange',
    '分享': 'blue',
    '讨论': 'purple',
    '经验交流': 'cyan'
  }
  return types[tag] || 'default'
}

// 切换标签选择
const toggleTag = (tag) => {
  const index = postForm.tags.indexOf(tag)
  if (index > -1) {
    postForm.tags.splice(index, 1)
  } else if (postForm.tags.length < 3) {
    postForm.tags.push(tag)
  } else {
    ElMessage.warning('最多选择3个标签')
  }
}

// 敏感词检测
const checkSensitiveWords = (text) => {
  return sensitiveWords.value.filter(word => text.toLowerCase().includes(word.toLowerCase()))
}

// 发布帖子
const submitPost = async () => {
  if (!postForm.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (postForm.title.length < 2) {
    ElMessage.warning('标题至少2个字符')
    return
  }
  if (!postForm.content.trim()) {
    ElMessage.warning('请输入内容')
    return
  }
  if (postForm.content.length < 10) {
    ElMessage.warning('内容至少10个字符')
    return
  }

  const allText = postForm.title + postForm.content
  const foundSensitive = checkSensitiveWords(allText)
  if (foundSensitive.length > 0) {
    sensitiveWarning.value = `内容包含敏感词：${foundSensitive.join(', ')}，请修改后再发布`
    return
  }

  sensitiveWarning.value = ''
  posting.value = true

  setTimeout(() => {
    if (postForm.id) {
      const index = posts.value.findIndex(p => p.id === postForm.id)
      if (index !== -1) {
        posts.value[index].title = postForm.title
        posts.value[index].content = postForm.content
        posts.value[index].tags = [...postForm.tags]
        posts.value[index].edited = true
      }
      ElMessage.success('帖子已更新')
    } else {
      const newPost = {
        id: Date.now(),
        title: postForm.title,
        content: postForm.content,
        tags: [...postForm.tags],
        author: props.currentUser || '匿名用户',
        time: '刚刚',
        createdAt: new Date().toISOString(),
        likes: 0,
        liked: false,
        comments: []
      }
      posts.value.unshift(newPost)
      ElMessage.success('发布成功')
    }

    savePosts()
    showPostDialog.value = false
    resetPostForm()
    posting.value = false
  }, 500)
}

// 重置表单
const resetPostForm = () => {
  postForm.id = null
  postForm.title = ''
  postForm.content = ''
  postForm.tags = []
  sensitiveWarning.value = ''
}

// 编辑帖子
const editPost = (post) => {
  postForm.id = post.id
  postForm.title = post.title
  postForm.content = post.content
  postForm.tags = post.tags ? [...post.tags] : []
  showPostDialog.value = true
}

// 删除帖子
const deletePost = (postId) => {
  ElMessageBox.confirm('确定要删除这篇帖子吗？删除后无法恢复', '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
    confirmButtonClass: 'danger-btn'
  }).then(() => {
    posts.value = posts.value.filter(p => p.id !== postId)
    savePosts()
    ElMessage.success('删除成功')
  }).catch(() => {})
}

// 点赞帖子
const toggleLike = (post) => {
  if (!props.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  post.liked = !post.liked
  post.likes += post.liked ? 1 : -1
  savePosts()
}

// 展开/收起评论
const toggleComments = (postId) => {
  expandedPostId.value = expandedPostId.value === postId ? null : postId
}

// 提交评论
const submitComment = (postId) => {
  const content = newComment[postId]
  if (!content || !content.trim()) return

  const foundSensitive = checkSensitiveWords(content)
  if (foundSensitive.length > 0) {
    ElMessage.error(`评论包含敏感词：${foundSensitive.join(', ')}`)
    return
  }

  const post = posts.value.find(p => p.id === postId)
  if (post) {
    post.comments.push({
      id: Date.now(),
      author: props.currentUser || '匿名用户',
      content: content.trim(),
      time: '刚刚',
      likes: 0
    })
    newComment[postId] = ''
    savePosts()
    ElMessage.success('评论成功')
  }
}

// 点赞评论
const likeComment = (postId, commentId) => {
  if (!props.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    const comment = post.comments.find(c => c.id === commentId)
    if (comment) {
      comment.likes++
      savePosts()
    }
  }
}

// 回复评论
const replyComment = (postId, comment) => {
  newComment[postId] = `@${comment.author} `
}

// 分享帖子
const sharePost = (post) => {
  const text = `【手语学习社区】${post.title} - ${post.content.substring(0, 50)}...`
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      ElMessage.success('已复制到剪贴板')
    })
  } else {
    ElMessage.info('请手动复制分享')
  }
}

// 保存帖子
const savePosts = () => {
  saveCommunityPosts(posts.value)
}

// 加载帖子
const loadPosts = () => {
  const defaults = [
      {
        id: 1,
        title: '分享我的手语学习心得',
        content: '学习手语已经一个月了，从最开始的数字手势到现在能做一些简单的日常交流，感觉进步很大！建议大家每天坚持练习，多看视频教程，配合AI识别练习效果更好。',
        tags: ['学习心得', '经验交流'],
        author: '手语爱好者',
        time: '2小时前',
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        likes: 15,
        liked: false,
        comments: [
          { id: 1, author: '小明', content: '说得太好了，我也在学习中！', time: '1小时前', likes: 3 },
          { id: 2, author: '学习者', content: '请问有什么推荐的学习资源吗？', time: '30分钟前', likes: 1 }
        ]
      },
      {
        id: 2,
        title: '求助：如何区分相似的手势？',
        content: '在学习数字手势的时候，发现6和9、7和8有时候容易混淆，有没有什么好的记忆方法？求大佬指点！',
        tags: ['求助', '讨论'],
        author: '新手小白',
        time: '5小时前',
        createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
        likes: 8,
        liked: false,
        comments: [
          { id: 1, author: '老师', content: '主要看手指的弯曲程度，6是小拇指和拇指，9是食指弯曲', time: '4小时前', likes: 5 }
        ]
      },
      {
        id: 3,
        title: '这个AI识别太准了！',
        content: '刚试了一下这个系统的手势识别功能，识别速度很快，准确率也很高。推荐大家用这个来练习，比对着镜子练习效率高多了！',
        tags: ['分享'],
        author: '科技达人',
        time: '1天前',
        createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        likes: 23,
        liked: false,
        comments: []
      }
  ]

  posts.value = getCommunityPosts(defaults)
}

onMounted(() => {
  sensitiveWords.value = getSensitiveWords(defaultSensitiveWords)
  loadPosts()
})
</script>

<style scoped>
.community {
  --radius-card: 16px;
  --radius-sm: 8px;
  --primary-color: #667eea;
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --glass-bg: rgba(255, 255, 255, 0.8);
  --glass-border: rgba(255, 255, 255, 0.5);
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;

  padding: 24px;
  min-height: 100%;
}

/* 页面头部 */
.community-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
}

.page-desc {
  margin: 0;
  font-size: 15px;
  color: var(--text-secondary);
}

.post-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary-gradient);
  border: none;
  border-radius: var(--radius-card);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.post-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.post-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 18px;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  gap: 32px;
  padding: 16px 24px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

/* 登录提示 */
.login-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: var(--radius-card);
  margin-bottom: 20px;
}

.notice-icon {
  font-size: 24px;
}

.notice-text {
  flex: 1;
  font-size: 14px;
  color: #92400e;
}

.notice-btn {
  background: #fff;
  border: none;
  color: #d97706;
  font-weight: 600;
}

/* 筛选栏 */
.glass-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  margin-bottom: 20px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.08);
  color: var(--primary-color);
}

.filter-tab.active {
  background: var(--primary-gradient);
  color: #fff;
}

.filter-tab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tab-icon {
  font-size: 16px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
}

.search-input {
  width: 220px;
  padding: 10px 36px;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-sm);
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-btn {
  position: absolute;
  right: 8px;
  padding: 4px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

/* 帖子卡片 */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.4s ease forwards;
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

.glass-card:hover {
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
  transform: translateY(-4px);
}

/* 帖子头部 */
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-wrapper {
  position: relative;
}

.author-avatar {
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 600;
}

.online-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  background: #10b981;
  border: 2px solid #fff;
  border-radius: 50%;
}

.author-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.post-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-muted);
}

.more-btn {
  padding: 8px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.more-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
}

/* 帖子内容 */
.post-body {
  margin-bottom: 16px;
}

.post-title {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.post-content {
  margin: 0 0 12px;
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.post-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.tag-green {
  background: #d1fae5;
  color: #059669;
}

.tag-orange {
  background: #fed7aa;
  color: #c2410c;
}

.tag-blue {
  background: #dbeafe;
  color: #1d4ed8;
}

.tag-purple {
  background: #e9d5ff;
  color: #7c3aed;
}

.tag-cyan {
  background: #a5f3fc;
  color: #0891b2;
}

/* 帖子操作栏 */
.post-footer {
  padding-top: 16px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
}

.action-group {
  display: flex;
  gap: 24px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(102, 126, 234, 0.08);
  color: var(--primary-color);
}

.action-btn.active {
  color: #ef4444;
}

.action-btn.active .action-icon {
  animation: heartBeat 0.3s ease;
}

@keyframes heartBeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.action-count {
  font-weight: 600;
}

.action-label {
  color: var(--text-muted);
}

/* 评论区 */
.comments-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
}

.comment-input-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.input-avatar {
  background: var(--primary-gradient);
  color: #fff;
  flex-shrink: 0;
}

.input-box {
  flex: 1;
  display: flex;
  gap: 8px;
}

.comment-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-sm);
  font-size: 14px;
  transition: all 0.3s ease;
}

.comment-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.send-btn {
  padding: 12px 20px;
  background: var(--primary-gradient);
  border: none;
  border-radius: var(--radius-sm);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 评论列表 */
.comment-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(102, 126, 234, 0.05);
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-avatar {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
  font-weight: 600;
  flex-shrink: 0;
}

.comment-body {
  flex: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.comment-author {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.comment-time {
  font-size: 12px;
  color: var(--text-muted);
}

.comment-text {
  margin: 0 0 8px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.comment-actions {
  display: flex;
  gap: 16px;
}

.comment-action {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.comment-action:hover {
  color: var(--primary-color);
}

/* 空评论 */
.empty-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 32px;
}

.empty-text {
  font-size: 14px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon-large {
  font-size: 64px;
}

.empty-state h3 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0;
  font-size: 15px;
  color: var(--text-muted);
}

.create-btn {
  margin-top: 8px;
  background: var(--primary-gradient);
  border: none;
  color: #fff;
}

/* 发帖弹窗 */
.dialog-content {
  padding: 0 8px;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.char-count {
  position: absolute;
  right: 12px;
  bottom: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.tag-select {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-option {
  padding: 8px 16px;
  background: #f3f4f6;
  border: 1px solid transparent;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag-option:hover {
  background: #e5e7eb;
}

.tag-option.selected {
  background: var(--primary-gradient);
  color: #fff;
}

.warning-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef2f2;
  border-radius: var(--radius-sm);
  color: #dc2626;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  padding: 10px 24px;
  background: #f3f4f6;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
}

.submit-btn {
  padding: 10px 24px;
  background: var(--primary-gradient);
  border: none;
  border-radius: var(--radius-sm);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

/* 动画 */
.post-list-enter-active,
.post-list-leave-active {
  transition: all 0.4s ease;
}

.post-list-enter-from,
.post-list-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.post-list-move {
  transition: transform 0.4s ease;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.comment-list-enter-active,
.comment-list-leave-active {
  transition: all 0.3s ease;
}

.comment-list-enter-from,
.comment-list-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 响应式 */
@media (max-width: 768px) {
  .community {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
  }

  .post-btn {
    width: 100%;
    justify-content: center;
  }

  .stats-bar {
    gap: 20px;
    padding: 12px 16px;
  }

  .glass-bar {
    flex-direction: column;
    gap: 12px;
  }

  .filter-tabs {
    width: 100%;
    justify-content: center;
  }

  .search-box {
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .action-group {
    justify-content: space-around;
  }

  .action-label {
    display: none;
  }
}
</style>
