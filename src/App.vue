<template>
  <div id="app" :class="{ 'nav-scrolled': isScrolled }">
    <el-container>
      <!-- 顶部导航 - 白色毛玻璃+渐变文字 -->
      <header class="app-header" :class="{ scrolled: isScrolled }">
        <div class="header-content">
          <div class="header-left">
            <div class="logo-group" @click="activeTab = 'dictionary'">
              <span class="logo-icon">🤟</span>
              <h1 class="logo">手语学习平台</h1>
            </div>
            <span class="slogan">学习中国通用手语，连接无声世界</span>
          </div>
          <div class="header-right">
            <template v-if="isLoggedIn">
              <el-dropdown trigger="click" placement="bottom-end">
                <div class="user-info">
                  <el-avatar :size="32" class="user-avatar">
                    {{ username.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <span class="username">{{ username }}</span>
                  <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu class="user-dropdown">
                    <el-dropdown-item @click="activeTab = 'user'">
                      <el-icon><User /></el-icon>
                      个人中心
                    </el-dropdown-item>
                    <el-dropdown-item divided @click="handleLogout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <button v-else class="login-btn" @click="activeTab = 'user'">
              登录 / 注册
            </button>
          </div>
        </div>
      </header>

      <!-- 主导航 - 简洁线条风格 -->
      <nav class="main-nav" :class="{ scrolled: isScrolled }">
        <div class="nav-content">
          <div class="nav-items">
            <button
              v-for="item in navItems"
              :key="item.key"
              :class="['nav-item', { active: activeTab === item.key }]"
              @click="handleMenuSelect(item.key)"
              v-show="!item.adminOnly || isAdmin"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-text">{{ item.label }}</span>
              <span class="nav-dot"></span>
            </button>
          </div>
        </div>
      </nav>

      <!-- 主内容区 -->
      <el-main class="app-main">
        <div class="content-wrapper">
          <Transition name="fade-slide" mode="out-in">
            <component
              :is="currentComponent"
              v-bind="currentProps"
              v-on="currentListeners"
              :key="activeTab"
            />
          </Transition>
        </div>
      </el-main>

      <!-- 底部 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <div class="footer-brand">
            <span class="footer-logo">🤟</span>
            <span>手语学习平台 v2.0</span>
          </div>
          <div class="footer-links">
            <a href="#">关于我们</a>
            <a href="#">使用帮助</a>
            <a href="#">联系方式</a>
          </div>
          <p class="footer-copyright">致力于推广中国通用手语 | 让沟通无障碍</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown, User, SwitchButton } from '@element-plus/icons-vue'
import SignDictionary from './components/SignDictionary.vue'
import SignLearning from './components/SignLearning.vue'
import SignTest from './components/SignTest.vue'
import Community from './components/Community.vue'
import AIChat from './components/AIChat.vue'
import UserCenter from './components/UserCenter.vue'
import AdminPanel from './components/AdminPanel.vue'

const activeTab = ref('dictionary')
const isLoggedIn = ref(false)
const isAdmin = ref(false)
const username = ref('')
const isScrolled = ref(false)

// 导航菜单配置
const navItems = [
  { key: 'dictionary', label: '手语词典', icon: '📖' },
  { key: 'learn', label: '手语学习', icon: '📚' },
  { key: 'test', label: '手语测试', icon: '✍️' },
  { key: 'community', label: '交流社区', icon: '💬' },
  { key: 'ai', label: 'AI助手', icon: '🤖' },
  { key: 'user', label: '个人中心', icon: '👤' },
  { key: 'admin', label: '后台管理', icon: '⚙️', adminOnly: true }
]

// 组件映射
const componentMap = {
  dictionary: markRaw(SignDictionary),
  learn: markRaw(SignLearning),
  test: markRaw(SignTest),
  community: markRaw(Community),
  ai: markRaw(AIChat),
  user: markRaw(UserCenter),
  admin: markRaw(AdminPanel)
}

// 当前组件
const currentComponent = computed(() => componentMap[activeTab.value])

// 组件属性
const currentProps = computed(() => {
  if (activeTab.value === 'community') {
    return { isLoggedIn: isLoggedIn.value, currentUser: username.value }
  }
  return {}
})

const currentListeners = computed(() => {
  if (activeTab.value === 'user') {
    return {
      'login-success': handleLoginSuccess,
      logout: handleUserLogout,
      'go-to': handleGoTo
    }
  }
  if (activeTab.value === 'community') {
    return {
      'go-login': handleGoLogin
    }
  }
  return {}
})

// 滚动监听
const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

const handleMenuSelect = (index) => {
  if (index === 'admin' && !isAdmin.value) {
    ElMessage.warning('仅管理员可访问后台管理')
    activeTab.value = 'user'
    return
  }
  activeTab.value = index
  // 切换页面时滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const clearAuthState = () => {
  isLoggedIn.value = false
  username.value = ''
  isAdmin.value = false
  localStorage.removeItem('currentUser')
}

const handleLogout = () => {
  clearAuthState()
  activeTab.value = 'dictionary'
}

const handleLoginSuccess = (user) => {
  if (!user) return
  isLoggedIn.value = true
  username.value = user.username || ''
  isAdmin.value = user.role === 'admin'
  activeTab.value = 'user'
}

const handleUserLogout = () => {
  clearAuthState()
  activeTab.value = 'dictionary'
}

const handleGoTo = (tab) => {
  if (!tab) return
  handleMenuSelect(tab)
}

const handleGoLogin = () => {
  activeTab.value = 'user'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  // 检查登录状态
  const savedUser = localStorage.getItem('currentUser')
  if (savedUser) {
    try {
      const user = JSON.parse(savedUser)
      isLoggedIn.value = true
      username.value = user.username || ''
      isAdmin.value = user.role === 'admin'
    } catch (error) {
      clearAuthState()
    }
  }

  // 添加滚动监听
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style>
/* 全局 CSS 变量 - 降低饱和度，更自然 */
:root {
  --primary-color: #6366f1;
  --primary-light: #818cf8;
  --primary-dark: #4f46e5;
  --accent-color: #8b5cf6;

  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;

  --glass-bg: rgba(255, 255, 255, 0.8);
  --glass-bg-dark: rgba(255, 255, 255, 0.6);
  --glass-border: rgba(255, 255, 255, 0.4);

  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  --header-height: 64px;
  --nav-height: 52px;
  --footer-height: 80px;

  --font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;

  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;

  --bg-base: #f8fafc;
  --bg-subtle: #f1f5f9;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  background: var(--bg-base);
  min-height: 100vh;
  color: var(--text-primary);
}

#app {
  min-height: 100vh;
}

.el-container {
  min-height: 100vh;
  flex-direction: column;
}

/* 顶部导航 - 白色毛玻璃 */
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.app-header.scrolled {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo-group:hover {
  opacity: 0.8;
}

.logo-icon {
  font-size: 28px;
  animation: gentle-wave 3s ease-in-out infinite;
}

@keyframes gentle-wave {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

.logo {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.slogan {
  color: var(--text-muted);
  font-size: 13px;
  padding-left: 20px;
  border-left: 1px solid #e2e8f0;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px 6px 6px;
  border-radius: var(--radius-full);
  transition: background 0.2s;
}

.user-info:hover {
  background: var(--bg-subtle);
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
}

.username {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
}

.dropdown-icon {
  color: var(--text-muted);
  font-size: 12px;
  transition: transform 0.2s;
}

.user-info:hover .dropdown-icon {
  transform: rotate(180deg);
}

.login-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
  border: none;
  color: #fff;
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* 主导航 - 简洁风格 */
.main-nav {
  position: fixed;
  top: var(--header-height);
  left: 0;
  right: 0;
  z-index: 999;
  height: var(--nav-height);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.main-nav.scrolled {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 32px;
}

.nav-items {
  display: flex;
  gap: 4px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-subtle);
}

.nav-item.active {
  color: var(--primary-color);
  font-weight: 500;
}

.nav-icon {
  font-size: 16px;
  transition: transform 0.2s;
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-text {
  white-space: nowrap;
}

/* 小圆点指示器 */
.nav-dot {
  position: absolute;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--primary-color);
  opacity: 0;
  transition: opacity 0.2s;
}

.nav-item.active .nav-dot {
  opacity: 1;
}

/* 为固定导航留出空间 */
.nav-scrolled .el-main {
  padding-top: calc(var(--header-height) + var(--nav-height) + 24px);
}

/* 主内容 */
.app-main {
  flex: 1;
  padding: 24px;
  padding-top: calc(var(--header-height) + var(--nav-height) + 24px);
  background: transparent;
  min-height: calc(100vh - var(--footer-height));
}

.content-wrapper {
  max-width: 1400px;
  width: 100%;
  min-width: 0;
  margin: 0 auto;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.04);
  border-radius: var(--radius-lg);
  min-height: calc(100vh - var(--header-height) - var(--nav-height) - var(--footer-height) - 48px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  overflow: visible;
}

/* 页面切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* 底部 */
.app-footer {
  background: #fff;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  padding: 24px 32px;
  height: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.footer-logo {
  font-size: 20px;
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--primary-color);
}

.footer-copyright {
  color: var(--text-muted);
  font-size: 12px;
}

/* 用户下拉菜单样式 */
.user-dropdown {
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.user-dropdown .el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .nav-items {
    gap: 2px;
  }

  .nav-item {
    padding: 8px 12px;
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  :root {
    --header-height: 56px;
    --nav-height: 48px;
  }

  .header-content {
    padding: 0 16px;
  }

  .logo {
    font-size: 18px;
  }

  .logo-icon {
    font-size: 24px;
  }

  .slogan {
    display: none;
  }

  .nav-content {
    padding: 0 12px;
    overflow-x: auto;
    justify-content: flex-start;
  }

  .nav-items {
    gap: 0;
    flex-wrap: nowrap;
  }

  .nav-item {
    padding: 8px 10px;
    flex-shrink: 0;
  }

  .nav-text {
    display: none;
  }

  .nav-icon {
    font-size: 18px;
  }

  .app-main {
    padding: 12px;
    padding-top: calc(var(--header-height) + var(--nav-height) + 12px);
  }

  .content-wrapper {
    border-radius: var(--radius-md);
  }
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 选中文字样式 */
::selection {
  background: rgba(99, 102, 241, 0.2);
  color: var(--text-primary);
}
</style>
