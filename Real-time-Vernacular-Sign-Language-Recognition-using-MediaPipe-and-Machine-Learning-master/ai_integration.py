"""
AI Integration Module - Alibaba Tongyi Qwen
用于手语学习App的AI智能问答和学习辅助
"""
import os
from http import HTTPStatus
try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("Warning: dashscope not installed. Run: pip install dashscope")


class SignLanguageAI:
    """手语学习AI助手"""

    def __init__(self, api_key=None):
        """
        初始化AI助手

        Args:
            api_key: 通义千问API密钥，也可通过环境变量 DASHSCOPE_API_KEY 设置
        """
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if DASHSCOPE_AVAILABLE and self.api_key:
            dashscope.api_key = self.api_key

        # 系统提示词 - 定义AI角色
        self.system_prompt = """你是一个专业的手语学习助手，名叫"手语小助手"。你的主要职责是：

1. 帮助用户学习手语知识，包括中国手语和国际手语
2. 解答关于手语的问题，如手势含义、使用场景、文化背景等
3. 提供学习建议和练习指导
4. 鼓励和激励用户坚持学习

回答要求：
- 回答要简洁明了，适合在App中显示
- 对于手势描述，要准确且易于理解
- 语气友好亲切，像一位耐心的老师
- 如果用户问了非手语相关问题，礼貌地引导回手语学习话题
"""

        # 手语知识库（用于离线模式或补充回答）
        self.gesture_knowledge = {
            "zero": {
                "name": "数字0/拳头",
                "description": "握紧拳头，所有手指弯曲收拢",
                "tip": "确保拳头握紧，拇指可以放在其他手指外侧或内侧"
            },
            "one": {
                "name": "数字1",
                "description": "伸出食指，其他手指弯曲",
                "tip": "食指要完全伸直，指向上方"
            },
            "two": {
                "name": "数字2/剪刀/胜利",
                "description": "伸出食指和中指，呈V形",
                "tip": "两指要分开，形成明显的V字形"
            },
            "three": {
                "name": "数字3",
                "description": "伸出食指、中指和无名指",
                "tip": "三根手指并拢或略微分开都可以"
            },
            "four": {
                "name": "数字4",
                "description": "伸出除拇指外的四根手指",
                "tip": "四指并拢伸直，拇指弯曲贴在掌心"
            },
            "five": {
                "name": "数字5/张开手掌",
                "description": "五指完全张开",
                "tip": "手指要完全伸直并分开"
            },
            "six": {
                "name": "数字6",
                "description": "伸出拇指和小指，其他手指弯曲",
                "tip": "这是中国手语的6，像打电话的手势"
            },
            "thumbs_up": {
                "name": "点赞/好",
                "description": "拇指向上，其他手指握拳",
                "tip": "拇指要完全伸直向上，表示赞同或很棒"
            },
            "ok": {
                "name": "OK/好的",
                "description": "拇指和食指形成圆圈，其他手指伸直",
                "tip": "圆圈要明显，其他三指自然伸展"
            },
            "i_love_you": {
                "name": "我爱你",
                "description": "同时伸出拇指、食指和小指",
                "tip": "这是美国手语中的'我爱你'，中指和无名指弯曲"
            },
            "rock": {
                "name": "摇滚/Rock",
                "description": "伸出食指和小指，拇指弯曲",
                "tip": "与'我爱你'类似，但拇指要收起来"
            }
        }

    def chat(self, user_message, conversation_history=None):
        """
        与AI对话

        Args:
            user_message: 用户消息
            conversation_history: 对话历史 [{"role": "user/assistant", "content": "..."}]

        Returns:
            AI回复内容
        """
        if not DASHSCOPE_AVAILABLE or not self.api_key:
            return self._offline_response(user_message)

        try:
            messages = [{"role": "system", "content": self.system_prompt}]

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": user_message})

            response = Generation.call(
                model="qwen-turbo",
                messages=messages,
                result_format='message'
            )

            if response.status_code == HTTPStatus.OK:
                return response.output.choices[0].message.content
            else:
                return f"抱歉，AI服务暂时不可用。错误: {response.message}"

        except Exception as e:
            return self._offline_response(user_message)

    def _offline_response(self, user_message):
        """离线模式回复"""
        user_message_lower = user_message.lower()

        # 检查是否问的是特定手势
        for gesture_id, info in self.gesture_knowledge.items():
            if gesture_id in user_message_lower or info["name"] in user_message:
                return f"**{info['name']}**\n\n做法：{info['description']}\n\n小贴士：{info['tip']}"

        # 通用回复
        if "学" in user_message or "怎么" in user_message:
            return "学习手语的建议：\n1. 从基础数字手势开始\n2. 每天练习10-15分钟\n3. 对着镜子练习，观察自己的手势\n4. 使用本App的练习功能检验学习效果"

        if "难" in user_message:
            return "别担心！手语学习需要时间和耐心。建议从简单的数字手势开始，慢慢增加难度。坚持练习，你一定能学会的！💪"

        return "你好！我是手语学习助手。你可以问我关于手语的任何问题，比如：\n- 某个手势怎么做\n- 学习手语的建议\n- 手势的含义和使用场景"

    def get_gesture_explanation(self, gesture_id):
        """
        获取手势的详细解释

        Args:
            gesture_id: 手势ID（如 "thumbs_up", "ok" 等）

        Returns:
            手势解释信息
        """
        if gesture_id in self.gesture_knowledge:
            info = self.gesture_knowledge[gesture_id]
            return {
                "gesture_id": gesture_id,
                "name": info["name"],
                "description": info["description"],
                "tip": info["tip"]
            }
        return None

    def get_learning_suggestion(self, completed_gestures, accuracy_history=None):
        """
        根据学习进度提供个性化建议

        Args:
            completed_gestures: 已完成的手势列表
            accuracy_history: 准确率历史记录

        Returns:
            学习建议
        """
        total_gestures = len(self.gesture_knowledge)
        completed_count = len(completed_gestures)
        progress = completed_count / total_gestures * 100

        if progress < 30:
            return {
                "level": "beginner",
                "message": "你刚开始学习手语，继续加油！建议先掌握数字0-5的手势。",
                "next_gestures": ["zero", "one", "two", "three", "four", "five"]
            }
        elif progress < 60:
            return {
                "level": "intermediate",
                "message": "你已经掌握了基础手势，可以尝试更复杂的手势了！",
                "next_gestures": ["six", "thumbs_up", "ok"]
            }
        elif progress < 90:
            return {
                "level": "advanced",
                "message": "太棒了！你已经是手语高手了，来挑战高级手势吧！",
                "next_gestures": ["i_love_you", "rock"]
            }
        else:
            return {
                "level": "master",
                "message": "恭喜你！你已经掌握了所有手势！继续保持练习，提高准确率！",
                "next_gestures": []
            }

    def generate_practice_feedback(self, gesture_id, is_correct, confidence):
        """
        生成练习反馈

        Args:
            gesture_id: 练习的手势ID
            is_correct: 是否正确
            confidence: 识别置信度

        Returns:
            反馈信息
        """
        gesture_info = self.gesture_knowledge.get(gesture_id, {})
        gesture_name = gesture_info.get("name", gesture_id)

        if is_correct:
            if confidence > 0.9:
                return {
                    "status": "excellent",
                    "message": f"太棒了！你的{gesture_name}手势非常标准！👏",
                    "stars": 3
                }
            elif confidence > 0.7:
                return {
                    "status": "good",
                    "message": f"很好！{gesture_name}手势识别成功！继续保持！",
                    "stars": 2
                }
            else:
                return {
                    "status": "pass",
                    "message": f"不错！{gesture_name}手势基本正确，可以再标准一些。",
                    "stars": 1,
                    "tip": gesture_info.get("tip", "")
                }
        else:
            return {
                "status": "retry",
                "message": f"再试一次！{gesture_name}手势：{gesture_info.get('description', '')}",
                "stars": 0,
                "tip": gesture_info.get("tip", "")
            }


# 创建全局实例
ai_assistant = SignLanguageAI()


def test_ai():
    """测试AI功能"""
    print("=" * 50)
    print("手语AI助手测试")
    print("=" * 50)

    # 测试离线模式
    print("\n1. 测试离线回复:")
    response = ai_assistant.chat("点赞手势怎么做？")
    print(f"回复: {response}")

    print("\n2. 测试学习建议:")
    suggestion = ai_assistant.get_learning_suggestion(["one", "two", "three"])
    print(f"建议: {suggestion}")

    print("\n3. 测试练习反馈:")
    feedback = ai_assistant.generate_practice_feedback("thumbs_up", True, 0.95)
    print(f"反馈: {feedback}")


if __name__ == "__main__":
    test_ai()
