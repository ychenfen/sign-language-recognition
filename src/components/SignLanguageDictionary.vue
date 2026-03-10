<template>
  <div class="sign-language-dictionary">
    <el-card class="dictionary-card">
      <template #header>
        <div class="card-header">
          <h2>📚 手语词典</h2>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索手语词汇..."
            style="width: 300px"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </div>
      </template>

      <!-- 分类导航 -->
      <div class="category-nav">
        <el-tabs v-model="activeCategory" @tab-change="handleCategoryChange">
          <el-tab-pane label="全部" name="all" />
          <el-tab-pane label="数字" name="numbers" />
          <el-tab-pane label="日常用语" name="daily" />
          <el-tab-pane label="情感表达" name="emotions" />
          <el-tab-pane label="称谓" name="titles" />
        </el-tabs>
      </div>

      <!-- 词汇列表 -->
      <div class="vocabulary-grid">
        <div
          v-for="word in filteredVocabulary"
          :key="word.id"
          class="vocabulary-card"
          @click="selectWord(word)"
        >
          <div class="word-icon">{{ word.icon }}</div>
          <div class="word-info">
            <h4>{{ word.word }}</h4>
            <p>{{ word.pinyin }}</p>
            <span class="category-tag">{{ getCategoryName(word.category) }}</span>
          </div>
        </div>
      </div>

      <!-- 详情弹窗 -->
      <el-dialog
        v-model="showDetailDialog"
        :title="selectedWord?.word"
        width="800px"
        center
      >
        <div v-if="selectedWord" class="word-detail">
          <!-- 基本信息 -->
          <div class="basic-info">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="info-item">
                  <label>词汇:</label>
                  <span class="word-text">{{ selectedWord.word }}</span>
                </div>
                <div class="info-item">
                  <label>拼音:</label>
                  <span class="pinyin-text">{{ selectedWord.pinyin }}</span>
                </div>
                <div class="info-item">
                  <label>分类:</label>
                  <el-tag :type="getCategoryTagType(selectedWord.category)">
                    {{ getCategoryName(selectedWord.category) }}
                  </el-tag>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-item">
                  <label>难度:</label>
                  <el-rate
                    v-model="selectedWord.difficulty"
                    :max="5"
                    disabled
                    show-score
                    text-color="#ff9900"
                  />
                </div>
                <div class="info-item">
                  <label>学习次数:</label>
                  <span>{{ selectedWord.learnCount || 0 }} 次</span>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 视频演示 -->
          <div class="video-section">
            <h4>🎥 视频演示</h4>
            <div class="video-container">
              <video
                v-if="selectedWord.videoUrl"
                :src="selectedWord.videoUrl"
                controls
                width="100%"
                height="300"
              >
                您的浏览器不支持视频播放
              </video>
              <div v-else class="no-video">
                <el-icon><VideoCamera /></el-icon>
                <p>暂无视频演示</p>
                <el-button type="primary" size="small">上传视频</el-button>
              </div>
            </div>
          </div>

          <!-- 分解步骤 -->
          <div class="steps-section">
            <h4>📋 分解步骤</h4>
            <div class="steps-container">
              <div
                v-for="(step, index) in selectedWord.steps"
                :key="index"
                class="step-item"
              >
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-content">
                  <div class="step-image">
                    <img
                      v-if="step.imageUrl"
                      :src="step.imageUrl"
                      :alt="step.description"
                      @error="handleImageError"
                    />
                    <div v-else class="no-image">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </div>
                  <div class="step-description">
                    <h5>{{ step.title }}</h5>
                    <p>{{ step.description }}</p>
                    <div class="step-tips" v-if="step.tips">
                      <el-tag size="small" type="warning">
                        💡 {{ step.tips }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 使用说明 -->
          <div class="usage-section" v-if="selectedWord.usage">
            <h4>💬 使用说明</h4>
            <div class="usage-content">
              <div class="usage-example" v-for="example in selectedWord.usage" :key="example.sentence">
                <p class="example-chinese">{{ example.sentence }}</p>
                <p class="example-pinyin">{{ example.pinyin }}</p>
                <p class="example-meaning">{{ example.meaning }}</p>
              </div>
            </div>
          </div>

          <!-- 相关词汇 -->
          <div class="related-section" v-if="selectedWord.relatedWords">
            <h4>🔗 相关词汇</h4>
            <div class="related-words">
              <el-tag
                v-for="word in selectedWord.relatedWords"
                :key="word"
                class="related-word-tag"
                @click="navigateToWord(word)"
              >
                {{ word }}
              </el-tag>
            </div>
          </div>

          <!-- 学习操作 -->
          <div class="action-section">
            <el-row :gutter="15">
              <el-col :span="6">
                <el-button type="primary" block @click="startPractice">
                  <el-icon><VideoPlay /></el-icon>
                  开始练习
                </el-button>
              </el-col>
              <el-col :span="6">
                <el-button type="success" block @click="addToFavorites">
                  <el-icon><Star /></el-icon>
                  收藏
                </el-button>
              </el-col>
              <el-col :span="6">
                <el-button type="warning" block @click="addToLearningPlan">
                  <el-icon><Calendar /></el-icon>
                  加入学习计划
                </el-button>
              </el-col>
              <el-col :span="6">
                <el-button type="info" block @click="shareWord">
                  <el-icon><Share /></el-icon>
                  分享
                </el-button>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script>
import { Search, VideoCamera, Picture, VideoPlay, Star, Calendar, Share } from '@element-plus/icons-vue'

export default {
  name: 'SignLanguageDictionary',
  components: {
    Search,
    VideoCamera,
    Picture,
    VideoPlay,
    Star,
    Calendar,
    Share
  },
  data() {
    return {
      searchKeyword: '',
      activeCategory: 'all',
      showDetailDialog: false,
      selectedWord: null,

      // 手语词汇数据库
      vocabulary: [
        {
          id: 1,
          word: '你好',
          pinyin: 'nǐ hǎo',
          category: 'daily',
          icon: '👋',
          difficulty: 1,
          learnCount: 156,
          videoUrl: '',
          steps: [
            {
              title: '准备姿势',
              description: '手掌自然张开，五指并拢',
              imageUrl: '/Users/yuchenxu/Desktop/手语识别/2d40ac465fa01c693adf3fa5162a8a04.jpg',
              tips: '保持手腕放松'
            },
            {
              title: '挥手动作',
              description: '从身体一侧向另一侧轻轻摆动',
              imageUrl: '',
              tips: '动作幅度适中，不要过大'
            },
            {
              title: '表情配合',
              description: '配合微笑表情，表示友好',
              imageUrl: '',
              tips: '面部表情也是手语的一部分'
            }
          ],
          usage: [
            {
              sentence: '你好，很高兴认识你！',
              pinyin: 'nǐ hǎo, hěn gāoxìng rènshi nǐ!',
              meaning: 'Hello, nice to meet you!'
            }
          ],
          relatedWords: ['再见', '谢谢', '早上好']
        },
        {
          id: 2,
          word: '谢谢',
          pinyin: 'xiè xie',
          category: 'daily',
          icon: '🙏',
          difficulty: 1,
          learnCount: 203,
          videoUrl: '',
          steps: [
            {
              title: '双手准备',
              description: '双手在胸前合十',
              imageUrl: '',
              tips: '双手手掌相对'
            },
            {
              title: '点头动作',
              description: '同时配合点头动作',
              imageUrl: '',
              tips: '表示真诚的感谢'
            }
          ],
          usage: [
            {
              sentence: '谢谢你的帮助！',
              pinyin: 'xiè xie nǐ de bāngzhù!',
              meaning: 'Thank you for your help!'
            }
          ],
          relatedWords: ['不客气', '请', '你好']
        },
        {
          id: 3,
          word: '数字1',
          pinyin: 'shù zì yī',
          category: 'numbers',
          icon: '☝️',
          difficulty: 1,
          learnCount: 89,
          videoUrl: '',
          steps: [
            {
              title: '握拳准备',
              description: '四指轻轻握拳',
              imageUrl: '',
              tips: '拳头不要握得太紧'
            },
            {
              title: '伸出食指',
              description: '食指向上伸直',
              imageUrl: '',
              tips: '食指保持笔直'
            }
          ],
          usage: [
            {
              sentence: '我需要一个人',
              pinyin: 'wǒ xūyào yī gè rén',
              meaning: 'I need one person'
            }
          ],
          relatedWords: ['数字2', '数字3', '数字4', '数字5']
        },
        {
          id: 4,
          word: '数字2',
          pinyin: 'shù zì èr',
          category: 'numbers',
          icon: '✌️',
          difficulty: 1,
          learnCount: 76,
          videoUrl: '',
          steps: [
            {
              title: '握拳准备',
              description: '三指轻轻握拳',
              imageUrl: '',
              tips: '保持手势自然'
            },
            {
              title: '伸出两指',
              description: '食指和中指向上伸直',
              imageUrl: '',
              tips: '两指保持平行'
            }
          ],
          usage: [
            {
              sentence: '给我两个苹果',
              pinyin: 'gěi wǒ liǎng gè píngguǒ',
              meaning: 'Give me two apples'
            }
          ],
          relatedWords: ['数字1', '数字3', '数字4', '数字5']
        },
        {
          id: 5,
          word: '数字3',
          pinyin: 'shù zì sān',
          category: 'numbers',
          icon: '🤟',
          difficulty: 2,
          learnCount: 65,
          videoUrl: '',
          steps: [
            {
              title: '握拳准备',
              description: '两指轻轻握拳',
              imageUrl: '',
              tips: '保持手腕放松'
            },
            {
              title: '伸出三指',
              description: '拇指、食指、中指向上伸直',
              imageUrl: '',
              tips: '三指形成适当角度'
            }
          ],
          usage: [
            {
              sentence: '我们有三个人',
              pinyin: 'wǒmen yǒu sān gè rén',
              meaning: 'We have three people'
            }
          ],
          relatedWords: ['数字1', '数字2', '数字4', '数字5']
        },
        {
          id: 6,
          word: '再见',
          pinyin: 'zài jiàn',
          category: 'daily',
          icon: '👋',
          difficulty: 1,
          learnCount: 167,
          videoUrl: '',
          steps: [
            {
              title: '挥手告别',
              description: '手掌向左右摆动',
              imageUrl: '',
              tips: '动作要明显'
            }
          ],
          usage: [
            {
              sentence: '再见，明天见！',
              pinyin: 'zàijiàn, míngtiān jiàn!',
              meaning: 'Goodbye, see you tomorrow!'
            }
          ],
          relatedWords: ['你好', '晚安', '明天见']
        },
        {
          id: 7,
          word: '我爱你',
          pinyin: 'wǒ ài nǐ',
          category: 'emotions',
          icon: '🤟',
          difficulty: 2,
          learnCount: 234,
          videoUrl: '',
          steps: [
            {
              title: '伸出三指',
              description: '拇指、食指、小指伸直',
              imageUrl: '',
              tips: '中指和无名指弯曲'
            }
          ],
          usage: [
            {
              sentence: '我爱你，妈妈！',
              pinyin: 'wǒ ài nǐ, māmā!',
              meaning: 'I love you, mom!'
            }
          ],
          relatedWords: ['喜欢', '关心', '家人']
        },
        {
          id: 8,
          word: '打不开',
          pinyin: 'dǎ bù kāi',
          category: 'daily',
          icon: '🔒',
          difficulty: 2,
          learnCount: 45,
          videoUrl: '',
          steps: [
            {
              title: '握拳准备',
              description: '一只手握成拳头',
              imageUrl: '',
              tips: '拳头要紧握，表示牢固'
            },
            {
              title: '另一只手尝试打开',
              description: '另一只手尝试掰开拳头',
              imageUrl: '',
              tips: '动作要明显，表示用力尝试'
            },
            {
              title: '摇头动作',
              description: '配合摇头表示无法打开',
              imageUrl: '',
              tips: '表情要配合，表示无能为力'
            }
          ],
          usage: [
            {
              sentence: '这个瓶子打不开，你能帮我一下吗？',
              pinyin: 'zhège píngzi dǎ bù kāi, nǐ néng bāng wǒ yīxià ma?',
              meaning: 'I can\'t open this bottle, can you help me?'
            },
            {
              sentence: '门打不开，可能锁了。',
              pinyin: 'mén dǎ bù kāi, kěnéng suǒ le.',
              meaning: 'The door won\'t open, it might be locked.'
            }
          ],
          relatedWords: ['打开', '关上', '锁住', '帮助']
        }
      ]
    }
  },

  computed: {
    filteredVocabulary() {
      let result = this.vocabulary

      // 按分类筛选
      if (this.activeCategory !== 'all') {
        result = result.filter(word => word.category === this.activeCategory)
      }

      // 按关键词搜索
      if (this.searchKeyword) {
        const keyword = this.searchKeyword.toLowerCase()
        result = result.filter(word =>
          word.word.toLowerCase().includes(keyword) ||
          word.pinyin.toLowerCase().includes(keyword)
        )
      }

      return result
    }
  },

  methods: {
    handleSearch() {
      // 搜索功能已在计算属性中实现
    },

    handleCategoryChange(category) {
      this.activeCategory = category
    },

    selectWord(word) {
      this.selectedWord = word
      this.showDetailDialog = true

      // 增加学习次数
      word.learnCount = (word.learnCount || 0) + 1
    },

    getCategoryName(category) {
      const categoryMap = {
        numbers: '数字',
        daily: '日常用语',
        emotions: '情感表达',
        titles: '称谓'
      }
      return categoryMap[category] || '其他'
    },

    getCategoryTagType(category) {
      const typeMap = {
        numbers: 'primary',
        daily: 'success',
        emotions: 'warning',
        titles: 'info'
      }
      return typeMap[category] || 'default'
    },

    handleImageError(event) {
      event.target.style.display = 'none'
    },

    startPractice() {
      this.$message.success('开始练习功能开发中...')
      // 这里可以跳转到练习页面
    },

    addToFavorites() {
      this.$message.success('已添加到收藏夹')
      // 这里可以调用API添加到收藏
    },

    addToLearningPlan() {
      this.$message.success('已加入学习计划')
      // 这里可以调用API添加到学习计划
    },

    shareWord() {
      this.$message.success('分享链接已复制')
      // 这里可以实现分享功能
    },

    navigateToWord(wordName) {
      const word = this.vocabulary.find(w => w.word === wordName)
      if (word) {
        this.selectWord(word)
      }
    }
  }
}
</script>

<style scoped>
.sign-language-dictionary {
  height: 100%;
}

.dictionary-card {
  height: 100%;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #409EFF;
  font-size: 1.5em;
}

.category-nav {
  margin: 20px 0;
}

.vocabulary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px 0;
}

.vocabulary-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.vocabulary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.word-icon {
  font-size: 2em;
}

.word-info h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.word-info p {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 0.9em;
  font-style: italic;
}

.category-tag {
  font-size: 0.8em;
}

.word-detail {
  max-height: 600px;
  overflow-y: auto;
}

.basic-info {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.info-item label {
  width: 80px;
  font-weight: bold;
  color: #606266;
}

.word-text {
  font-size: 1.2em;
  font-weight: bold;
  color: #409EFF;
}

.pinyin-text {
  font-style: italic;
  color: #909399;
}

.video-section,
.steps-section,
.usage-section,
.related-section,
.action-section {
  margin-bottom: 25px;
}

.video-section h4,
.steps-section h4,
.usage-section h4,
.related-section h4 {
  margin-bottom: 15px;
  color: #409EFF;
  display: flex;
  align-items: center;
  gap: 8px;
}

.video-container {
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

.no-video {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}

.no-video .el-icon {
  font-size: 3em;
  margin-bottom: 10px;
}

.steps-container {
  space-y: 15px;
}

.step-item {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.step-number {
  width: 30px;
  height: 30px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content {
  display: flex;
  gap: 15px;
  flex: 1;
}

.step-image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.step-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.no-image {
  width: 100%;
  height: 100%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  border-radius: 8px;
}

.step-description {
  flex: 1;
}

.step-description h5 {
  margin: 0 0 8px 0;
  color: #303133;
}

.step-description p {
  margin: 0 0 10px 0;
  color: #606266;
  line-height: 1.5;
}

.step-tips {
  margin-top: 8px;
}

.usage-example {
  margin-bottom: 15px;
  padding: 15px;
  background: #fff;
  border-left: 4px solid #409EFF;
  border-radius: 4px;
}

.example-chinese {
  margin: 0 0 5px 0;
  font-weight: bold;
  color: #303133;
}

.example-pinyin {
  margin: 0 0 5px 0;
  color: #909399;
  font-style: italic;
}

.example-meaning {
  margin: 0;
  color: #606266;
}

.related-words {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.related-word-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.related-word-tag:hover {
  transform: translateY(-1px);
}
</style>