"""
Gesture Recognition with Visual Effects
"""
import cv2
import mediapipe as mp
import math
import numpy as np
import random
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    max_num_hands=2
)

cap = cv2.VideoCapture(0)

print("=" * 50)
print("Gesture Recognition with Effects")
print("=" * 50)
print("Press ESC to exit")


# ==================== 特效类 ====================

class Particle:
    """粒子特效"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.life = 1.0
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # gravity
        self.life -= 0.03
        return self.life > 0

    def draw(self, image):
        if self.life > 0:
            alpha = self.life
            color = tuple(int(c * alpha) for c in self.color)
            cv2.circle(image, (int(self.x), int(self.y)),
                      int(self.size * self.life), color, -1)


class EffectManager:
    """特效管理器"""
    def __init__(self):
        self.particles = []
        self.last_gesture = ""
        self.gesture_time = 0
        self.show_celebration = False
        self.celebration_start = 0
        self.trail_points = []  # 手部轨迹
        self.pulse_phase = 0

    def add_particles(self, x, y, color, count=20):
        """添加粒子"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def on_gesture_detected(self, gesture, x, y, color):
        """当检测到新手势时"""
        if gesture != self.last_gesture and gesture not in ["Waiting...", "Gesture"]:
            self.last_gesture = gesture
            self.gesture_time = time.time()
            self.show_celebration = True
            self.celebration_start = time.time()
            # 添加庆祝粒子
            self.add_particles(x, y, color, 30)

    def add_trail_point(self, x, y):
        """添加轨迹点"""
        self.trail_points.append((x, y, time.time()))
        # 只保留最近的点
        current = time.time()
        self.trail_points = [(px, py, t) for px, py, t in self.trail_points
                            if current - t < 0.5]

    def update(self):
        """更新所有特效"""
        self.particles = [p for p in self.particles if p.update()]
        self.pulse_phase += 0.1

        # 检查庆祝是否结束
        if self.show_celebration and time.time() - self.celebration_start > 1.5:
            self.show_celebration = False

    def draw(self, image):
        """绘制所有特效"""
        # 绘制粒子
        for p in self.particles:
            p.draw(image)

        # 绘制手部轨迹
        if len(self.trail_points) > 1:
            for i in range(1, len(self.trail_points)):
                pt1 = (int(self.trail_points[i-1][0]), int(self.trail_points[i-1][1]))
                pt2 = (int(self.trail_points[i][0]), int(self.trail_points[i][1]))
                age = time.time() - self.trail_points[i][2]
                alpha = max(0, 1 - age * 2)
                thickness = int(3 * alpha) + 1
                color = (int(100 * alpha), int(255 * alpha), int(200 * alpha))
                cv2.line(image, pt1, pt2, color, thickness)


effects = EffectManager()


# ==================== 手势识别函数 ====================

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


def get_finger_curl(landmarks, finger_idx):
    if finger_idx == 0:
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

    finger_len = distance(base, tip)
    max_len = distance(base, mcp) + distance(mcp, pip) + distance(pip, tip)

    if max_len == 0:
        return 0.5
    return 1 - (finger_len / max_len)


def get_finger_states(landmarks):
    states = []
    curls = []

    for i in range(5):
        curl = get_finger_curl(landmarks, i)
        curls.append(curl)

    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]
    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]

    thumb_to_index_x = abs(thumb_tip.x - index_mcp.x)
    thumb_to_middle = distance(thumb_tip, middle_mcp)
    thumb_mcp_to_middle = distance(thumb_mcp, middle_mcp)
    thumb_extended = (thumb_to_middle > thumb_mcp_to_middle * 1.3) or (thumb_to_index_x > 0.12)
    states.append(thumb_extended)

    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    for i, (tip_idx, pip_idx) in enumerate(zip(finger_tips, finger_pips)):
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]
        tip_above_pip = tip.y < pip.y
        curl_value = curls[i + 1]
        finger_extended = tip_above_pip or (curl_value < 0.35)
        states.append(finger_extended)

    return states, curls


def recognize_gesture(finger_states, landmarks, curls=None):
    thumb, index, middle, ring, pinky = finger_states
    count = sum(finger_states)

    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]

    if curls is not None:
        c_thumb, c_index, c_middle, c_ring, c_pinky = curls

        # Thumbs Up
        if c_thumb < 0.15 and c_index > 0.50 and c_middle > 0.60 and c_ring > 0.70 and c_pinky > 0.80:
            return "Thumbs Up!", (0, 200, 255), "Good / Like"

        # I Love You / Rock
        if c_index < 0.15 and c_pinky < 0.15 and c_middle > 0.30 and c_ring > 0.30:
            thumb_x_dist = abs(thumb_tip.x - landmarks[5].x)
            if c_thumb < 0.10 or thumb_x_dist > 0.12:
                return "I Love You!", (255, 0, 255), "Sign: I Love You"
            else:
                return "Rock!", (255, 100, 0), "Index + Pinky"

        # Six
        if c_thumb < 0.20 and c_pinky < 0.15 and c_index > 0.40 and c_middle > 0.40 and c_ring > 0.40:
            return "Six 6", (0, 255, 0), "Thumb + Pinky"

    # OK
    thumb_index_dist = distance(thumb_tip, index_tip)
    if thumb_index_dist < 0.06:
        if middle or ring or pinky:
            return "OK!", (0, 200, 255), "Okay / Agree"

    # Other gestures
    if thumb and index and pinky and not middle and not ring:
        return "I Love You!", (255, 0, 255), "Sign: I Love You"

    if thumb and pinky and not index and not middle and not ring:
        return "Six 6", (0, 255, 0), "Thumb + Pinky"

    if index and pinky and not middle and not ring and not thumb:
        return "Rock!", (255, 100, 0), "Index + Pinky"

    if thumb and index and not middle and not ring and not pinky:
        return "Eight 8", (0, 255, 0), "Thumb + Index"

    if count == 0:
        return "Fist", (0, 0, 255), "Closed fist"

    if thumb and not index and not middle and not ring and not pinky:
        return "Thumbs Up!", (0, 200, 255), "Good / Like"

    if count == 1 and thumb:
        return "Thumbs Up!", (0, 200, 255), "Good / Like"

    if index and not middle and not ring and not pinky:
        if not thumb:
            return "One 1", (0, 255, 0), "Index finger"
        else:
            return "Eight 8", (0, 255, 0), "Thumb + Index"

    if index and middle and not ring and not pinky:
        return "Two 2", (0, 255, 0), "Peace / Victory"

    if index and middle and ring and not pinky:
        return "Three 3", (0, 255, 0), "Three fingers"

    if index and middle and ring and pinky and not thumb:
        return "Four 4", (0, 255, 0), "Four fingers"

    if count >= 4 and thumb:
        return "Five 5", (0, 255, 0), "High Five!"

    return f"Gesture ({count})", (128, 128, 128), f"Fingers: {count}"


# ==================== UI绘制函数 ====================

def draw_fancy_panel(image, gesture, color, description, finger_states, curls, effects_mgr):
    """绘制带特效的UI面板"""
    h, w = image.shape[:2]

    # 渐变背景
    overlay = image.copy()
    for i in range(120):
        alpha = 0.9 - (i / 120) * 0.5
        cv2.line(overlay, (0, i), (w, i), (20, 20, 30), 1)
    cv2.addWeighted(overlay, 0.8, image, 0.2, 0, image)

    # 脉冲效果
    pulse = abs(math.sin(effects_mgr.pulse_phase)) * 0.3 + 0.7

    # 手势名称 - 带发光效果
    if effects_mgr.show_celebration:
        # 发光效果
        glow_color = tuple(min(255, int(c * 1.5)) for c in color)
        cv2.putText(image, gesture, (18, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, glow_color, 5, cv2.LINE_AA)

    cv2.putText(image, gesture, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, color, 3, cv2.LINE_AA)

    # 描述
    cv2.putText(image, description, (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

    # 手指状态 - 动态指示器
    fingers = ["Th", "In", "Mi", "Ri", "Pi"]
    x_offset = 20
    for i, (name, state) in enumerate(zip(fingers, finger_states)):
        x = x_offset + i * 70 + 15
        y = 110

        # 外圈
        ring_color = (0, 255, 0) if state else (60, 60, 60)
        cv2.circle(image, (x, y), 12, ring_color, 2)

        # 内圈 - 带脉冲
        if state:
            inner_size = int(8 * pulse)
            cv2.circle(image, (x, y), inner_size, (0, 255, 0), -1)
        else:
            cv2.circle(image, (x, y), 6, (40, 40, 40), -1)

        # 名称
        cv2.putText(image, name, (x - 10, y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)


def draw_hand_effects(image, hand_landmarks, w, h, color):
    """绘制手部特效"""
    # 获取手掌中心
    palm_x = int(hand_landmarks.landmark[9].x * w)
    palm_y = int(hand_landmarks.landmark[9].y * h)

    # 添加轨迹点
    effects.add_trail_point(palm_x, palm_y)

    # 绘制指尖光点
    fingertips = [4, 8, 12, 16, 20]
    for tip_idx in fingertips:
        x = int(hand_landmarks.landmark[tip_idx].x * w)
        y = int(hand_landmarks.landmark[tip_idx].y * h)

        # 发光效果
        cv2.circle(image, (x, y), 10, (color[0]//3, color[1]//3, color[2]//3), -1)
        cv2.circle(image, (x, y), 6, color, -1)
        cv2.circle(image, (x, y), 3, (255, 255, 255), -1)

    return palm_x, palm_y


# ==================== 主循环 ====================

gesture_text = "Waiting..."
color = (128, 128, 128)
description = "Show your hand"
finger_states = [False] * 5
curls = [0.5] * 5

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    h, w = image.shape[:2]

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = hands.process(image_rgb)
    image_rgb.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    palm_x, palm_y = w // 2, h // 2

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 绘制骨架 - 自定义样式
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 128), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            )

            # 手部特效
            palm_x, palm_y = draw_hand_effects(image, hand_landmarks, w, h, color)

            # 识别手势
            finger_states, curls = get_finger_states(hand_landmarks.landmark)
            gesture_text, color, description = recognize_gesture(
                finger_states, hand_landmarks.landmark, curls
            )

            # 触发特效
            effects.on_gesture_detected(gesture_text, palm_x, palm_y, color)

    # 更新和绘制特效
    effects.update()
    effects.draw(image)

    # 绘制UI面板
    draw_fancy_panel(image, gesture_text, color, description, finger_states, curls, effects)

    # 显示FPS
    cv2.putText(image, "Press ESC to exit", (w - 180, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1, cv2.LINE_AA)

    cv2.imshow('Gesture Recognition', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
