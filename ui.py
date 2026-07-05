import streamlit as st
import cv2
from datetime import datetime
import pyautogui

from behavior_detection import BehaviorDetector
from audio_monitor import AudioMonitor
from network_monitor import NetworkSeatingMonitor
from logger import ProctorLogger

# ---------------- INITIALIZE MODULES ---------------- #
detector = BehaviorDetector()
audio_monitor = AudioMonitor()
network_monitor = NetworkSeatingMonitor()
logger = ProctorLogger()

st.set_page_config(page_title="AI Exam Proctoring System", layout="wide")

st.title("🧠 AI-Based Exam Proctoring System")
st.markdown("### Candidate Smart Monitoring Interface")

# ---------------- SESSION STATE ---------------- #
if "exam_started" not in st.session_state:
    st.session_state.exam_started = False

if "violation_count" not in st.session_state:
    st.session_state.violation_count = 0

if "last_reason" not in st.session_state:
    st.session_state.last_reason = None

# ---------------- EVIDENCE CAPTURE ---------------- #
def capture_screenshot():
    ts = datetime.now().strftime("%H%M%S")
    path = f"evidence/screenshots/SCR_{ts}.png"
    pyautogui.screenshot(path)
    return path

# ---------------- START EXAM ---------------- #
if st.button("Start Exam"):
    st.session_state.exam_started = True

# ================= MONITORING ================= #
if st.session_state.exam_started:

    st.success("✅ Exam Started. Monitoring Activated.")

    cap = cv2.VideoCapture(0)

    col1, col2 = st.columns([3, 1])

    with col1:
        frame_window = st.image([])

    with col2:
        st.subheader("📊 Live Status")
        status_box = st.empty()
        audio_box = st.empty()
        internet_box = st.empty()
        violation_box = st.empty()
        counter_box = st.empty()

    submit = st.button("Submit Exam")

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera error")
            break

        suspicious = False
        reason = "Normal"

        # -------- Behavior Detection -------- #
        behavior_flag, behavior_reason = detector.detect_behavior(frame)
        if behavior_flag:
            suspicious = True
            reason = behavior_reason

        # -------- Audio Monitoring -------- #
        audio_status = audio_monitor.detect_audio()
        audio_box.info(f"🎤 Audio Status: {audio_status}")

        if audio_status in ["TALKING", "BACKGROUND_VOICE"]:
            suspicious = True
            reason = audio_status

        # -------- Network Monitoring -------- #
        movement_flag = network_monitor.detect_unusual_movement(frame)
        leave_flag = network_monitor.detect_leaving_seat(behavior_reason)
        internet_flag = network_monitor.check_internet()

        if movement_flag:
            suspicious = True
            reason = "Unusual Movement"

        if leave_flag:
            suspicious = True
            reason = "Left Seat"

        if not internet_flag:
            suspicious = True
            reason = "Internet Lost"

        # -------- DISPLAY CAMERA -------- #
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame_rgb)

        # -------- INTERNET STATUS -------- #
        if internet_flag:
            internet_box.success("🌐 Internet Connected")
        else:
            internet_box.error("🌐 Internet Lost")

        # -------- ALERT SYSTEM -------- #
        if suspicious:
            status_box.error(f"🚨 {reason}")

            if reason != st.session_state.last_reason:
                st.session_state.violation_count += 1

                evidence = capture_screenshot()
                logger.log_violation(reason, evidence)

                st.session_state.last_reason = reason
        else:
            status_box.success("✅ Normal Behavior")
            st.session_state.last_reason = None

        violation_box.warning(f"⚠ Current Issue: {reason}")
        counter_box.metric("Total Violations", st.session_state.violation_count)

        if submit:
            st.info("Exam Submitted Successfully")
            break

    cap.release()
