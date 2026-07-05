"""
Quick test script for phone and tab switch detection
Run: python test_detection.py
"""

import cv2
import time
from behavior_detection import BehaviorDetector
from system_monitor import system_monitor

print("=" * 60)
print("🧪 AI PROCTOR - DETECTION TEST")
print("=" * 60)

# Test 1: Check if system_monitor can detect tab switches
print("\n1️⃣ TESTING TAB SWITCH DETECTION")
print("-" * 60)
print("Instructions: Start this test, then switch between applications")
print("(e.g., Switch to Explorer, then back to this window)")
print("Watch for 'TAB SWITCH' messages below...")
print()

system_monitor.start_monitoring()
print(f"✅ System monitor started (tab switches: {system_monitor.get_stats()['tab_switches']})")

for i in range(10):
    time.sleep(1)
    stats = system_monitor.get_stats()
    if stats['tab_switches'] > 0:
        print(f"✅ TAB SWITCHES DETECTED: {stats['tab_switches']}")
        break
    print(f"⏳ {10-i} seconds remaining... (tab switches: {stats['tab_switches']})")

system_monitor.stop_monitoring()

# Test 2: Check if phone detection works with camera
print("\n\n2️⃣ TESTING PHONE DETECTION")
print("-" * 60)
print("Instructions: Hold an object (phone, book, etc.) near your face")
print("for the next 10 seconds. Watch for '📱 Phone' messages...")
print()

detector = BehaviorDetector()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Cannot open camera!")
else:
    print("📹 Camera opened. Starting detection...")
    phone_detected = False
    
    for frame_count in range(300):  # ~10 seconds at 30fps
        ret, frame = cap.read()
        if not ret:
            print("❌ Camera error")
            break
        
        # Test phone detection  
        phone_flag, phone_reason = detector.detect_phone_usage(frame)
        
        if phone_flag:
            print(f"✅ PHONE DETECTED! Message: {phone_reason}")
            phone_detected = True
            break
        
        # Show progress
        if frame_count % 30 == 0:
            elapsed_sec = frame_count / 30
            print(f"⏳ {elapsed_sec:.0f} seconds... (status: {phone_reason if phone_reason else 'Waiting...'})")
        
        time.sleep(0.033)  # ~30fps
    
    if not phone_detected:
        print("⚠️ Phone not detected in the timeframe. Try holding an object closer to your face.")
    
    cap.release()

print("\n" + "=" * 60)
print("🧪 TEST COMPLETE")
print("=" * 60)
print("\nIf either detection didn't work, the system may need adjustment.")
print("Check the console output above for [PHONE] debug messages.")
