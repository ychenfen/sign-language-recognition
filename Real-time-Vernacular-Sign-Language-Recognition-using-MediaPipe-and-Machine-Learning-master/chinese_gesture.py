"""
中国手语识别 - 支持数字0-10和常用手语
按照中国人习惯设计
"""
import cv2
import mediapipe as mp
import math

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    max_num_hands=2
)

cap = cv2.VideoCapture(0)

print("=" * 50)
print("Gesture Recognition System")
print("=" * 50)
print("Supported gestures:")
print("  Numbers: 0-9")
print("  Common: Thumbs Up, OK, I Love You, Rock")
print("=" * 50)
print("Press ESC to exit")


def distance(p1, p2):
    """计算两点之间的距离"""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


def get_finger_curl(landmarks, finger_idx):
    """
    计算手指弯曲程度 (0=完全伸直, 1=完全弯曲)
    finger_idx: 0=拇指, 1=食指, 2=中指, 3=无名指, 4=小指
    """
    if finger_idx == 0:  # 拇指
        tip = landmarks[4]
        pip = landmarks[3]
        mcp = landmarks[2]
        base = landmarks[1]
    else:
        tip_idx = 4 + finger_idx * 4
        pip_idx = tip_idx - 1
        mcp_idx = tip_idx - 2
        base_idx = tip_idx - 3
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]
        mcp = landmarks[mcp_idx]
        base = landmarks[base_idx]

    # 计算手指长度和弯曲程度
    finger_len = distance(base, tip)
    max_len = distance(base, mcp) + distance(mcp, pip) + distance(pip, tip)

    if max_len == 0:
        return 0.5

    curl = 1 - (finger_len / max_len)
    return curl


def get_finger_states(landmarks):
    """
    判断每根手指是否伸直
    返回: [拇指, 食指, 中指, 无名指, 小指] 的状态 (True=伸直), curls
    """
    states = []
    curls = []

    # 计算每根手指的弯曲程度
    for i in range(5):
        curl = get_finger_curl(landmarks, i)
        curls.append(curl)

    # ===== 拇指检测 =====
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]
    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]

    # 拇指伸出的判断：拇指尖到食指根部的水平距离
    # 当拇指竖起时，拇指尖会明显远离食指根部
    thumb_to_index_x = abs(thumb_tip.x - index_mcp.x)
    thumb_to_index_y = thumb_tip.y - index_mcp.y  # 负值表示拇指尖高于食指根部

    # 拇指尖到中指根部的距离
    thumb_to_middle = distance(thumb_tip, middle_mcp)
    thumb_mcp_to_middle = distance(thumb_mcp, middle_mcp)

    # 判断拇指是否伸出：
    # 1. 拇指尖远离中指根部（相对于拇指根部到中指根部的距离）
    # 2. 或者拇指尖在水平方向明显突出
    thumb_extended = (thumb_to_middle > thumb_mcp_to_middle * 1.3) or (thumb_to_index_x > 0.12)

    states.append(thumb_extended)

    # ===== 其他四指检测 =====
    # 使用指尖相对于PIP关节的y坐标来判断
    finger_tips = [8, 12, 16, 20]  # 食指、中指、无名指、小指的指尖
    finger_pips = [6, 10, 14, 18]  # 对应的PIP关节

    for i, (tip_idx, pip_idx) in enumerate(zip(finger_tips, finger_pips)):
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]

        # 指尖y坐标小于PIP关节 = 手指伸直（y轴向下为正）
        tip_above_pip = tip.y < pip.y

        # 使用弯曲度辅助判断
        curl_value = curls[i + 1]  # curls[0]是拇指

        # 伸直条件：指尖高于PIP 或 弯曲度很低
        finger_extended = tip_above_pip or (curl_value < 0.35)

        states.append(finger_extended)

    return states, curls


def recognize_chinese_gesture(finger_states, landmarks, curls=None):
    """
    识别中国手势
    curls: [拇指, 食指, 中指, 无名指, 小指] 的弯曲度 (0=伸直, 1=弯曲)
    """
    thumb, index, middle, ring, pinky = finger_states
    count = sum(finger_states)

    # 获取关键点
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    wrist = landmarks[0]

    # 如果有弯曲度信息，用它来辅助判断
    if curls is not None:
        c_thumb, c_index, c_middle, c_ring, c_pinky = curls

        # ============ 基于弯曲度的手势识别 ============
        # 根据实际测量值调整阈值

        # 点赞 Thumbs Up - 拇指伸出，其他四指弯曲
        # 实测: 0.02, 0.61, 0.71, 0.78, 0.91
        if c_thumb < 0.15 and c_index > 0.50 and c_middle > 0.60 and c_ring > 0.70 and c_pinky > 0.80:
            return "Thumbs Up!", (255, 200, 0), "Good / Like"

        # 我爱你 I Love You 和 摇滚 Rock 模式相似，用拇指位置区分
        # 我爱你实测: 0.01, 0.00, 0.39, 0.42, 0.00
        # 摇滚实测: 0.23, 0.00, 0.46, 0.42, 0.00
        if c_index < 0.15 and c_pinky < 0.15 and c_middle > 0.30 and c_ring > 0.30:
            # 检查拇指是否明显伸出（用拇指弯曲度和位置判断）
            thumb_x_dist = abs(thumb_tip.x - landmarks[5].x)
            if c_thumb < 0.10 or thumb_x_dist > 0.12:  # 拇指明显伸出
                return "I Love You!", (255, 0, 255), "Sign: I Love You"
            else:  # 拇指收起
                return "Rock!", (255, 0, 255), "Index + Pinky"

        # 数字 6 - 拇指、小指伸出，其他弯曲
        if c_thumb < 0.20 and c_pinky < 0.15 and c_index > 0.40 and c_middle > 0.40 and c_ring > 0.40:
            return "Six 6", (0, 255, 0), "Thumb + Pinky"

    # ============ 特殊手势优先判断 ============

    # OK 手势 - 拇指和食指指尖接近
    thumb_index_dist = distance(thumb_tip, index_tip)
    if thumb_index_dist < 0.06:
        if middle or ring or pinky:
            return "OK!", (255, 200, 0), "Okay / Agree"

    # 我爱你 - 拇指、食指、小指伸出
    if thumb and index and pinky and not middle and not ring:
        return "I Love You!", (255, 0, 255), "Sign: I Love You"

    # 数字 6 - 拇指和小指伸出
    if thumb and pinky and not index and not middle and not ring:
        return "Six 6", (0, 255, 0), "Thumb + Pinky"

    # 摇滚手势 - 食指+小指，无拇指
    if index and pinky and not middle and not ring and not thumb:
        return "Rock!", (255, 0, 255), "Index + Pinky"

    # 数字 8 - 拇指和食指伸出
    if thumb and index and not middle and not ring and not pinky:
        return "Eight 8", (0, 255, 0), "Thumb + Index"

    # 数字 7 - 拇指、食指、中指捏在一起
    thumb_index_close = distance(thumb_tip, index_tip) < 0.07
    index_middle_close = distance(index_tip, middle_tip) < 0.07
    if thumb_index_close and index_middle_close and not ring and not pinky:
        return "Seven 7", (0, 255, 0), "Three fingers pinch"

    # ============ 基础数字手势 ============

    # 数字 0 / 拳头
    if count == 0:
        return "Zero 0 / Fist", (0, 0, 255), "Closed fist"

    # 点赞 - 拇指伸直，其他不伸
    if thumb and not index and not middle and not ring and not pinky:
        return "Thumbs Up!", (255, 200, 0), "Good / Like"

    # 如果只有拇指算作伸出
    if count == 1 and thumb:
        return "Thumbs Up!", (255, 200, 0), "Good / Like"

    # 数字 1 - 只有食指伸直
    if index and not middle and not ring and not pinky:
        if not thumb:
            return "One 1", (0, 255, 0), "Index finger"
        else:
            return "Eight 8", (0, 255, 0), "Thumb + Index"

    # 数字 2
    if index and middle and not ring and not pinky:
        return "Two 2", (0, 255, 0), "Index + Middle"

    # 数字 3
    if index and middle and ring and not pinky:
        if not thumb:
            return "Three 3", (0, 255, 0), "Three fingers"
        else:
            return "Three 3+", (0, 255, 0), "Three + Thumb"

    # 数字 4
    if index and middle and ring and pinky and not thumb:
        return "Four 4", (0, 255, 0), "Four fingers"

    # 数字 5
    if count >= 4 and thumb:
        return "Five 5", (0, 255, 0), "Open palm"

    # 数字 9 - 食指弯曲成钩
    index_bent = landmarks[8].y > landmarks[6].y
    if index_bent and not middle and not ring and not pinky and thumb:
        return "Nine 9", (0, 255, 0), "Hooked index"

    return f"Gesture ({count} fingers)", (128, 128, 128), f"Th{'+' if thumb else '-'} In{'+' if index else '-'} Mi{'+' if middle else '-'} Ri{'+' if ring else '-'} Pi{'+' if pinky else '-'}"


def draw_info_panel(image, gesture, color, description, finger_states, curls=None):
    """绘制信息面板"""
    h, w = image.shape[:2]

    # 背景面板
    cv2.rectangle(image, (0, 0), (w, 160), (30, 30, 30), -1)

    # 手势名称
    cv2.putText(image, gesture, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 3, cv2.LINE_AA)

    # 描述
    cv2.putText(image, description, (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

    # 手指状态
    fingers = ["Th", "In", "Mi", "Ri", "Pi"]
    x_offset = 20
    for i, (name, state) in enumerate(zip(fingers, finger_states)):
        color_dot = (0, 255, 0) if state else (100, 100, 100)
        cv2.circle(image, (x_offset + i * 70 + 15, 115), 8, color_dot, -1)
        cv2.putText(image, name, (x_offset + i * 70, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)

        # 显示弯曲度数值
        if curls is not None and i < len(curls):
            curl_text = f"{curls[i]:.2f}"
            cv2.putText(image, curl_text, (x_offset + i * 70, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1, cv2.LINE_AA)


# 初始化变量
gesture_text = "Waiting..."
color = (128, 128, 128)
description = "Show your hand to camera"
finger_states = [False] * 5
curls = [0.5] * 5

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False

    results = hands.process(image_rgb)

    image_rgb.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 绘制手部骨架
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            )

            # 识别手势
            finger_states, curls = get_finger_states(hand_landmarks.landmark)
            gesture_text, color, description = recognize_chinese_gesture(
                finger_states, hand_landmarks.landmark, curls
            )

    # 绘制信息面板
    draw_info_panel(image, gesture_text, color, description, finger_states, curls)

    cv2.imshow('Chinese Sign Language Recognition', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
