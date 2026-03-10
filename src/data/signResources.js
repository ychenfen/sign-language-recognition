/**
 * 手语资源配置文件
 * 包含词汇的视频、图片资源链接
 *
 * 数据来源: 用户提供的手语学习资源
 * 更新日期: 2025-01-17
 */

// 手语词汇数据（带视频资源）
export const signVocabulary = [
  // ========== 基础词汇 ==========
  {
    id: 1,
    word: '爱',
    pinyin: 'ài',
    category: '基础词汇',
    description: '表达爱意',
    video: '/videos/signs/ai.mp4',
    image: '/images/signs/ai.png',
    steps: [
      '双手交叉放在心口',
      '轻轻抱住自己',
      '表情温柔'
    ],
    examples: ['我爱你', '爱学习']
  },
  {
    id: 2,
    word: '谢谢',
    pinyin: 'xiè xie',
    category: '基础词汇',
    description: '表示感谢',
    video: '/videos/signs/xiexie.mp4',
    image: '/images/signs/xiexie.png',
    steps: [
      '右手伸出，手心向下',
      '从胸前向外平推',
      '同时微微点头'
    ],
    examples: ['收到帮助后说"谢谢"', '表达感激之情']
  },
  {
    id: 3,
    word: '对不起',
    pinyin: 'duì bu qǐ',
    category: '基础词汇',
    description: '道歉用语',
    video: '/videos/signs/duibuqi.mp4',
    image: '/images/signs/duibuqi.png',
    steps: [
      '右手握拳',
      '轻轻敲击左胸口',
      '表情带有歉意'
    ],
    examples: ['做错事时道歉', '表示抱歉']
  },
  {
    id: 4,
    word: '没关系',
    pinyin: 'méi guān xi',
    category: '基础词汇',
    description: '表示没关系、不要紧',
    video: '/videos/signs/meiguanxi.mp4',
    image: '/images/signs/meiguanxi.jpg',
    steps: [
      '双手在胸前交叉摆动',
      '表示"没事"的意思',
      '面带微笑'
    ],
    examples: ['别人道歉时回应', '表示不介意']
  },
  {
    id: 5,
    word: '我们',
    pinyin: 'wǒ men',
    category: '基础词汇',
    description: '第一人称复数',
    video: '/videos/signs/women.mp4',
    image: '/images/signs/women.jpg',
    steps: [
      '右手食指指向自己',
      '然后画一个小圈包含周围的人'
    ],
    examples: ['我们一起', '我们是朋友']
  },
  {
    id: 6,
    word: '帮助',
    pinyin: 'bāng zhù',
    category: '基础词汇',
    description: '帮助他人',
    video: '/videos/signs/bangzhu.mp4',
    image: '/images/signs/bangzhu.png',
    steps: [
      '左手握拳',
      '右手托住左手',
      '向上抬起'
    ],
    examples: ['帮助别人', '请帮助我']
  },

  // ========== 情绪表达 ==========
  {
    id: 7,
    word: '高兴',
    pinyin: 'gāo xìng',
    category: '情绪表达',
    description: '表达开心',
    video: '/videos/signs/gaoxing.mp4',
    image: '/images/signs/gaoxing.png',
    steps: [
      '双手在胸前',
      '手心向上，向上抬起',
      '面带笑容'
    ],
    examples: ['我很高兴', '见到你很高兴']
  },
  {
    id: 8,
    word: '难受',
    pinyin: 'nán shòu',
    category: '情绪表达',
    description: '表达不舒服、难过',
    video: '/videos/signs/nanshou.mp4',
    image: '/images/signs/nanshou.png',
    steps: [
      '右手放在胸口',
      '做揉搓动作',
      '表情痛苦'
    ],
    examples: ['身体难受', '心里难受']
  },
  {
    id: 9,
    word: '笑',
    pinyin: 'xiào',
    category: '情绪表达',
    description: '表达笑、开心',
    video: '/videos/signs/xiao.mp4',
    image: '/images/signs/xiao.png',
    steps: [
      '双手放在嘴角两侧',
      '向上提起',
      '做出微笑的表情'
    ],
    examples: ['笑一笑', '开心地笑']
  },
  {
    id: 10,
    word: '哭',
    pinyin: 'kū',
    category: '情绪表达',
    description: '表达哭泣',
    video: '/videos/signs/ku.mp4',
    image: '/images/signs/ku.png',
    steps: [
      '双手食指从眼角向下划',
      '模仿眼泪流下',
      '表情悲伤'
    ],
    examples: ['哭了', '别哭']
  },
  {
    id: 11,
    word: '生气',
    pinyin: 'shēng qì',
    category: '情绪表达',
    description: '表达愤怒',
    video: '/videos/signs/shengqi.mp4',
    image: '/images/signs/shengqi.png',
    steps: [
      '双手握拳',
      '放在胸前抖动',
      '表情愤怒'
    ],
    examples: ['我生气了', '别生气']
  },

  // ========== 家庭称谓 ==========
  {
    id: 12,
    word: '爸爸',
    pinyin: 'bà ba',
    category: '家庭称谓',
    description: '父亲',
    video: '/videos/signs/baba.mp4',
    image: '/images/signs/baba.png',
    steps: [
      '右手握拳',
      '拇指竖起',
      '在额头前方'
    ],
    examples: ['我爸爸', '爸爸好']
  },
  {
    id: 13,
    word: '妈妈',
    pinyin: 'mā ma',
    category: '家庭称谓',
    description: '母亲',
    video: '/videos/signs/mama.mp4',
    image: '/images/signs/mama.png',
    steps: [
      '右手五指张开',
      '手心贴在脸颊上',
      '轻轻拍两下'
    ],
    examples: ['我妈妈', '妈妈好']
  },
  {
    id: 14,
    word: '爷爷',
    pinyin: 'yé ye',
    category: '家庭称谓',
    description: '祖父（父亲的父亲）',
    video: '/videos/signs/yeye.mp4',
    image: '/images/signs/yeye.png',
    steps: [
      '先做"爸爸"的手势',
      '然后再做一次',
      '表示"爸爸的爸爸"'
    ],
    examples: ['我爷爷', '爷爷好']
  },
  {
    id: 15,
    word: '奶奶',
    pinyin: 'nǎi nai',
    category: '家庭称谓',
    description: '祖母（父亲的母亲）',
    video: '/videos/signs/nainai.mp4',
    image: '/images/signs/nainai.png',
    steps: [
      '先做"妈妈"的手势',
      '然后再做"爸爸"的手势',
      '表示"爸爸的妈妈"'
    ],
    examples: ['我奶奶', '奶奶好']
  },
  {
    id: 16,
    word: '姥姥',
    pinyin: 'lǎo lao',
    category: '家庭称谓',
    description: '外祖母（母亲的母亲）',
    video: '/videos/signs/laolao.mp4',
    image: '/images/signs/laolao.png',
    steps: [
      '先做"妈妈"的手势',
      '然后再做一次',
      '表示"妈妈的妈妈"'
    ],
    examples: ['我姥姥', '姥姥好']
  },
  {
    id: 17,
    word: '姥爷',
    pinyin: 'lǎo ye',
    category: '家庭称谓',
    description: '外祖父（母亲的父亲）',
    video: '/videos/signs/laoye.mp4',
    image: '/images/signs/laoye.jpg',
    steps: [
      '先做"妈妈"的手势',
      '然后做"爸爸"的手势',
      '表示"妈妈的爸爸"'
    ],
    examples: ['我姥爷', '姥爷好']
  },

  // ========== 姓氏 ==========
  {
    id: 18,
    word: '王',
    pinyin: 'wáng',
    category: '姓氏',
    description: '姓氏"王"',
    video: '/videos/signs/wang.mp4',
    image: '/images/signs/wang.png',
    steps: [
      '右手做"王"字的手势',
      '三横一竖的形状'
    ],
    examples: ['我姓王', '王先生']
  },
  {
    id: 19,
    word: '李',
    pinyin: 'lǐ',
    category: '姓氏',
    description: '姓氏"李"',
    video: '/videos/signs/li.mp4',
    image: '/images/signs/li.png',
    steps: [
      '右手做"李"字的手势',
      '木字加子的形状'
    ],
    examples: ['我姓李', '李老师']
  },
  {
    id: 20,
    word: '陈',
    pinyin: 'chén',
    category: '姓氏',
    description: '姓氏"陈"',
    video: '/videos/signs/chen.mp4',
    image: '/images/signs/chen.png',
    steps: [
      '右手做"陈"字的手势'
    ],
    examples: ['我姓陈', '陈同学']
  },
  {
    id: 21,
    word: '赵',
    pinyin: 'zhào',
    category: '姓氏',
    description: '姓氏"赵"',
    video: '/videos/signs/zhao.mp4',
    image: '/images/signs/zhao.png',
    steps: [
      '右手做"赵"字的手势'
    ],
    examples: ['我姓赵', '赵医生']
  },
  {
    id: 22,
    word: '杨',
    pinyin: 'yáng',
    category: '姓氏',
    description: '姓氏"杨"',
    video: '/videos/signs/yang.mp4',
    image: '/images/signs/yang.png',
    steps: [
      '右手做"杨"字的手势'
    ],
    examples: ['我姓杨', '杨阿姨']
  },
  {
    id: 23,
    word: '刘',
    pinyin: 'liú',
    category: '姓氏',
    description: '姓氏"刘"',
    video: '/videos/signs/liu.mp4',
    image: '/images/signs/liu.png',
    steps: [
      '右手做"刘"字的手势'
    ],
    examples: ['我姓刘', '刘叔叔']
  }
]

// 学习课程数据
export const learningCourses = [
  {
    id: 1,
    title: '认识手语',
    description: '了解聋人文化和手语基础知识',
    icon: '📚',
    lessons: [
      {
        id: 101,
        title: '认识聋人和手语',
        description: '了解聋人群体和手语的基本概念',
        video: '/videos/lessons/01-认识手语/renshi-longren.mp4',
        duration: '约18分钟'
      },
      {
        id: 102,
        title: '手语与有声语言的区别',
        description: '学习手语与有声语言的主要差异',
        video: '/videos/lessons/01-认识手语/shouyu-qubie.mp4',
        duration: '约30分钟'
      }
    ]
  },
  {
    id: 2,
    title: '手语核心',
    description: '掌握手语的核心语法和表达',
    icon: '🎯',
    lessons: [
      {
        id: 201,
        title: '数量词的运用',
        description: '学习手语中数量词的表达方式',
        video: '/videos/lessons/02-手语核心/shuliangci.mp4',
        duration: '约20分钟'
      },
      {
        id: 202,
        title: '疑问句的表达',
        description: '学习如何用手语表达疑问',
        video: '/videos/lessons/02-手语核心/yiwenju.mp4',
        duration: '约33分钟'
      }
    ]
  },
  {
    id: 3,
    title: '情景会话',
    description: '实际场景中的手语应用',
    icon: '💬',
    lessons: [
      {
        id: 301,
        title: '打招呼',
        description: '学习日常打招呼的手语表达',
        video: '/videos/lessons/03-情景会话/dazhaohuo.mp4',
        duration: '约16分钟'
      },
      {
        id: 302,
        title: '北京',
        description: '关于北京的手语会话',
        video: '/videos/lessons/03-情景会话/beijing.mp4',
        duration: '约19分钟'
      }
    ]
  }
]

// 获取所有词汇分类
export const getCategories = () => {
  const categories = [...new Set(signVocabulary.map(item => item.category))]
  return categories
}

// 按分类获取词汇
export const getVocabularyByCategory = (category) => {
  if (!category || category === '全部') {
    return signVocabulary
  }
  return signVocabulary.filter(item => item.category === category)
}

// 搜索词汇
export const searchVocabulary = (keyword) => {
  if (!keyword) return signVocabulary
  const lowerKeyword = keyword.toLowerCase()
  return signVocabulary.filter(item =>
    item.word.includes(keyword) ||
    item.pinyin.toLowerCase().includes(lowerKeyword) ||
    item.description.includes(keyword)
  )
}

// 获取视频URL
export const getVideoUrl = (item) => {
  if (item.video) {
    return item.video
  }
  return null
}

// 获取所有课程
export const getAllCourses = () => {
  return learningCourses
}

// 获取课程详情
export const getCourseById = (courseId) => {
  return learningCourses.find(course => course.id === courseId)
}

// 获取课时详情
export const getLessonById = (lessonId) => {
  for (const course of learningCourses) {
    const lesson = course.lessons.find(l => l.id === lessonId)
    if (lesson) {
      return { ...lesson, courseName: course.title }
    }
  }
  return null
}

export default signVocabulary
