import { learningCourses, signVocabulary } from './signResources'

const STORAGE_KEYS = {
  users: 'users',
  words: 'adminWords',
  courses: 'adminCourses',
  posts: 'community_posts',
  sensitiveWords: 'sensitiveWords',
  favorites: 'favorites'
}

const LEGACY_KEYS = {
  posts: 'communityPosts',
  favorites: 'signFavorites'
}

const DEFAULT_SENSITIVE_WORDS = [
  '广告', '推销', '代购', '微信', 'QQ群',
  '色情', '暴力', '赌博', '诈骗',
  '政治', '反动', '谣言'
]

const DEFAULT_ADMIN_USER = {
  id: 1,
  username: 'admin',
  password: 'admin123',
  role: 'admin',
  status: 'active',
  registerTime: '2026-02-22'
}

const safeParse = (value, fallback = null) => {
  if (!value) return fallback
  try {
    return JSON.parse(value)
  } catch (error) {
    console.warn('Failed to parse localStorage JSON:', error)
    return fallback
  }
}

const readJSON = (key, fallback = null) => safeParse(localStorage.getItem(key), fallback)
const writeJSON = (key, value) => localStorage.setItem(key, JSON.stringify(value))

const normalizeWord = (word, index = 0) => {
  const normalizedWord = word?.word || word?.name || `未命名词汇${index + 1}`
  return {
    id: word?.id ?? Date.now() + index,
    word: normalizedWord,
    name: word?.name || normalizedWord,
    pinyin: word?.pinyin || '',
    category: word?.category || '未分类',
    description: word?.description || '暂无描述',
    image: word?.image || '',
    video: word?.video || '',
    steps: Array.isArray(word?.steps) && word.steps.length > 0 ? word.steps : ['暂无动作分解'],
    examples: Array.isArray(word?.examples) ? word.examples : []
  }
}

const normalizeLesson = (lesson, index = 0) => ({
  id: lesson?.id ?? Date.now() + index,
  title: lesson?.title || `课时 ${index + 1}`,
  description: lesson?.description || '暂无课程描述',
  video: lesson?.video || '',
  duration: lesson?.duration || '约10分钟'
})

const normalizeCourse = (course, index = 0) => ({
  id: course?.id ?? Date.now() + index,
  title: course?.title || `课程 ${index + 1}`,
  description: course?.description || '暂无课程描述',
  icon: course?.icon || '📚',
  category: course?.category || '未分类',
  lessons: Array.isArray(course?.lessons) ? course.lessons.map((lesson, lessonIndex) => normalizeLesson(lesson, lessonIndex)) : []
})

const normalizeComment = (comment, index = 0) => ({
  id: comment?.id ?? Date.now() + index,
  author: comment?.author || '匿名用户',
  content: comment?.content || '',
  time: comment?.time || '刚刚',
  likes: Number(comment?.likes || 0)
})

const normalizePost = (post, index = 0) => ({
  id: post?.id ?? Date.now() + index,
  title: post?.title || '未命名帖子',
  content: post?.content || '',
  tags: Array.isArray(post?.tags) ? post.tags : [],
  author: post?.author || '匿名用户',
  time: post?.time || '刚刚',
  createdAt: post?.createdAt || new Date().toISOString(),
  likes: Number(post?.likes || 0),
  liked: Boolean(post?.liked),
  comments: Array.isArray(post?.comments) ? post.comments.map((comment, commentIndex) => normalizeComment(comment, commentIndex)) : []
})

const normalizeFavorite = (item, index = 0) => {
  const normalizedWord = item?.word || item?.name || item?.title || `词汇${index + 1}`
  return {
    id: item?.id ?? Date.now() + index,
    word: normalizedWord,
    name: item?.name || normalizedWord,
    pinyin: item?.pinyin || '',
    category: item?.category || '未分类',
    time: item?.time || new Date().toLocaleString()
  }
}

export const getUsers = () => {
  const users = readJSON(STORAGE_KEYS.users, null)
  if (Array.isArray(users) && users.length > 0) {
    const normalizedUsers = users.map((user, index) => ({
      ...user,
      id: user?.id ?? Date.now() + index,
      role: user?.role || 'user',
      status: user?.status || 'active'
    }))
    if (!normalizedUsers.some(user => user.role === 'admin')) {
      normalizedUsers.unshift(DEFAULT_ADMIN_USER)
      writeJSON(STORAGE_KEYS.users, normalizedUsers)
    }
    return normalizedUsers
  }
  writeJSON(STORAGE_KEYS.users, [DEFAULT_ADMIN_USER])
  return [DEFAULT_ADMIN_USER]
}

export const saveUsers = (users = []) => {
  if (!Array.isArray(users)) return
  writeJSON(
    STORAGE_KEYS.users,
    users.map((user, index) => ({
      ...user,
      id: user?.id ?? Date.now() + index,
      role: user?.role || 'user',
      status: user?.status || 'active'
    }))
  )
}

export const getWords = () => {
  const words = readJSON(STORAGE_KEYS.words, null)
  if (Array.isArray(words) && words.length > 0) {
    return words.map((word, index) => normalizeWord(word, index))
  }
  const defaults = signVocabulary.map((word, index) => normalizeWord(word, index))
  writeJSON(STORAGE_KEYS.words, defaults)
  return defaults
}

export const saveWords = (words = []) => {
  if (!Array.isArray(words)) return
  writeJSON(STORAGE_KEYS.words, words.map((word, index) => normalizeWord(word, index)))
}

export const getCourses = () => {
  const courses = readJSON(STORAGE_KEYS.courses, null)
  if (Array.isArray(courses) && courses.length > 0) {
    return courses.map((course, index) => normalizeCourse(course, index))
  }
  const defaults = learningCourses.map((course, index) => normalizeCourse(course, index))
  writeJSON(STORAGE_KEYS.courses, defaults)
  return defaults
}

export const saveCourses = (courses = []) => {
  if (!Array.isArray(courses)) return
  writeJSON(STORAGE_KEYS.courses, courses.map((course, index) => normalizeCourse(course, index)))
}

export const getCommunityPosts = (fallbackPosts = []) => {
  const storedPosts = readJSON(STORAGE_KEYS.posts, null)
  const legacyPosts = readJSON(LEGACY_KEYS.posts, null)
  const sourcePosts = Array.isArray(storedPosts)
    ? storedPosts
    : (Array.isArray(legacyPosts) ? legacyPosts : fallbackPosts)

  if (!Array.isArray(sourcePosts) || sourcePosts.length === 0) {
    return []
  }

  const normalized = sourcePosts.map((post, index) => normalizePost(post, index))
  writeJSON(STORAGE_KEYS.posts, normalized)
  writeJSON(LEGACY_KEYS.posts, normalized)
  return normalized
}

export const saveCommunityPosts = (posts = []) => {
  if (!Array.isArray(posts)) return
  const normalized = posts.map((post, index) => normalizePost(post, index))
  writeJSON(STORAGE_KEYS.posts, normalized)
  writeJSON(LEGACY_KEYS.posts, normalized)
}

export const getSensitiveWords = (fallback = DEFAULT_SENSITIVE_WORDS) => {
  const words = readJSON(STORAGE_KEYS.sensitiveWords, null)
  if (Array.isArray(words) && words.length > 0) {
    return words
  }

  const normalizedFallback = Array.isArray(fallback)
    ? [...new Set(fallback.map(item => String(item).trim()).filter(Boolean))]
    : DEFAULT_SENSITIVE_WORDS

  writeJSON(STORAGE_KEYS.sensitiveWords, normalizedFallback)
  return normalizedFallback
}

export const saveSensitiveWords = (words = []) => {
  if (!Array.isArray(words)) return
  const normalized = [...new Set(words.map(item => String(item).trim()).filter(Boolean))]
  writeJSON(STORAGE_KEYS.sensitiveWords, normalized)
}

export const getFavorites = () => {
  const storedFavorites = readJSON(STORAGE_KEYS.favorites, null)
  const legacyFavorites = readJSON(LEGACY_KEYS.favorites, null)
  const sourceFavorites = Array.isArray(storedFavorites)
    ? storedFavorites
    : (Array.isArray(legacyFavorites) ? legacyFavorites : [])

  const normalized = sourceFavorites.map((favorite, index) => normalizeFavorite(favorite, index))
  writeJSON(STORAGE_KEYS.favorites, normalized)
  writeJSON(LEGACY_KEYS.favorites, normalized)
  return normalized
}

export const saveFavorites = (favorites = []) => {
  if (!Array.isArray(favorites)) return
  const normalized = favorites.map((favorite, index) => normalizeFavorite(favorite, index))
  writeJSON(STORAGE_KEYS.favorites, normalized)
  writeJSON(LEGACY_KEYS.favorites, normalized)
}
