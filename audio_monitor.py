import sounddevice as sd
import numpy as np
import time
import librosa
import cv2
from logger import log_event


SILENCE_THRESHOLD = 0.01
VOICE_THRESHOLD = 0.05
ABSENCE_TIME = 10
BREATHING_FREQ_MIN = 0.2  # 12 breaths/min = 0.2 Hz
BREATHING_FREQ_MAX = 0.5  # 30 breaths/min = 0.5 Hz


class AudioMonitor:
    def __init__(self):
        self.last_voice_time = time.time()
        self.last_presence_time = time.time()
        self.previous_state = None
        self.running = True
        self.absence_counter = 0

        # Face detection setup
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.cap = cv2.VideoCapture(0)

    # --------------------------
    # FACE DETECTION
    # --------------------------
    def detect_face(self, frame=None):
        """Detect face in provided frame or from camera"""
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            ret, frame = self.cap.read()
            if not ret:
                return False
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return len(faces) > 0

    # --------------------------
    # BREATHING PATTERN DETECTION
    # --------------------------
    def detect_breathing_pattern(self, audio, sr=16000):
        """Detect if breathing pattern is present in audio"""
        try:
            # Detect low-frequency energy patterns (breathing is 0.2-0.5 Hz)
            onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
            
            if len(onset_env) < 10:
                return False
                
            # Look for periodic low-frequency components
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=2)
            
            # Breathing produces consistent low-frequency patterns
            # Check if there's periodic activity in the lowest coefficients
            lpf = librosa.feature.chroma_cqt(y=audio, sr=sr)
            periodicity = np.std(lpf[0]) / (np.mean(np.abs(lpf[0])) + 1e-5)
            
            return periodicity > 0.3
        except:
            return False

    # --------------------------
    # AUDIO + BREATHING DETECTION (ENHANCED)
    # --------------------------
    def detect_audio(self, frame=None):
        """Detect audio patterns and presence with enhanced breathing detection"""
        duration = 2
        sample_rate = 16000

        try:
            recording = sd.rec(int(duration * sample_rate),
                               samplerate=sample_rate,
                               channels=1,
                               dtype='float32')
            sd.wait()
        except:
            return "AUDIO_ERROR"

        audio = recording.flatten()
        
        if len(audio) == 0:
            return "NO_AUDIO"

        volume = np.sqrt(np.mean(audio**2))

        try:
            spectral_centroid = np.mean(
                librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
            )
            zero_crossings = np.mean(
                librosa.feature.zero_crossing_rate(audio)
            )
        except:
            spectral_centroid = 0
            zero_crossings = 0

        # Get face detection from provided frame or camera
        face_present = self.detect_face(frame)

        # --------------------------
        # PRESENCE CHECK (Face + Any Audio)
        # --------------------------
        if face_present:
            self.absence_counter = 0
            self.last_presence_time = time.time()
            
            # --------------------------
            # BREATHING DETECTION (Low volume + face)
            # --------------------------
            if volume < VOICE_THRESHOLD:
                breathing_detected = self.detect_breathing_pattern(audio, sample_rate)
                if breathing_detected:
                    current_state = "BREATHING_DETECTED"
                else:
                    current_state = "SILENCE"
            
            # --------------------------
            # BACKGROUND VOICE
            # --------------------------
            elif spectral_centroid > 3000 and zero_crossings > 0.1:
                current_state = "BACKGROUND_VOICE"
                self.last_voice_time = time.time()

            # --------------------------
            # NORMAL TALKING
            # --------------------------
            else:
                current_state = "TALKING"
                self.last_voice_time = time.time()
        
        else:
            # --------------------------
            # ABSENCE DETECTION (No face detected)
            # --------------------------
            self.absence_counter += 1
            
            if self.absence_counter > 3:  # 3 checks = ~6 seconds
                current_state = "CANDIDATE_ABSENT"
            else:
                current_state = "FACE_NOT_VISIBLE"

        # Log state changes
        if current_state != self.previous_state:
            log_event(current_state)
            self.previous_state = current_state

        return current_state

    # --------------------------
    # START MONITORING
    # --------------------------
    def start_monitoring(self):
        print("🎤🎥 Smart Proctoring Started...")
        print("Press Ctrl+C to stop.\n")

        try:
            while self.running:
                status = self.detect_audio()
                print("Status:", status)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Monitoring Stopped.")
            self.cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    monitor = AudioMonitor()
    monitor.start_monitoring()

