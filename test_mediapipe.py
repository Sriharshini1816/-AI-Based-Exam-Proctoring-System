import sys
import mediapipe as mp

print(f"MediaPipe version: {mp.__version__}")
print(f"Python version: {sys.version}")

# Try to find solutions
try:
    from mediapipe import solutions
    print("✅ mediapipe.solutions found")
except ImportError as e:
    print(f"❌ mediapipe.solutions not found: {e}")

# Try alternative import
try:
    from mediapipe.tasks import vision
    print("✅ mediapipe.tasks.vision found")
except ImportError as e:
    print(f"❌ mediapipe.tasks.vision not found: {e}")

# List available attributes
print("\nAvailable in mp:", [x for x in dir(mp) if not x.startswith('_')])
