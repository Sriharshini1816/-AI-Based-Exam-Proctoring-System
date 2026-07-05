import mediapipe as mp
from mediapipe import tasks
from mediapipe.tasks import vision

print("=== Available in tasks ===")
print([x for x in dir(tasks) if not x.startswith('_')])

print("\n=== Available in vision ===")
print([x for x in dir(vision) if not x.startswith('_')])

# Explore vision module more
print("\n=== Exploring vision.hand_landmarker ===")
try:
    print(f"HandLandmarker: {vision.HandLandmarker}")
except:
    pass

print("\n=== Exploring vision.hand_landmarker_options ===")
try:
    print(f"HandLandmarkerOptions: {vision.HandLandmarkerOptions}")
except:
    pass
