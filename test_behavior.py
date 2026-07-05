#!/usr/bin/env python
import sys
print("Python version:", sys.version)

print("\n1. Importing behavior_detection...")
try:
    from behavior_detection import BehaviorDetector
    print("✅ BehaviorDetector imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\n2. Initializing BehaviorDetector...")
try:
    bd = BehaviorDetector()
    print("✅ BehaviorDetector initialized successfully")
except Exception as e:
    print(f"❌ Initialization error: {e}")
    sys.exit(1)

print("\n3. Checking methods...")
print(f"   - detect_behavior: {hasattr(bd, 'detect_behavior')}")
print(f"   - detect_paper: {hasattr(bd, 'detect_paper')}")
print(f"   - detect_hand_usage: {hasattr(bd, 'detect_hand_usage')}")

print("\n✅ All tests passed!")
