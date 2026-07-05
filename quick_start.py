#!/usr/bin/env python
"""
Quick Start Guide for AI Proctoring System
Run this to verify everything is ready
"""

import os
import sys
from datetime import datetime

print("\n" + "="*70)
print("🧠 AI PROCTORING SYSTEM - QUICK START VERIFICATION")
print("="*70)

# Check Python version
py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print(f"\n📌 Python Version: {py_version}")
if sys.version_info.major >= 3 and sys.version_info.minor >= 11:
    print("   ✅ Compatible (Python 3.11+)")
else:
    print("   ⚠️  Consider upgrading to Python 3.11+")

# Check directories
print("\n📁 Checking Evidence Directories:")
dirs = ["evidence", "evidence/screenshots", "evidence/clips"]
all_exist = True
for d in dirs:
    if os.path.exists(d):
        print(f"   ✅ {d}")
    else:
        print(f"   ❌ {d} MISSING")
        all_exist = False

if not all_exist:
    print("\n   Creating missing directories...")
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("   ✅ Directories created")

# Check modules
print("\n🔧 Loading Core Modules:")
modules_ok = True

try:
    from behavior_detection import BehaviorDetector
    print("   ✅ BehaviorDetector")
except Exception as e:
    print(f"   ❌ BehaviorDetector: {e}")
    modules_ok = False

try:
    from audio_monitor import AudioMonitor
    print("   ✅ AudioMonitor")
except Exception as e:
    print(f"   ❌ AudioMonitor: {e}")
    modules_ok = False

try:
    from system_monitor import SystemMonitor
    print("   ✅ SystemMonitor")
except Exception as e:
    print(f"   ❌ SystemMonitor: {e}")
    modules_ok = False

try:
    from network_monitor import NetworkSeatingMonitor
    print("   ✅ NetworkMonitor")
except Exception as e:
    print(f"   ❌ NetworkMonitor: {e}")
    modules_ok = False

try:
    from logger import ProctorLogger
    print("   ✅ ProctorLogger")
except Exception as e:
    print(f"   ❌ ProctorLogger: {e}")
    modules_ok = False

# Check dependencies
print("\n📦 Checking Critical Dependencies:")
deps_ok = True

packages = {
    "cv2": "OpenCV",
    "numpy": "NumPy",
    "streamlit": "Streamlit",
    "pynput": "Pynput",
    "pyperclip": "Pyperclip",
    "sounddevice": "SoundDevice"
}

for module, name in packages.items():
    try:
        __import__(module)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} MISSING")
        deps_ok = False

# Summary
print("\n" + "="*70)
if modules_ok and deps_ok and all_exist:
    print("✅ SYSTEM READY - ALL CHECKS PASSED")
    print("\n🚀 Next Steps:")
    print("   1. Run: streamlit run main.py")
    print("   2. Open: http://localhost:8501")
    print("   3. Click 'Start Exam' button")
    print("   4. Allow camera access when prompted")
else:
    print("⚠️  SOME CHECKS FAILED - SEE ABOVE")
    print("\n🔧 Troubleshooting:")
    if not modules_ok:
        print("   • Run: pip install -r requirements.txt")
    if not deps_ok:
        print("   • Install missing packages listed above")

print("="*70 + "\n")
