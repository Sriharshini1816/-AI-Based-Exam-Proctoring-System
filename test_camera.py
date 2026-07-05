import cv2
from behavior_detection import BehaviorDetector

detector = BehaviorDetector()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    suspicious, reason = detector.detect_behavior(frame)

    color = (0,0,255) if suspicious else (0,255,0)

    cv2.putText(frame, reason, (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                color, 2)

    cv2.imshow("Test Camera", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
