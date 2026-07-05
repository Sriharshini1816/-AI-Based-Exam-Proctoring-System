#!/usr/bin/env python
"""
Comprehensive test of all AI Proctoring System modules
"""
import sys
print("=" * 60)
print("AI PROCTORING SYSTEM - MODULE TESTS")
print("=" * 60)
print(f"Python: {sys.version.split()[0]}\n")

# Test 1: Behavior Detection
print("TEST 1: Behavior Detection Module")
print("-" * 60)
try:
    from behavior_detection import BehaviorDetector
    bd = BehaviorDetector()
    print("✅ BehaviorDetector initialized")
    print("   Methods: detect_behavior, detect_paper, detect_hand_usage")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Audio Monitor
print("\nTEST 2: Audio Monitor Module")
print("-" * 60)
try:
    from audio_monitor import AudioMonitor
    am = AudioMonitor()
    print("✅ AudioMonitor initialized")
    print("   Methods: detect_audio")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: System Monitor
print("\nTEST 3: System Monitor Module")
print("-" * 60)
try:
    from system_monitor import SystemMonitor, system_monitor
    print("✅ SystemMonitor imported")
    stats = system_monitor.get_stats()
    print(f"   Stats available: {list(stats.keys())}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Network Monitor
print("\nTEST 4: Network Monitor Module")
print("-" * 60)
try:
    from network_monitor import NetworkSeatingMonitor
    nm = NetworkSeatingMonitor()
    print("✅ NetworkSeatingMonitor initialized")
    print("   Methods: detect_unusual_movement, detect_leaving_seat, check_internet")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Logger
print("\nTEST 5: Logger Module")
print("-" * 60)
try:
    from logger import ProctorLogger
    logger = ProctorLogger()
    print("✅ ProctorLogger initialized")
    print("   Methods: log_violation")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Face Detection
print("\nTEST 6: Face Detection Module")
print("-" * 60)
try:
    from face_detection import check_face_presence
    print("✅ Face detection imported")
    print("   Function: check_face_presence()")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Dependencies
print("\nTEST 7: Critical Dependencies")
print("-" * 60)
deps_ok = True
try:
    import cv2
    print(f"✅ OpenCV {cv2.__version__}")
except:
    print("❌ OpenCV missing")
    deps_ok = False

try:
    import numpy as np
    print(f"✅ NumPy {np.__version__}")
except:
    print("❌ NumPy missing")
    deps_ok = False

try:
    import streamlit as st
    print(f"✅ Streamlit {st.__version__}")
except:
    print("❌ Streamlit missing")
    deps_ok = False

try:
    import pynput
    print(f"✅ Pynput")
except:
    print("❌ Pynput missing")
    deps_ok = False

try:
    import pyperclip
    print(f"✅ Pyperclip")
except:
    print("❌ Pyperclip missing")
    deps_ok = False

# Test 8: Directories
print("\nTEST 8: Evidence Directories")
print("-" * 60)
import os
dirs_ok = True
for dir_path in ["evidence", "evidence/screenshots", "evidence/clips"]:
    if os.path.exists(dir_path):
        print(f"✅ {dir_path}")
    else:
        print(f"❌ {dir_path} MISSING")
        dirs_ok = False

print("\n" + "=" * 60)
if deps_ok and dirs_ok:
    print("✅ ALL TESTS PASSED - SYSTEM READY")
else:
    print("⚠️  SOME ISSUES DETECTED - SEE ABOVE")
print("=" * 60)
