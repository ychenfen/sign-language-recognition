import cv2
import mediapipe as mp 
import joblib
import numpy as np 

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
hands = mp_hands.Hands(
    min_detection_confidence=0.7, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

# 预加载模型（只加载一次）
clf = joblib.load('model.pkl')
print("模型加载成功! 识别 ASL 字母 A-Z")
print("按 ESC 键退出")

def data_clean(landmark):
  """
  提取手部关键点坐标，只保留 x, y（42个特征）
  兼容新版 MediaPipe
  """
  try:
    hand = landmark[0]
    clean = []

    # 21个关键点，每个取 x, y 坐标（忽略 z）
    for point in hand.landmark:
      clean.append(point.x)
      clean.append(point.y)

    return [clean]  # 返回 42 个特征

  except:
    return None

while cap.isOpened():
  success, image = cap.read()
  
  image = cv2.flip(image, 1)
  
  if not success:
    break

  # Flip the image horizontally for a later selfie-view display, and convert
  # the BGR image to RGB.
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  # To improve performance, optionally mark the image as not writeable to
  # pass by reference.
  image.flags.writeable = False
  results = hands.process(image)

  # Draw the hand annotations on the image.
  image.flags.writeable = True

  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

  if results.multi_hand_landmarks:
    for hand_landmarks in results.multi_hand_landmarks:
      mp_drawing.draw_landmarks(
          image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cleaned_landmark = data_clean(results.multi_hand_landmarks)

    if cleaned_landmark is not None:
      y_pred = clf.predict(cleaned_landmark)
      # 显示识别结果
      image = cv2.putText(image, str(y_pred[0]), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3, cv2.LINE_AA)
      image = cv2.putText(image, "ASL Letter", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA) 
    
  cv2.imshow('MediaPipe Hands', image)
  
  if cv2.waitKey(5) & 0xFF == 27:
    break

hands.close()
cap.release()
cv2.destroyAllWindows()
