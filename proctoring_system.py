# proctoring_system.py
import streamlit as st
import time
import threading
from pynput import keyboard, mouse

# -------------------------------
# Session state for violations
# -------------------------------
if "violations" not in st.session_state:
    st.session_state.violations = []

last_activity = time.time()

# -------------------------------
# Server-side Keyboard & Mouse Monitoring
# -------------------------------
def on_key_press(key):
    global last_activity
    last_activity = time.time()
    st.session_state.violations.append(f"Key pressed: {key}")

def on_click(x, y, button, pressed):
    global last_activity
    if pressed:
        last_activity = time.time()
        st.session_state.violations.append(f"Mouse clicked at ({x}, {y})")

def inactivity_checker():
    global last_activity
    while True:
        if time.time() - last_activity > 30:
            st.session_state.violations.append("Server inactivity >30 sec")
            last_activity = time.time()
        time.sleep(5)

# -------------------------------
# Start listeners once
# -------------------------------
if "listeners_started" not in st.session_state:
    keyboard.Listener(on_press=on_key_press).start()
    mouse.Listener(on_click=on_click).start()
    threading.Thread(target=inactivity_checker, daemon=True).start()
    st.session_state.listeners_started = True

# -------------------------------
# Page UI for monitoring browser
# -------------------------------
st.components.v1.html(
    """
    <script>
    function sendViolation(msg){
        const data = {msg: msg};
        const event = new CustomEvent('browserViolation', {detail: msg});
        window.dispatchEvent(event);
    }

    // Tab switch
    document.addEventListener("visibilitychange", function() {
        if (document.hidden) sendViolation("Tab switched");
    });

    // Window minimize/blur
    window.addEventListener("blur", function() {
        sendViolation("Window minimized");
    });

    // Copy/paste/cut
    document.addEventListener("copy", () => sendViolation("Copy detected"));
    document.addEventListener("paste", () => sendViolation("Paste detected"));
    document.addEventListener("cut", () => sendViolation("Cut detected"));

    // Inactivity
    let idle = 0;
    setInterval(() => {
        idle++;
        if(idle > 30){
            sendViolation("Browser inactive >30 sec");
            idle = 0;
        }
    }, 1000);
    document.onmousemove = document.onkeypress = () => idle = 0;
    </script>
    """,
    height=0
)
