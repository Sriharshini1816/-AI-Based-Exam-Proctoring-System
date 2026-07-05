import cv2
import numpy as np
import sounddevice as sd
import time
import os
from scipy import signal


class BehaviorDetector:

    def __init__(self):
        # Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        
        # Alternative cascade for better accuracy
        self.face_cascade_alt = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        )
        
        # Eye cascade for blink detection
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )

        self.blink_counter = 0
        self.blink_reset_time = time.time()
        self.eye_closed_frames = 0

        self.away_counter = 0
        self.away_threshold = 15
        
        self.face_present_frames = 0
        self.face_absent_frames = 0

        self.last_audio_check = time.time()
        
        # Phone detection tracking - SIMPLIFIED
        self.phone_suspicion_frames = 0
        self.phone_threshold = 2

    # 👁 Blink detection using eye cascade
    def detect_blink(self, frame):
        """Detect excessive blinking which indicates drowsiness"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return False, ""
            
        face_roi = gray[faces[0][1]:faces[0][1]+faces[0][3], 
                       faces[0][0]:faces[0][0]+faces[0][2]]
        
        eyes = self.eye_cascade.detectMultiScale(face_roi)
        
        # If no eyes detected, might be closed
        if len(eyes) < 2:
            self.eye_closed_frames += 1
            if self.eye_closed_frames > 10:  # Eyes closed for too long
                return True, "Eyes Closed - Possible Sleep/Cheating"
        else:
            self.eye_closed_frames = 0

        return False, ""

    # 👄 Talking/Mouth movement detection using contours
    def detect_talking(self, frame):
        """Detect if person is talking by analyzing mouth region"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return False, ""
        
        x, y, w, h = faces[0]
        # Estimate mouth region (lower part of face)
        mouth_region = frame[int(y + h*0.6):int(y + h), int(x + w*0.2):int(x + w*0.8)]
        
        if mouth_region.size == 0:
            return False, ""
        
        # Convert to HSV to detect skin tone changes
        hsv = cv2.cvtColor(mouth_region, cv2.COLOR_BGR2HSV)
        
        # Look for dark regions (open mouth)
        lower_mouth = np.array([0, 0, 0])
        upper_mouth = np.array([180, 255, 50])
        
        mask = cv2.inRange(hsv, lower_mouth, upper_mouth)
        
        # If significant dark area detected (open mouth)
        if np.sum(mask) > mouth_region.shape[0] * mouth_region.shape[1] * 0.15:
            return True, "Talking Detected"

        return False, ""

    # 🎤 Whisper/Voice detection
    def detect_voice(self):
        if time.time() - self.last_audio_check < 3:
            return False, ""

        self.last_audio_check = time.time()

        try:
            audio = sd.rec(int(0.2 * 16000), samplerate=16000, channels=1)
            sd.wait()
            volume = np.linalg.norm(audio)

            if volume > 10:
                return True, "Voice Detected"
        except:
            pass

        return False, ""

    # 📱 Simple, Direct Phone Detection
    def detect_phone_usage(self, frame):
        """Detect phone usage - VERY SIMPLE AND DIRECT"""
        h, w, _ = frame.shape
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Get face
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                return False, ""
            
            x, y, fw, fh = faces[0]
            face_right = x + fw
            
            # ===== ULTRA SIMPLE: Look for ANY dark object in hand regions =====
            # Left side (left hand area)
            left_side = gray[y:y+fh, max(0, x-fw):x]
            # Right side (right hand area)  
            right_side = gray[y:y+fh, face_right:min(w, face_right+fw)]
            
            # Count very dark pixels (phones are dark)
            left_dark = np.sum(left_side < 80)  # Very dark
            right_dark = np.sum(right_side < 80)
            
            # Total dark pixels in regions
            total_dark = left_dark + right_dark
            max_possible = (fh * fw) * 2  # Both sides combined
            
            dark_ratio = total_dark / (max_possible + 1)
            
            # If more than 5% of the region is very dark (phone-like)
            if dark_ratio > 0.05:
                self.phone_suspicion_frames += 1
                print(f"[PHONE] Dark object ratio: {dark_ratio:.2%} (frames: {self.phone_suspicion_frames})")
                if self.phone_suspicion_frames >= 2:
                    return True, "📱 Phone/Device Detected"
            else:
                self.phone_suspicion_frames = max(0, self.phone_suspicion_frames - 2)
            
            return False, ""
            
        except Exception as e:
            print(f"[PHONE] Detection error: {e}")
            return False, ""

    # ✋ Hand usage (kept for backward compatibility, uses phone detection) 
    def detect_hand_usage(self, frame):
        """Legacy method - redirects to phone detection"""
        return self.detect_phone_usage(frame)

    # 📄 Paper detection
    def detect_paper(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])

        mask = cv2.inRange(hsv, lower_white, upper_white)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if area > 15000:
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = w / float(h)

                if 0.7 < aspect_ratio < 1.4:
                    return True, "Paper / Notes Detected"

        return False, ""

    # 🎯 MAIN DETECTION
    def detect_behavior(self, frame):

        h, w, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # ===== DUAL CASCADE FACE DETECTION FOR RELIABILITY =====
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # If primary cascade misses, try alternative
        if len(faces) == 0:
            faces = self.face_cascade_alt.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(50, 50)
            )

        # 🚨 Multiple persons detection
        if len(faces) > 1:
            self.away_counter = 0
            return True, "Multiple Persons Detected"

        # 🚨 Face missing - track absence
        if len(faces) == 0:
            self.face_absent_frames += 1
            self.away_counter += 1

            # Quick response on first frames
            if self.face_absent_frames > self.away_threshold:
                return True, "Face Not Visible"

            return False, "Face Lost Briefly"

        # ✅ Face detected - reset counters
        self.face_absent_frames = 0
        self.away_counter = 0
        self.face_present_frames += 1

        # 🚨 Looking away detection - improved
        (x, y, fw, fh) = faces[0]
        frame_center = w / 2
        face_center = x + fw / 2
        
        # Check if face is too far left or right
        deviation = abs(frame_center - face_center) / w
        if deviation > 0.3:  # 30% deviation = looking away
            return True, "Looking Away"
        
        # Check if face is too high or too low
        face_vertical_center = y + fh / 2
        frame_vertical_center = h / 2
        vertical_deviation = abs(frame_vertical_center - face_vertical_center) / h
        if vertical_deviation > 0.35:  # Looking up/down significantly
            return True, "Looking Away"

        # 🎭 Additional behavioral analysis
        blink, msg = self.detect_blink(frame)
        if blink:
            return True, msg

        talk, msg = self.detect_talking(frame)
        if talk:
            return True, msg

        # 📱 Phone/Device detection (improved multi-method)
        phone, msg = self.detect_phone_usage(frame)
        if phone:
            return True, msg

        # 📄 Paper detection
        paper, msg = self.detect_paper(frame)
        if paper:
            return True, msg

        # 🎤 Voice detection
        voice, msg = self.detect_voice()
        if voice:
            return True, msg

        return False, "Normal"
