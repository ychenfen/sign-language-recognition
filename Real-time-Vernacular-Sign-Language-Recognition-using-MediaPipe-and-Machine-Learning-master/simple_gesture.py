"""
简单手势识别 - 基于规则识别数字 1-5 和常用手势
无需训练，直接可用
"""
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    max_num_hands=1
)

cap = cv2.VideoCapture(0)

print("=" * 40)
print("简单手势识别 - 支持以下手势：")
print("  ✊ 拳头 (Rock)")
print("  ☝️  数字 1")
print("  ✌️  数字 2 / 剪刀")
print("  🤟 数字 3")
print("  🖖 数字 4")
print("  🖐️  数字 5 / 布")
print("  👍 点赞 (Thumb Up)")
print("  👌 OK")
print("=" * 40)
print("按 ESC 键退出")


def get_finger_states(landmarks):
    """
    判断每根手指是否伸直
    返回: [拇指, 食指, 中指, 无名指, 小指] 的状态 (True=伸直)
    """
    states = []

    # 拇指 - 用指尖到手腕的距离判断
    # 拇指伸直时，指尖(4)远离食指根部(5)
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]
    index_mcp = landmarks[5]

    # 计算拇指是否伸出：指尖到食指根部的距离
    thumb_to_index = ((thumb_tip.x - index_mcp.x)**2 + (thumb_tip.y - index_mcp.y)**2)**0.5
    thumb_base_to_index = ((thumb_mcp.x - index_mcp.x)**2 + (thumb_mcp.y - index_mcp.y)**2)**0.5
    states.append(thumb_to_index > thumb_base_to_index * 1.2)

    # 其他四指 - 判断指尖是否高于中间关节
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    for tip, pip in zip(finger_tips, finger_pips):
        # 指尖y坐标小于中间关节 = 手指伸直
        states.append(landmarks[tip].y < landmarks[pip].y)

    return states


def recognize_gesture(finger_states, landmarks=None):
    """
    根据手指状态识别手势（中国手势习惯）
    """
    thumb, index, middle, ring, pinky = finger_states
    count = sum(finger_states)

    # OK 手势 - 拇指和食指指尖接近（优先判断）
    if landmarks is not None:
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
        if distance < 0.05 and middle and ring and pinky:
            return "OK 👌", (255, 200, 0)

    # 拳头 - 没有手指伸直
    if count == 0:
        return "拳头 ✊", (0, 0, 255)

    # 点赞 - 拇指伸出，其他四指弯曲
    if thumb and count == 1:
        return "点赞 👍", (255, 200, 0)

    # 数字 1 - 只有食指伸直（不管拇指）
    if index and not middle and not ring and not pinky:
        return "数字 1 ☝️", (0, 255, 0)

    # 数字 2 - 食指+中指伸直
    if index and middle and not ring and not pinky:
        return "数字 2 ✌️", (0, 255, 0)

    # 数字 3 - 食指+中指+无名指 或 拇指+食指+中指
    if index and middle and ring and not pinky and not thumb:
        return "数字 3", (0, 255, 0)
    if thumb and index and middle and not ring and not pinky:
        return "数字 3", (0, 255, 0)

    # 数字 4 - 四指伸直（除拇指）
    if index and middle and ring and pinky and not thumb:
        return "数字 4", (0, 255, 0)

    # 数字 5 - 全部张开
    if count >= 4 and thumb:
        return "数字 5 🖐️", (0, 255, 0)

    # 我爱你
    if thumb and index and pinky and not middle and not ring:
        return "我爱你 🤟", (255, 0, 255)

    return f"手指数: {count}", (128, 128, 128)


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

    gesture_text = "无手势"
    color = (128, 128, 128)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 绘制手部骨架
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            )

            # 识别手势
            finger_states = get_finger_states(hand_landmarks.landmark)
            gesture_text, color = recognize_gesture(finger_states, hand_landmarks.landmark)

    # 显示结果
    cv2.rectangle(image, (0, 0), (400, 120), (0, 0, 0), -1)
    cv2.putText(image, gesture_text, (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3, cv2.LINE_AA)

    # 显示手指状态调试信息
    if results.multi_hand_landmarks:
        fingers = ["拇", "食", "中", "无", "小"]
        status = ""
        for i, (name, state) in enumerate(zip(fingers, finger_states)):
            status += f"{name}{'✓' if state else '✗'} "
        cv2.putText(image, status, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('Simple Gesture Recognition', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
