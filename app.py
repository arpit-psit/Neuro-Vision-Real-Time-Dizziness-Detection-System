import streamlit as st
import cv2
import mediapipe as mp
import pygame
import time
from scipy.spatial import distance as dist
import math

st.set_page_config(page_title="AI Driver Monitoring System", layout="wide")

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "logged_in": False,
    "camera_on": False,
    "alarm_on": False,
    "sleep_time": 2,
    "closed_start": None,
    "total_closed_time": 0,
    "session_start": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- LOGIN ----------------
def login(user, pwd):
    if user == "admin" and pwd == "1234":
        st.session_state.logged_in = True
        st.rerun()
    else:
        st.error("Invalid Credentials")

# ---------------- GLASS LOGIN ----------------
if not st.session_state.logged_in:

    st.markdown("""
    <style>
    body {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
    .login-box {
        width:380px;margin:auto;margin-top:100px;padding:50px;
        backdrop-filter: blur(25px);
        background: rgba(255,255,255,0.08);
        border-radius:28px;
        border:1px solid rgba(255,255,255,0.2);
        box-shadow: 0 25px 60px rgba(0,0,0,0.6);
        text-align:center;
    }
    .title {font-size:28px;font-weight:600;color:white;}
    .subtitle {font-size:14px;color:#bcd;margin-bottom:30px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>AI Driver Monitoring</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Real-Time Drowsiness Detection</div>", unsafe_allow_html=True)

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        login(user, pwd)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
else:

    st.sidebar.title("⚙ Controls")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.camera_on = False
        st.rerun()

    st.session_state.sleep_time = st.sidebar.slider(
        "Alert if eyes closed (seconds)",
        1, 5, 2
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ START CAMERA"):
            st.session_state.camera_on = True
            st.session_state.session_start = time.time()
            st.session_state.total_closed_time = 0
            st.session_state.closed_start = None

    with col2:
        if st.button("⏹ STOP CAMERA"):
            st.session_state.camera_on = False

    st.markdown("---")

    # Circular Sleep Meter
    def circular_progress(percent):
        angle = percent * 3.6
        color = "#00ffcc" if percent < 40 else "#ffaa00" if percent < 70 else "#ff0000"
        html = f"""
        <div style="display:flex;justify-content:center;">
        <div style="
            width:150px;height:150px;border-radius:50%;
            background:conic-gradient({color} {angle}deg,#222 {angle}deg);
            display:flex;align-items:center;justify-content:center;
            font-size:28px;color:white;font-weight:bold;">
            {percent}%
        </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    frame_container = st.empty()
    meter_container = st.empty()

    if st.session_state.camera_on:

        cap = cv2.VideoCapture(0)
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True
        )

        pygame.mixer.init()
        alarm = pygame.mixer.Sound("test_alert.wav")

        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        EAR_THRESHOLD = 0.23

        def calculate_EAR(eye_points):
            A = dist.euclidean(eye_points[1], eye_points[5])
            B = dist.euclidean(eye_points[2], eye_points[4])
            C = dist.euclidean(eye_points[0], eye_points[3])
            return (A + B) / (2.0 * C)

        while st.session_state.camera_on:

            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            alert_active = False

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    h, w, _ = frame.shape
                    leftEye, rightEye = [], []

                    for idx in LEFT_EYE:
                        x = int(face_landmarks.landmark[idx].x * w)
                        y = int(face_landmarks.landmark[idx].y * h)
                        leftEye.append((x, y))

                    for idx in RIGHT_EYE:
                        x = int(face_landmarks.landmark[idx].x * w)
                        y = int(face_landmarks.landmark[idx].y * h)
                        rightEye.append((x, y))

                    ear = (calculate_EAR(leftEye) + calculate_EAR(rightEye)) / 2.0

                    if ear < EAR_THRESHOLD:
                        if st.session_state.closed_start is None:
                            st.session_state.closed_start = time.time()

                        elapsed = time.time() - st.session_state.closed_start

                        if elapsed >= st.session_state.sleep_time:
                            alert_active = True
                            cv2.putText(frame, "🚨 DROWSINESS ALERT!",
                                        (20, 80),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        1, (0, 0, 255), 3)

                            if not st.session_state.alarm_on:
                                alarm.play(loops=-1)
                                st.session_state.alarm_on = True
                    else:
                        if st.session_state.closed_start is not None:
                            st.session_state.total_closed_time += (
                                time.time() - st.session_state.closed_start
                            )
                        st.session_state.closed_start = None
                        if st.session_state.alarm_on:
                            alarm.stop()
                            st.session_state.alarm_on = False

            # Red glow overlay
            if alert_active:
                overlay = frame.copy()
                cv2.rectangle(overlay, (0,0), (frame.shape[1], frame.shape[0]),
                              (0,0,255), -1)
                cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

            total_session = time.time() - st.session_state.session_start

            if total_session > 0:
                sleep_percent = int(
                    (st.session_state.total_closed_time / total_session) * 100
                )
                sleep_percent = min(sleep_percent, 100)
                meter_container.empty()
                with meter_container:
                    circular_progress(sleep_percent)

            frame_container.image(frame, channels="BGR")

        cap.release()
