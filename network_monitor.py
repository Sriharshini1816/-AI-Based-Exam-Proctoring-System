import cv2
import numpy as np
import socket
import time

class NetworkSeatingMonitor:
    def __init__(self):
        self.prev_frame = None
        self.last_internet_check = time.time()
        self.internet_status = True

    # Detect unusual movement (excessive motion)
    def detect_unusual_movement(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_frame is None:
            self.prev_frame = gray
            return False

        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_score = np.sum(thresh)

        self.prev_frame = gray

        if motion_score > 4000000:
            return True

        return False

    # Detect leaving seat (no face detected)
    def detect_leaving_seat(self, suspicious_reason):
        if suspicious_reason in ["No Face Detected", "Face Not Visible"]:
            return True
        return False

    # Check internet connection
    def check_internet(self):
        if time.time() - self.last_internet_check < 10:
            return self.internet_status

        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.internet_status = True
        except OSError:
            self.internet_status = False

        self.last_internet_check = time.time()
        return self.internet_status

    # Handle suspicious face detection
    def handle_suspicious_face(self, suspicious_reason):
        if suspicious_reason in ["No Face Detected", "Face Not Visible"]:
            print("Warning: Face not detected properly!")
