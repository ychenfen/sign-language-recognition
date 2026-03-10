#!/usr/bin/env python3
"""
生成手语占位图片
为所有词汇生成简单的SVG占位图
"""
import os

# 词汇列表
vocabulary = [
    ("nihao", "你好", "#667eea", "竖起大拇指，表示问候"),
    ("xiexie", "谢谢", "#67c23a", "手掌向外推，表示感谢"),
    ("duibuqi", "对不起", "#f56c6c", "握拳轻敲胸口"),
    ("zaijian", "再见", "#e6a23c", "手掌左右摆动"),
    ("qing", "请", "#909399", "手掌向前做请的动作"),
    ("bukeqi", "不客气", "#409eff", "双手交叉摆动"),
    ("shi", "是", "#67c23a", "拇指向下点一下"),
    ("bushi", "不是", "#f56c6c", "食指左右摆动"),
    ("wo", "我", "#667eea", "食指指向自己"),
    ("ni", "你", "#667eea", "食指指向对方"),
    ("ta", "他/她", "#667eea", "食指指向旁边"),
    ("shenme", "什么", "#e6a23c", "手掌向上摇晃"),
    ("nali", "哪里", "#e6a23c", "食指画小圈"),
    ("zenme", "怎么", "#e6a23c", "双手交替翻动"),
    ("keyi", "可以", "#67c23a", "拇指向下点"),
    ("bukeyi", "不可以", "#f56c6c", "双手交叉成X形"),
    ("xihuan", "喜欢", "#f56c6c", "手放心口轻拍"),
    ("gaoxing", "高兴", "#67c23a", "双手向上抬起"),
    ("nanguo", "难过", "#909399", "食指从眼角向下划"),
    ("shengqi", "生气", "#f56c6c", "双手握拳抖动"),
    ("haipa", "害怕", "#909399", "手指张开抖动"),
    ("ai", "爱", "#f56c6c", "双手交叉放在心口"),
    ("xiang", "想", "#667eea", "食指点太阳穴"),
    ("ling", "零", "#409eff", "拇指食指围成圆"),
    ("yi", "一", "#409eff", "伸出食指"),
    ("er", "二", "#409eff", "伸出食指和中指"),
    ("san", "三", "#409eff", "伸出三指"),
    ("si", "四", "#409eff", "伸出四指"),
    ("wu", "五", "#409eff", "五指张开"),
    ("liu", "六", "#409eff", "拇指和小指伸出"),
    ("qi", "七", "#409eff", "三指捏在一起"),
    ("ba", "八", "#409eff", "拇指食指张开成八字"),
    ("jiu", "九", "#409eff", "食指弯曲成钩"),
    ("shi10", "十", "#409eff", "双手食指交叉"),
    ("jintian", "今天", "#667eea", "食指指向脚下"),
    ("mingtian", "明天", "#667eea", "食指向前指"),
    ("zuotian", "昨天", "#667eea", "拇指向后指"),
    ("baba", "爸爸", "#409eff", "拇指在额头前"),
    ("mama", "妈妈", "#f56c6c", "手心贴脸颊"),
    ("gege", "哥哥", "#409eff", "两指在头上方"),
    ("jiejie", "姐姐", "#f56c6c", "女+高的手势"),
    ("didi", "弟弟", "#409eff", "手在身体下方"),
    ("meimei", "妹妹", "#f56c6c", "女+矮的手势"),
    ("chi", "吃", "#e6a23c", "做拿筷子送嘴边"),
    ("he", "喝", "#409eff", "做握杯子倾斜"),
    ("kan", "看", "#667eea", "两指指向眼睛再向前"),
    ("ting", "听", "#667eea", "手放耳朵旁边"),
    ("shuo", "说", "#667eea", "食指从嘴边向外"),
    ("zou", "走", "#67c23a", "两指交替前进"),
    ("pao", "跑", "#e6a23c", "双拳快速摆动"),
    ("xuexi", "学习", "#667eea", "从书本拿知识到头"),
    ("gongzuo", "工作", "#909399", "双拳交替敲击"),
    ("bangzhu", "帮助", "#67c23a", "右手托住左手向上"),
    ("wan", "玩", "#e6a23c", "双手摇晃表示轻松"),
]

def generate_svg(pinyin, word, color, desc):
    """生成SVG占位图"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color}20"/>
      <stop offset="100%" style="stop-color:{color}10"/>
    </linearGradient>
  </defs>
  <!-- 背景 -->
  <rect width="200" height="200" fill="url(#bg)" rx="16"/>
  <rect x="4" y="4" width="192" height="192" fill="none" stroke="{color}" stroke-width="2" rx="14" opacity="0.3"/>

  <!-- 手形图标 -->
  <g transform="translate(100, 75)">
    <circle cx="0" cy="0" r="45" fill="{color}" opacity="0.15"/>
    <text x="0" y="8" text-anchor="middle" font-size="40" fill="{color}">🤟</text>
  </g>

  <!-- 词汇 -->
  <text x="100" y="145" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="{color}" font-weight="bold">{word}</text>

  <!-- 说明 -->
  <text x="100" y="170" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#666">{desc[:15]}...</text>

  <!-- 拼音 -->
  <text x="100" y="188" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#999">{pinyin}</text>
</svg>'''
    return svg

def main():
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'public', 'images', 'signs')
    os.makedirs(output_dir, exist_ok=True)

    # 生成所有SVG
    for pinyin, word, color, desc in vocabulary:
        svg_content = generate_svg(pinyin, word, color, desc)
        filepath = os.path.join(output_dir, f'{pinyin}.svg')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f'Generated: {filepath}')

    print(f'\n共生成 {len(vocabulary)} 个SVG文件')

if __name__ == '__main__':
    main()
