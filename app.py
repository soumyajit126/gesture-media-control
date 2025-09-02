import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# ---------------- Streamlit Page Setup ----------------
st.set_page_config(page_title="OpenCV + Mediapipe Projects", layout="wide")
st.title("🎥 OpenCV + Mediapipe Live Projects")
st.sidebar.title("Choose a Project")

project = st.sidebar.selectbox(
    "Select one",
    [
        "Hand Tracking",
        "Gesture Media Control",
        "Face Detection",
        "Pose Estimation",
        "Virtual Painter",
    ],
)

# ---------------- Mediapipe Setup ----------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_face = mp.solutions.face_detection
mp_pose = mp.solutions.pose

# ---------------- Webcam ----------------
cap = cv2.VideoCapture(0)
FRAME_WINDOW = st.image([])


# ---------------- Helper Functions ----------------
def draw_hand_landmarks(frame, landmarks):
    mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)


def change_volume(delta=0.05):
    """Change system volume, positive to increase, negative to decrease"""
    try:
        if delta > 0:
            pyautogui.press("volumeup")
        else:
            pyautogui.press("volumedown")
        return True
    except:
        return False


# ---------------- Hand Tracking ----------------
def hand_tracking():
    with mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7
    ) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    draw_hand_landmarks(frame, hand_landmarks)

            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


# ---------------- Face Detection ----------------
def face_detection():
    with mp_face.FaceDetection(min_detection_confidence=0.6) as face_detector:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detector.process(rgb)

            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)

            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


# ---------------- Pose Estimation ----------------
def pose_estimation():
    with mp_pose.Pose(
        min_detection_confidence=0.6, min_tracking_confidence=0.6
    ) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


# ---------------- Virtual Painter ----------------
def virtual_painter():
    brush_color = (0, 0, 255)
    canvas = None
    with mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7
    ) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if canvas is None:
                canvas = np.zeros_like(frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    draw_hand_landmarks(frame, hand_landmarks)
                    h, w, _ = frame.shape
                    x = int(hand_landmarks.landmark[8].x * w)
                    y = int(hand_landmarks.landmark[8].y * h)
                    cv2.circle(canvas, (x, y), 8, brush_color, -1)

            frame = cv2.addWeighted(frame, 1, canvas, 0.5, 0)
            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


# ---------------- Gesture Media Control ----------------
def gesture_media_control():
    cooldown = st.sidebar.slider("Cooldown (seconds)", 0.2, 2.0, 0.8, 0.1)
    show_landmarks = st.sidebar.checkbox("Show landmarks", True)
    last_action_time = 0

    with mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1
    ) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            now = time.time()
            gesture_text = ""

            if results.multi_hand_landmarks:
                lm = results.multi_hand_landmarks[0].landmark
                fingers = []
                tip_ids = [4, 8, 12, 16, 20]
                for tip in tip_ids:
                    fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

                if show_landmarks:
                    draw_hand_landmarks(frame, results.multi_hand_landmarks[0])

                # Fist: next track
                if fingers == [0, 0, 0, 0, 0] and (now - last_action_time) > cooldown:
                    pyautogui.press("nexttrack")
                    gesture_text = "Next Track"
                    last_action_time = now

                # Open palm: play/pause
                elif fingers == [1, 1, 1, 1, 1] and (now - last_action_time) > cooldown:
                    pyautogui.press("playpause")
                    gesture_text = "Play / Pause"
                    last_action_time = now

                # Index finger up: volume control
                elif fingers == [0, 1, 0, 0, 0]:
                    if lm[8].y < lm[6].y and (now - last_action_time) > cooldown:
                        change_volume(+0.05)
                        gesture_text = "Volume Up"
                        last_action_time = now
                    elif lm[8].y > lm[6].y and (now - last_action_time) > cooldown:
                        change_volume(-0.05)
                        gesture_text = "Volume Down"
                        last_action_time = now

            if gesture_text:
                cv2.putText(
                    frame,
                    gesture_text,
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


# ---------------- Run the Selected Project ----------------
if project == "Hand Tracking":
    hand_tracking()
elif project == "Face Detection":
    face_detection()
elif project == "Pose Estimation":
    pose_estimation()
elif project == "Virtual Painter":
    virtual_painter()
elif project == "Gesture Media Control":
    gesture_media_control()
