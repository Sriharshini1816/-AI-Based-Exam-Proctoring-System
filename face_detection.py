import cv2
import time
import os

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Alternative cascade for better accuracy
face_cascade_alt = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
)

def check_face_presence(show_window=False, duration=5):
    """
    Continuously check for face presence
    
    Args:
        show_window: Whether to display camera
        duration: How long to monitor (seconds)
    
    Returns:
        bool: True if face present, False if absent
    """

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Cannot access webcam")
        return False

    face_present = False
    start_time = time.time()
    face_frames = 0
    total_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1
        
        # Resize frame for faster processing
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # Primary cascade
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # If no faces found, try alternative cascade
        if len(faces) == 0:
            faces = face_cascade_alt.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(50, 50)
            )

        # If at least one face detected
        if len(faces) > 0:
            face_present = True
            face_frames += 1
        else:
            face_present = False

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show camera window if enabled
        if show_window:
            status_text = f"Face Present: {face_present} | Frames: {face_frames}/{total_frames}"
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if face_present else (0, 0, 255), 2)
            cv2.imshow("Face Detection - Press Q to Exit", frame)

        # Run for specified duration
        if time.time() - start_time > duration:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Return True if face was detected in most frames
    detection_rate = face_frames / max(total_frames, 1)
    print(f"📊 Face Detection Rate: {detection_rate*100:.1f}% ({face_frames}/{total_frames} frames)")
    
    return detection_rate > 0.3  # Face present if detected in >30% of frames


# Run this file directly for testing
if __name__ == "__main__":
    print("🔍 Starting Face Detection Test...")
    print("Position your face in front of the camera")
    print("Press 'q' to exit early")
    print("-" * 40)
    
    result = check_face_presence(show_window=True, duration=10)

    if result:
        print("✅ Face Present - Detection Successful")
    else:
        print("❌ Face Not Present - No face detected")
