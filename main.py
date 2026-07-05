import streamlit as st
import cv2
from datetime import datetime
import pyautogui
import time
import threading
import os
from collections import defaultdict

from behavior_detection import BehaviorDetector
from audio_monitor import AudioMonitor
from network_monitor import NetworkSeatingMonitor
from logger import ProctorLogger
from system_monitor import system_monitor


# ============= ENSURE EVIDENCE DIRECTORIES EXIST =============
def setup_evidence_directories():
    """Create evidence directories if they don't exist"""
    os.makedirs("evidence/screenshots", exist_ok=True)
    os.makedirs("evidence/clips", exist_ok=True)
    print("✅ Evidence directories created/verified")

# Setup directories on app start
setup_evidence_directories()


# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="AI Smart Proctoring", layout="wide")
st.title("🧠 AI-Based Exam Proctoring System")
st.markdown("### Real-Time Smart Monitoring Dashboard")

# ---------------- INITIALIZE MODULES ---------------- #
detector = BehaviorDetector()
audio_monitor = AudioMonitor()
network_monitor = NetworkSeatingMonitor()
logger = ProctorLogger()

# ---------------- SESSION STATES - VIOLATIONS TRACKING ---------------- #
if "exam_started" not in st.session_state:
    st.session_state.exam_started = False

if "violations" not in st.session_state:
    st.session_state.violations = 0

if "violation_list" not in st.session_state:
    st.session_state.violation_list = []

if "last_reason" not in st.session_state:
    st.session_state.last_reason = None

if "cap" not in st.session_state:
    st.session_state.cap = None

# Analytics tracking
if "analytics" not in st.session_state:
    st.session_state.analytics = {
        "violation_counts": defaultdict(int),
        "mouse_clicks": 0,
        "copy_paste_attempts": 0,
        "tab_switches": 0,
        "inactivity_periods": 0,
        "start_time": None,
        "suspicious_events": []
    }

# Browser-level monitoring flags
if "browser_events" not in st.session_state:
    st.session_state.browser_events = []

# Keyboard tracking for paste detection
if "last_key_time" not in st.session_state:
    st.session_state.last_key_time = time.time()

# Screenshot function with timestamp and error handling
def capture_screenshot():
    """Capture screenshot with timestamp for evidence"""
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Better timestamp format
        path = f"evidence/screenshots/SCR_{ts}.png"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Capture screenshot
        pyautogui.screenshot(path)
        print(f"✅ Screenshot captured: {path}")
        return path
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        return None

# Detailed violation logging
def log_detailed_violation(reason, evidence_path=None):
    """Log violations with detailed tracking"""
    timestamp = datetime.now().isoformat(timespec='milliseconds')
    
    violation_entry = {
        "timestamp": timestamp,
        "reason": reason,
        "evidence": evidence_path,
        "severity": "🔴 CRITICAL" if any(x in reason for x in ["Phone", "Call", "Device", "Multiple", "Face Not", "Left Seat", "Internet"]) else ("🟠 HIGH" if any(x in reason for x in ["Copy", "Paste", "Tab", "Looking Away", "Paper"]) else "🟡 MEDIUM")
    }
    
    st.session_state.violation_list.append(violation_entry)
    st.session_state.analytics["violation_counts"][reason] += 1
    st.session_state.analytics["suspicious_events"].append({
        "time": timestamp,
        "event": reason
    })
    logger.log_violation(reason, evidence_path)

# JavaScript-based browser monitoring (injected into Streamlit)
def inject_browser_monitor():
    """Inject browser tab switching and copy/paste detection"""
    st.components.v1.html(
        """
        <script>
        // Tab switch detection
        document.addEventListener("visibilitychange", function() {
            if (document.hidden) {
                const event = new Event('tabswitch');
                window.dispatchEvent(event);
            }
        });

        // Copy/Paste detection
        document.addEventListener("copy", function() {
            const event = new Event('copypaste');
            window.dispatchEvent(event);
        });
        
        document.addEventListener("paste", function() {
            const event = new Event('copypaste');
            window.dispatchEvent(event);
        });
        
        document.addEventListener("cut", function() {
            const event = new Event('copypaste');
            window.dispatchEvent(event);
        });
        </script>
        """,
        height=0
    )

# Inject browser monitoring when exam starts
if st.session_state.exam_started:
    inject_browser_monitor()

# ---------------- START EXAM BUTTON ---------------- #
if not st.session_state.exam_started:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎬 Start Exam", key="start_exam_btn", use_container_width=True):
            st.session_state.exam_started = True
            st.session_state.cap = cv2.VideoCapture(0)
            st.session_state.analytics["start_time"] = datetime.now()
            
            # Start system monitoring
            system_monitor.start_monitoring()
            
            if not st.session_state.cap.isOpened():
                st.error("❌ Cannot access the camera")
            else:
                st.success("✅ Exam Started. All Monitoring Activated.")
                st.info("📹 Camera, 🎤 Audio, ⌨️ Keyboard, 🖱️ Mouse, 🌐 Network, and 📑 Browser all being monitored.")

# Show exam duration
if st.session_state.exam_started and st.session_state.analytics["start_time"]:
    elapsed = datetime.now() - st.session_state.analytics["start_time"]
    st.markdown(f"#### ⏱️ Exam Duration: `{str(elapsed).split('.')[0]}`")

# ==================== EXAM MONITOR ==================== #
if st.session_state.exam_started:
    
    # Layout: Video on left, dashboard on right
    col_video, col_dash = st.columns([3, 2])

    with col_video:
        frame_window = st.empty()

    with col_dash:
        st.subheader("📊 Live Monitoring")
        status_box = st.empty()
        violation_counter = st.empty()
        last_violation_box = st.empty()
        internet_box = st.empty()
        audio_box = st.empty()
        
        # Analytics mini-dashboard
        with st.expander("📈 Analytics", expanded=True):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.metric("🚨 Total Violations", st.session_state.violations)
                st.metric("🖱️ Mouse Clicks", st.session_state.analytics["mouse_clicks"])
            with col_a2:
                st.metric("📋 Copy/Paste Attempts", st.session_state.analytics["copy_paste_attempts"])
                st.metric("📑 Tab Switches", st.session_state.analytics["tab_switches"])

    # Submit button
    col_submit_left, col_submit_right = st.columns([3, 2])
    with col_submit_right:
        if st.button("✅ Submit Exam", key="submit_exam_btn", use_container_width=True):
            st.warning("Exam Submitted Successfully")
            st.session_state.exam_started = False
            if st.session_state.cap:
                st.session_state.cap.release()
            # Stop system monitoring
            system_monitor.stop_monitoring()
            st.info("📊 View the report below.")

    # Horizontal line separator
    st.divider()

    # ============ MAIN DETECTION LOOP ============
    ret, frame = st.session_state.cap.read()
    
    if not ret:
        st.error("❌ Camera access lost")
    else:
        suspicious = False
        reason = "Normal"
        evidence_path = None

        # -------- 1. BEHAVIOR DETECTION -------- #
        behavior_flag, behavior_reason = detector.detect_behavior(frame)
        if behavior_flag:
            suspicious = True
            reason = behavior_reason
            # Specifically track phone use and suspicious objects
            if any(x in behavior_reason for x in ["Phone", "Call", "Device", "Suspicious Object"]):
                log_detailed_violation(reason, capture_screenshot())
                print(f"🔴 CRITICAL: {reason} detected!")
            # Always log talking separately
            if "Talking" in behavior_reason:
                print(f"🎤 Talking detected")
        
        # Debug: Show detection status
        if not behavior_flag:
            # print(f"[DEBUG] Behavior: Normal")  # Uncomment for full debugging
            pass


        # -------- 2. AUDIO MONITORING (with frame) -------- #
        audio_status = audio_monitor.detect_audio(frame)
        audio_box.info(f"🎤 Audio: {audio_status}")
        
        # Suspicious audio patterns
        if audio_status in ["TALKING", "BACKGROUND_VOICE"]:
            suspicious = True
            reason = audio_status
        elif audio_status == "CANDIDATE_ABSENT":
            suspicious = True
            reason = "Candidate Left Seat"

        # -------- 3. SYSTEM MONITORING (Mouse, Keyboard, Copy/Paste, Tab Switch) -------- #
        system_stats = system_monitor.get_stats()
        st.session_state.analytics["mouse_clicks"] = system_stats["mouse_clicks"]
        st.session_state.analytics["copy_paste_attempts"] = system_stats["copy_paste_attempts"]
        st.session_state.analytics["tab_switches"] = system_stats["tab_switches"]
        
        # Check for suspicious copy/paste patterns
        if system_stats["copy_paste_attempts"] > 0 and system_stats["copy_paste_attempts"] % 3 == 0:
            if system_stats["copy_paste_attempts"] != st.session_state.get("last_copy_paste", 0):
                suspicious = True
                reason = f"Copy/Paste Detected ({system_stats['copy_paste_attempts']} attempts)"
                st.session_state["last_copy_paste"] = system_stats["copy_paste_attempts"]

        # Check for tab switching
        if system_stats["tab_switches"] > 0 and system_stats["tab_switches"] != st.session_state.get("last_tab_switch", 0):
            suspicious = True
            reason = f"📑 Tab Switch Detected (#{system_stats['tab_switches']})"
            st.session_state["last_tab_switch"] = system_stats["tab_switches"]
            print(f"🔴 ALERT: Tab switch #{system_stats['tab_switches']} detected!")
            log_detailed_violation(reason, capture_screenshot())

        # -------- 4. NETWORK & MOVEMENT -------- #
        movement_flag = network_monitor.detect_unusual_movement(frame)
        leave_flag = network_monitor.detect_leaving_seat(reason)
        internet_flag = network_monitor.check_internet()

        if movement_flag:
            suspicious = True
            reason = "Unusual Movement Detected"
        
        if leave_flag and reason == "Normal":
            suspicious = True
            reason = "Candidate Left Seat"
            
        if not internet_flag:
            suspicious = True
            reason = "Internet Connection Lost"

        # -------- 4. DISPLAY CAMERA FEED -------- #
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        color = (0, 0, 255) if suspicious else (0, 255, 0)  # Red if suspicious, Green if normal
        
        # Display text overlay
        cv2.putText(frame_rgb, reason, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        frame_window.image(frame_rgb, use_column_width=True)

        # -------- 5. INTERNET STATUS -------- #
        if internet_flag:
            internet_box.success("🌐 Connected")
        else:
            internet_box.error("🌐 Connection Lost")

        # -------- 6. VIOLATION ALERT & LOGGING -------- #
        if suspicious:
            status_box.error(f"🚨 ALERT: {reason}")
            
            # Log new/unique violations
            if reason != st.session_state.last_reason:
                st.session_state.violations += 1
                
                # Capture screenshot for evidence (if not already captured)
                if "Phone" not in reason and "Call" not in reason:  # Phone use already logged in behavior detection
                    evidence_path = capture_screenshot()
                else:
                    evidence_path = None
                    
                log_detailed_violation(reason, evidence_path)
                st.session_state.last_reason = reason
        else:
            status_box.success("✅ Normal Behavior Detected")
            st.session_state.last_reason = None

        violation_counter.metric("Current Violations", st.session_state.violations)
        last_violation_box.warning(f"Last Alert: {reason}")

    # Automatic refresh for live streaming effect
    time.sleep(1)
    st.rerun()

# ==================== REPORT SECTION ==================== #
else:
    if st.session_state.violations > 0:
        st.markdown("## 📋 Exam Report")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Violations", st.session_state.violations)
        with col2:
            st.metric("Mouse Clicks", st.session_state.analytics["mouse_clicks"])
        with col3:
            st.metric("Copy/Paste", st.session_state.analytics["copy_paste_attempts"])
        with col4:
            st.metric("Tab Switches", st.session_state.analytics["tab_switches"])

        # Violation breakdown
        st.subheader("🎯 Violation Summary")
        if st.session_state.violation_list:
            
            # Display detailed violation timeline
            st.markdown("### Violation Timeline")
            for v in reversed(st.session_state.violation_list[-15:]):
                severity_emoji = "🔴" if v["severity"] == "HIGH" else "🟡"
                st.write(f"{severity_emoji} **{v['timestamp']}** - {v['reason']}")
                if v["evidence"]:
                    st.caption(f"Evidence: {v['evidence']}")
            
            # Violation type breakdown
            st.markdown("### Violation Breakdown by Type")
            if st.session_state.analytics["violation_counts"]:
                violation_df = {
                    "Type": list(st.session_state.analytics["violation_counts"].keys()),
                    "Count": list(st.session_state.analytics["violation_counts"].values())
                }
                st.bar_chart(violation_df, x="Type", y="Count")
    else:
        st.success("✅ Exam Completed with No Violations Detected!")


