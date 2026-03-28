"""
Sign Language Recognition API Server
Supports both static gesture recognition and LSTM-based action recognition

Resources:
- Static gestures: MediaPipe hand detection
- Dynamic actions: LSTM model trained on 6 common sign language actions
- AI Assistant: Alibaba Tongyi Qwen integration
"""
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import base64
import math
import threading
import time
import os

# Try to import TensorFlow for LSTM model
try:
    from tensorflow.keras.models import load_model
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    print("Warning: TensorFlow not available, LSTM recognition disabled")

# AI Integration
try:
    from ai_integration import SignLanguageAI
    ai_assistant = SignLanguageAI()
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI integration not available")

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')

app = Flask(__name__, static_folder=DIST_DIR, static_url_path='/')
CORS(app)

# ==================== MediaPipe Setup ====================
mp_hands = mp.solutions.hands
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    max_num_hands=1
)

# ==================== LSTM Model Setup ====================
lstm_model = None
LSTM_ACTIONS = np.array(['你好', '谢谢', '对不起', '可以', '帮助', '玩'])
SEQUENCE_LENGTH = 40
sequence_buffer = []

if LSTM_AVAILABLE:
    model_path = os.path.join(os.path.dirname(__file__), 'models', '手语数据训练参数.h5')
    if os.path.exists(model_path):
        try:
            lstm_model = load_model(model_path)
            print(f"LSTM model loaded from {model_path}")
        except Exception as e:
            print(f"Error loading LSTM model: {e}")
            lstm_model = None
    else:
        print(f"LSTM model not found at {model_path}")

# Global variables
camera = None
camera_lock = threading.Lock()


# ==================== Helper Functions ====================

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


def recognize_static_gesture(landmarks, curls):
    """Recognize static hand gesture"""
    finger_states, curls = get_finger_states(landmarks)
    thumb, index, middle, ring, pinky = finger_states
    count = sum(finger_states)
    c_thumb, c_index, c_middle, c_ring, c_pinky = curls

    thumb_tip = landmarks[4]
    index_tip = landmarks[8]

    # Thumbs Up
    if c_thumb < 0.15 and c_index > 0.50 and c_middle > 0.60 and c_ring > 0.70 and c_pinky > 0.80:
        return {"gesture": "thumbs_up", "name": "点赞/好", "confidence": 0.95}

    # I Love You
    if c_index < 0.15 and c_pinky < 0.15 and c_middle > 0.30 and c_ring > 0.30:
        thumb_x_dist = abs(thumb_tip.x - landmarks[5].x)
        if c_thumb < 0.10 or thumb_x_dist > 0.12:
            return {"gesture": "i_love_you", "name": "我爱你", "confidence": 0.90}
        else:
            return {"gesture": "rock", "name": "摇滚", "confidence": 0.90}

    # OK
    thumb_index_dist = distance(thumb_tip, index_tip)
    if thumb_index_dist < 0.06 and (middle or ring or pinky):
        return {"gesture": "ok", "name": "OK/好的", "confidence": 0.90}

    # Six
    if c_thumb < 0.20 and c_pinky < 0.15 and c_index > 0.40 and c_middle > 0.40 and c_ring > 0.40:
        return {"gesture": "six", "name": "六", "confidence": 0.85}

    # Numbers
    if count == 0:
        return {"gesture": "zero", "name": "零/拳头", "confidence": 0.90}

    if thumb and not index and not middle and not ring and not pinky:
        return {"gesture": "thumbs_up", "name": "点赞/好", "confidence": 0.85}

    if index and not middle and not ring and not pinky and not thumb:
        return {"gesture": "one", "name": "一", "confidence": 0.90}

    if index and middle and not ring and not pinky:
        return {"gesture": "two", "name": "二", "confidence": 0.90}

    if index and middle and ring and not pinky and not thumb:
        return {"gesture": "three", "name": "三", "confidence": 0.90}

    if index and middle and ring and pinky and not thumb:
        return {"gesture": "four", "name": "四", "confidence": 0.90}

    if count >= 4 and thumb:
        return {"gesture": "five", "name": "五", "confidence": 0.90}

    if thumb and index and not middle and not ring and not pinky:
        return {"gesture": "eight", "name": "八", "confidence": 0.85}

    return {"gesture": "unknown", "name": f"未知 ({count}指)", "confidence": 0.5}


def extract_keypoints(results):
    """Extract keypoints from MediaPipe holistic results for LSTM model"""
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)

    face = np.array([[res.x, res.y, res.z] for res in
                     results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)

    lh = np.array([[res.x, res.y, res.z] for res in
                   results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)

    rh = np.array([[res.x, res.y, res.z] for res in
                   results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)

    return np.concatenate([pose, face, lh, rh])


def process_image_static(image_data):
    """Process image for static gesture recognition"""
    if isinstance(image_data, str):
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        image = image_data

    if image is None:
        return {"error": "Invalid image"}

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if not results.multi_hand_landmarks:
        return {"gesture": "no_hand", "name": "未检测到手", "confidence": 0}

    hand_landmarks = results.multi_hand_landmarks[0]
    landmarks = hand_landmarks.landmark
    finger_states, curls = get_finger_states(landmarks)
    result = recognize_static_gesture(landmarks, curls)
    result["finger_states"] = finger_states
    result["curls"] = [round(c, 3) for c in curls]

    return result


def process_image_lstm(image_data):
    """Process image for LSTM-based action recognition"""
    global sequence_buffer

    if lstm_model is None:
        return {"error": "LSTM model not available"}

    if isinstance(image_data, str):
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        image = image_data

    if image is None:
        return {"error": "Invalid image"}

    # Use holistic model for full body detection
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = holistic.process(image_rgb)

        # Extract keypoints
        keypoints = extract_keypoints(results)
        sequence_buffer.append(keypoints)
        sequence_buffer = sequence_buffer[-SEQUENCE_LENGTH:]

        if len(sequence_buffer) < SEQUENCE_LENGTH:
            return {
                "action": "collecting",
                "name": "正在收集帧...",
                "confidence": 0,
                "frames_collected": len(sequence_buffer),
                "frames_needed": SEQUENCE_LENGTH
            }

        # Predict action
        res = lstm_model.predict(np.expand_dims(sequence_buffer, axis=0), verbose=0)[0]
        action_idx = np.argmax(res)
        confidence = float(res[action_idx])

        return {
            "action": LSTM_ACTIONS[action_idx],
            "name": LSTM_ACTIONS[action_idx],
            "confidence": confidence,
            "all_probabilities": {action: float(prob) for action, prob in zip(LSTM_ACTIONS, res)}
        }


def frontend_ready():
    return os.path.exists(os.path.join(DIST_DIR, 'index.html'))


# ==================== API Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Sign Language Recognition API is running",
        "features": {
            "static_gesture": True,
            "lstm_action": lstm_model is not None,
            "ai_assistant": AI_AVAILABLE
        }
    })


@app.route('/api/recognize', methods=['POST'])
def recognize():
    """Recognize static gesture from image"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        result = process_image_static(data['image'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recognize/action', methods=['POST'])
def recognize_action():
    """Recognize dynamic action using LSTM model"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        result = process_image_lstm(data['image'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recognize/reset', methods=['POST'])
def reset_sequence():
    """Reset the LSTM sequence buffer"""
    global sequence_buffer
    sequence_buffer = []
    return jsonify({"status": "ok", "message": "Sequence buffer reset"})


@app.route('/api/verify', methods=['POST'])
def verify_gesture():
    """Verify if user's gesture matches expected gesture"""
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'expected' not in data:
            return jsonify({"error": "Missing image or expected gesture"}), 400

        result = process_image_static(data['image'])
        expected = data['expected'].lower()
        detected = result.get('gesture', 'unknown')

        is_correct = detected == expected
        confidence = result.get('confidence', 0)

        if is_correct and confidence > 0.8:
            message = "非常好！手势正确！"
        elif is_correct:
            message = "正确！可以再清晰一些。"
        elif detected == "no_hand":
            message = "未检测到手，请将手放在摄像头前。"
        else:
            message = f"不太对哦，你做的是'{result.get('name')}'，应该是'{expected}'。"

        return jsonify({
            "correct": is_correct,
            "detected": detected,
            "detected_name": result.get('name'),
            "expected": expected,
            "confidence": confidence,
            "message": message
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/gestures', methods=['GET'])
def list_gestures():
    """List all supported gestures"""
    static_gestures = [
        {"id": "zero", "name": "零/拳头", "description": "握拳", "type": "static"},
        {"id": "one", "name": "一", "description": "伸出食指", "type": "static"},
        {"id": "two", "name": "二", "description": "伸出食指和中指", "type": "static"},
        {"id": "three", "name": "三", "description": "伸出食指、中指、无名指", "type": "static"},
        {"id": "four", "name": "四", "description": "四指伸开（除拇指）", "type": "static"},
        {"id": "five", "name": "五", "description": "五指张开", "type": "static"},
        {"id": "six", "name": "六", "description": "拇指和小指伸开", "type": "static"},
        {"id": "eight", "name": "八", "description": "拇指和食指伸开", "type": "static"},
        {"id": "thumbs_up", "name": "点赞/好", "description": "竖起大拇指", "type": "static"},
        {"id": "ok", "name": "OK/好的", "description": "拇指和食指圈成O形", "type": "static"},
        {"id": "i_love_you", "name": "我爱你", "description": "拇指、食指、小指伸出", "type": "static"},
    ]

    dynamic_actions = [
        {"id": "你好", "name": "你好", "description": "问候手势", "type": "dynamic"},
        {"id": "谢谢", "name": "谢谢", "description": "感谢手势", "type": "dynamic"},
        {"id": "对不起", "name": "对不起", "description": "道歉手势", "type": "dynamic"},
        {"id": "可以", "name": "可以", "description": "同意手势", "type": "dynamic"},
        {"id": "帮助", "name": "帮助", "description": "请求帮助手势", "type": "dynamic"},
        {"id": "玩", "name": "玩", "description": "玩耍手势", "type": "dynamic"},
    ]

    return jsonify({
        "static_gestures": static_gestures,
        "dynamic_actions": dynamic_actions if lstm_model else [],
        "lstm_available": lstm_model is not None
    })


# ==================== AI Endpoints ====================

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI Chat - Ask questions about sign language"""
    if not AI_AVAILABLE:
        return jsonify({
            "status": "error",
            "reply": "AI服务暂不可用，请检查配置。"
        }), 503

    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400

        message = data['message']
        history = data.get('history', None)
        reply = ai_assistant.chat(message, history)

        return jsonify({
            "status": "success",
            "reply": reply
        })
    except Exception as e:
        return jsonify({"status": "error", "reply": str(e)}), 500


@app.route('/api/ai/explain/<gesture_id>', methods=['GET'])
def ai_explain_gesture(gesture_id):
    """Get detailed explanation for a gesture"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI service not available"}), 503

    try:
        explanation = ai_assistant.get_gesture_explanation(gesture_id)
        if explanation:
            return jsonify(explanation)
        else:
            return jsonify({"error": f"Unknown gesture: {gesture_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/suggestion', methods=['POST'])
def ai_learning_suggestion():
    """Get personalized learning suggestions"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI service not available"}), 503

    try:
        data = request.get_json() or {}
        completed = data.get('completed_gestures', [])
        accuracy = data.get('accuracy_history', None)
        suggestion = ai_assistant.get_learning_suggestion(completed, accuracy)
        return jsonify(suggestion)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/feedback', methods=['POST'])
def ai_practice_feedback():
    """Get AI-generated feedback for practice"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI service not available"}), 503

    try:
        data = request.get_json() or {}
        gesture_id = data.get('gesture_id')
        is_correct = data.get('is_correct')
        confidence = data.get('confidence', 0.5)

        if gesture_id is None or is_correct is None:
            return jsonify({"error": "Missing gesture_id or is_correct"}), 400

        feedback = ai_assistant.generate_practice_feedback(
            gesture_id,
            bool(is_correct),
            float(confidence)
        )
        return jsonify(feedback)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve built frontend in customer delivery mode."""
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404

    if not frontend_ready():
        return Response(
            "Frontend build not found. Run `npm install && npm run build` in the project root.",
            mimetype='text/plain',
            status=503
        )

    asset_path = os.path.join(DIST_DIR, path)
    if path and os.path.exists(asset_path) and os.path.isfile(asset_path):
        return send_from_directory(DIST_DIR, path)

    return send_from_directory(DIST_DIR, 'index.html')


# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5001'))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    print("=" * 60)
    print("Sign Language Recognition API Server")
    print("=" * 60)
    print("\nFeatures:")
    print(f"  - Static Gesture Recognition: Enabled")
    print(f"  - LSTM Action Recognition: {'Enabled' if lstm_model else 'Disabled'}")
    print(f"  - AI Assistant: {'Enabled' if AI_AVAILABLE else 'Disabled'}")
    print("\nEndpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/gestures            - List supported gestures")
    print("  POST /api/recognize           - Recognize static gesture")
    print("  POST /api/recognize/action    - Recognize dynamic action (LSTM)")
    print("  POST /api/recognize/reset     - Reset LSTM sequence buffer")
    print("  POST /api/verify              - Verify gesture matches expected")
    print("\nAI Endpoints:")
    print("  POST /api/ai/chat             - Chat with AI assistant")
    print("  GET  /api/ai/explain/<id>     - Get gesture explanation")
    print("  POST /api/ai/suggestion       - Get learning suggestions")
    print("  POST /api/ai/feedback         - Get practice feedback")
    print("\nFrontend:")
    print(f"  - Built frontend detected: {'Yes' if frontend_ready() else 'No'}")
    print("=" * 60)
    print(f"Starting server on http://localhost:{port}")

    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
