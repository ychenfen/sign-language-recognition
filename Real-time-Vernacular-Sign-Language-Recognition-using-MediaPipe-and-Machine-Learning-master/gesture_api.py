"""
Gesture Recognition API Server
Flask API for Java backend integration
With AI Integration (Alibaba Tongyi Qwen)
"""
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import base64
import math
import threading
import time

# AI Integration
try:
    from ai_integration import SignLanguageAI
    ai_assistant = SignLanguageAI()
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI integration not available")

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    max_num_hands=1
)

# Global variable for webcam stream
camera = None
camera_lock = threading.Lock()


# ==================== Gesture Recognition Functions ====================

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


def recognize_gesture(landmarks, curls):
    """Recognize gesture and return result"""
    finger_states, curls = get_finger_states(landmarks)
    thumb, index, middle, ring, pinky = finger_states
    count = sum(finger_states)
    c_thumb, c_index, c_middle, c_ring, c_pinky = curls

    thumb_tip = landmarks[4]
    index_tip = landmarks[8]

    # Gesture recognition logic
    gestures = []

    # Thumbs Up
    if c_thumb < 0.15 and c_index > 0.50 and c_middle > 0.60 and c_ring > 0.70 and c_pinky > 0.80:
        return {"gesture": "thumbs_up", "name": "Thumbs Up", "confidence": 0.95}

    # I Love You / Rock
    if c_index < 0.15 and c_pinky < 0.15 and c_middle > 0.30 and c_ring > 0.30:
        thumb_x_dist = abs(thumb_tip.x - landmarks[5].x)
        if c_thumb < 0.10 or thumb_x_dist > 0.12:
            return {"gesture": "i_love_you", "name": "I Love You", "confidence": 0.90}
        else:
            return {"gesture": "rock", "name": "Rock", "confidence": 0.90}

    # OK
    thumb_index_dist = distance(thumb_tip, index_tip)
    if thumb_index_dist < 0.06 and (middle or ring or pinky):
        return {"gesture": "ok", "name": "OK", "confidence": 0.90}

    # Six
    if c_thumb < 0.20 and c_pinky < 0.15 and c_index > 0.40 and c_middle > 0.40 and c_ring > 0.40:
        return {"gesture": "six", "name": "Six 6", "confidence": 0.85}

    # Numbers
    if count == 0:
        return {"gesture": "zero", "name": "Zero / Fist", "confidence": 0.90}

    if thumb and not index and not middle and not ring and not pinky:
        return {"gesture": "thumbs_up", "name": "Thumbs Up", "confidence": 0.85}

    if index and not middle and not ring and not pinky and not thumb:
        return {"gesture": "one", "name": "One 1", "confidence": 0.90}

    if index and middle and not ring and not pinky:
        return {"gesture": "two", "name": "Two 2", "confidence": 0.90}

    if index and middle and ring and not pinky and not thumb:
        return {"gesture": "three", "name": "Three 3", "confidence": 0.90}

    if index and middle and ring and pinky and not thumb:
        return {"gesture": "four", "name": "Four 4", "confidence": 0.90}

    if count >= 4 and thumb:
        return {"gesture": "five", "name": "Five 5", "confidence": 0.90}

    if thumb and index and not middle and not ring and not pinky:
        return {"gesture": "eight", "name": "Eight 8", "confidence": 0.85}

    return {"gesture": "unknown", "name": f"Unknown ({count} fingers)", "confidence": 0.5}


def process_image(image_data):
    """Process image and return gesture result"""
    # Decode base64 image
    if isinstance(image_data, str):
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        image = image_data

    if image is None:
        return {"error": "Invalid image"}

    # Convert to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if not results.multi_hand_landmarks:
        return {"gesture": "no_hand", "name": "No hand detected", "confidence": 0}

    # Process first hand
    hand_landmarks = results.multi_hand_landmarks[0]
    landmarks = hand_landmarks.landmark

    # Get finger states and curls
    finger_states, curls = get_finger_states(landmarks)

    # Recognize gesture
    result = recognize_gesture(landmarks, curls)
    result["finger_states"] = finger_states
    result["curls"] = [round(c, 3) for c in curls]

    return result


# ==================== API Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Gesture API is running"})


@app.route('/api/recognize', methods=['POST'])
def recognize():
    """
    Recognize gesture from uploaded image

    Request body:
    - image: base64 encoded image string

    Response:
    - gesture: gesture identifier (e.g., "thumbs_up", "ok")
    - name: human readable name
    - confidence: recognition confidence (0-1)
    - finger_states: [thumb, index, middle, ring, pinky] boolean array
    - curls: [thumb, index, middle, ring, pinky] curl values (0-1)
    """
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        result = process_image(data['image'])
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/verify', methods=['POST'])
def verify_gesture():
    """
    Verify if user's gesture matches expected gesture

    Request body:
    - image: base64 encoded image
    - expected: expected gesture identifier

    Response:
    - correct: boolean
    - detected: detected gesture
    - expected: expected gesture
    - message: feedback message
    """
    try:
        data = request.get_json()

        if not data or 'image' not in data or 'expected' not in data:
            return jsonify({"error": "Missing image or expected gesture"}), 400

        result = process_image(data['image'])
        expected = data['expected'].lower()
        detected = result.get('gesture', 'unknown')

        is_correct = detected == expected
        confidence = result.get('confidence', 0)

        # Generate feedback message
        if is_correct and confidence > 0.8:
            message = "Perfect! Your gesture is correct!"
        elif is_correct:
            message = "Good! Try to make the gesture clearer."
        elif detected == "no_hand":
            message = "No hand detected. Please show your hand to the camera."
        else:
            message = f"Not quite right. You showed '{result.get('name')}', expected '{expected}'."

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
    gestures = [
        {"id": "zero", "name": "Zero / Fist", "description": "Closed fist"},
        {"id": "one", "name": "One 1", "description": "Index finger up"},
        {"id": "two", "name": "Two 2", "description": "Index and middle finger up"},
        {"id": "three", "name": "Three 3", "description": "Index, middle, ring fingers up"},
        {"id": "four", "name": "Four 4", "description": "Four fingers up (no thumb)"},
        {"id": "five", "name": "Five 5", "description": "All fingers open"},
        {"id": "six", "name": "Six 6", "description": "Thumb and pinky out"},
        {"id": "eight", "name": "Eight 8", "description": "Thumb and index out"},
        {"id": "thumbs_up", "name": "Thumbs Up", "description": "Thumb up, others closed"},
        {"id": "ok", "name": "OK", "description": "Thumb and index touching, others open"},
        {"id": "i_love_you", "name": "I Love You", "description": "Thumb, index, pinky out"},
        {"id": "rock", "name": "Rock", "description": "Index and pinky out, thumb in"},
    ]
    return jsonify({"gestures": gestures})


# ==================== Video Stream (Optional) ====================

def generate_frames():
    """Generate video frames for streaming"""
    global camera

    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)

        # Process frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Recognize gesture
                finger_states, curls = get_finger_states(hand_landmarks.landmark)
                result = recognize_gesture(hand_landmarks.landmark, curls)

                # Draw result
                cv2.putText(frame, result['name'], (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/api/stream')
def video_stream():
    """Video stream endpoint for real-time recognition"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


# ==================== AI Endpoints ====================

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """
    AI Chat - Ask questions about sign language

    Request body:
    - message: User's message/question
    - history: (optional) Conversation history

    Response:
    - reply: AI's response
    - status: "success" or "error"
    """
    if not AI_AVAILABLE:
        return jsonify({
            "status": "error",
            "reply": "AI service is not available. Please check configuration."
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
    """
    Get detailed explanation for a gesture

    Response:
    - gesture_id: Gesture identifier
    - name: Gesture name
    - description: How to make the gesture
    - tip: Helpful tip
    """
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
    """
    Get personalized learning suggestions

    Request body:
    - completed_gestures: List of completed gesture IDs
    - accuracy_history: (optional) Accuracy history

    Response:
    - level: User's current level
    - message: Personalized suggestion
    - next_gestures: Recommended gestures to learn next
    """
    if not AI_AVAILABLE:
        return jsonify({"error": "AI service not available"}), 503

    try:
        data = request.get_json()
        completed = data.get('completed_gestures', [])
        accuracy = data.get('accuracy_history', None)

        suggestion = ai_assistant.get_learning_suggestion(completed, accuracy)

        return jsonify(suggestion)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/feedback', methods=['POST'])
def ai_practice_feedback():
    """
    Get AI-generated feedback for practice

    Request body:
    - gesture_id: The gesture being practiced
    - is_correct: Whether the gesture was correct
    - confidence: Recognition confidence

    Response:
    - status: "excellent", "good", "pass", or "retry"
    - message: Feedback message
    - stars: 0-3 star rating
    - tip: (optional) Helpful tip
    """
    if not AI_AVAILABLE:
        return jsonify({"error": "AI service not available"}), 503

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        gesture_id = data.get('gesture_id', 'unknown')
        is_correct = data.get('is_correct', False)
        confidence = data.get('confidence', 0.0)

        feedback = ai_assistant.generate_practice_feedback(
            gesture_id, is_correct, confidence
        )

        return jsonify(feedback)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 50)
    print("Gesture Recognition API Server with AI")
    print("=" * 50)
    print("Endpoints:")
    print("  GET  /api/health         - Health check")
    print("  GET  /api/gestures       - List supported gestures")
    print("  POST /api/recognize      - Recognize gesture from image")
    print("  POST /api/verify         - Verify gesture matches expected")
    print("  GET  /api/stream         - Real-time video stream")
    print("")
    print("AI Endpoints:")
    print("  POST /api/ai/chat        - Chat with AI assistant")
    print("  GET  /api/ai/explain/<id>- Get gesture explanation")
    print("  POST /api/ai/suggestion  - Get learning suggestions")
    print("  POST /api/ai/feedback    - Get practice feedback")
    print("=" * 50)
    if AI_AVAILABLE:
        print("AI Status: Available")
    else:
        print("AI Status: Not available (install dashscope)")
    print("=" * 50)
    print("Starting server on http://localhost:5001")

    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
