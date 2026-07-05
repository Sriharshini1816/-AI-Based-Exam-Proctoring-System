# 🧠 AI-Based Exam Proctoring System - FIXES & IMPROVEMENTS

## ✅ Issues Fixed

### 1. **Person Present/Absent Detection**
   - **Problem**: Was only checking for 5 seconds, causing miss-detections
   - **Solution**: Implemented continuous dual-cascade face detection with:
     - Primary & alternative Haar Cascade classifiers for reliability
     - Improved responsiveness (15-frame threshold instead of 30)
     - Continuous frame-based tracking
   - **Result**: Accurate presence/absence detection throughout exam

### 2. **Phone & Device Detection**
   - **Problem**: Unreliable hand position logic with flawed range checks
   - **Solution**: Implemented improved detection with:
     - Skin tone analysis in upper & side regions of frame
     - Multi-pattern phone use detection (calling, texting, device on desk)
     - Frame-based suspicion tracking (5-frame confirmation)
   - **Result**: Detects phone use, suspicious hand activity, and device placement

### 3. **Screenshots Not Captured**
   - **Problem**: Evidence directories didn't exist, screenshot failures
   - **Solution**:
     - Automatic directory creation (`evidence/screenshots`, `evidence/clips`)
     - Error handling for screenshot capture
     - Better timestamp formatting (YYYY-MM-DD_HH-MM-SS_ms)
   - **Result**: Screenshots captured successfully with proper evidence trail

### 4. **Tab Switches Not Detected**
   - **Problem**: Basic window switching detection that missed browser activities
   - **Solution**: Enhanced window monitoring with:
     - Debouncing to avoid false positives
     - Browser-specific keyword detection
     - Suspicious application detection (YouTube, social media, etc.)
     - Faster polling (0.3 seconds instead of 1 second)
   - **Result**: Reliable tab/app switching detection

### 5. **MediaPipe Compatibility Issues**
   - **Problem**: MediaPipe 0.10.32 on Python 3.14 removed `solutions` API
   - **Solution**:
     - Removed MediaPipe dependency
     - Implemented OpenCV-only detection pipeline:
       - Haar Cascade for face detection
       - Contour analysis for paper/notes
       - HSV color space for mouth/hand detection
       - Eye cascade for blink detection
   - **Result**: Lightweight, no dependency conflicts, Python 3.11+ compatible

## 📊 Detection Capabilities

### Enabled Detections:
✅ **Face Presence/Absence** - Continuous dual-cascade detection  
✅ **Looking Away** - Head orientation analysis  
✅ **Multiple Persons** - More than one face in frame  
✅ **Phone Use** - Calling, texting, device positioning  
✅ **Talking** - Mouth movement analysis  
✅ **Eye Closure** - Drowsiness/cheating detection  
✅ **Paper/Notes** - Physical aids detection  
✅ **Voice** - Audio level monitoring  
✅ **Copy/Paste** - Keyboard shortcut tracking  
✅ **Mouse Clicks** - Activity monitoring  
✅ **Tab Switches** - Browser/app switching  
✅ **Internet Offline** - Connection loss detection  
✅ **Unusual Movement** - Motion-based flagging  

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python test_all_modules.py
```

Expected output:
```
✅ ALL TESTS PASSED - SYSTEM READY
```

### 3. Run the Proctoring System
```bash
streamlit run main.py
```

The system will open at `http://localhost:8501`

### 4. Start an Exam Session
- Click "🎬 Start Exam" button
- Position face in camera  
- System begins monitoring
- All activity logged with evidence capture

## 🔧 Configuration

### Adjust Detection Sensitivity
Edit `behavior_detection.py`:
- `away_threshold` - Face absence detection (default: 15 frames)
- `phone_threshold` - Phone suspicion frames (default: 5)
- `eye_closed_frames` - Eye closure limit (default: 10)

Edit `system_monitor.py`:
- Tab switch polling: change `time.sleep(0.3)` value
- Modifier key debounce: change `0.3` in keyboard monitor

## 📁 File Structure

```
AI_Proctor_Final/
├── main.py                      # Main Streamlit app
├── behavior_detection.py         # Face, hand, paper, mouth detection
├── audio_monitor.py             # Audio analysis
├── system_monitor.py            # Keyboard, mouse, clipboard monitoring
├── network_monitor.py           # Internet & movement tracking
├── face_detection.py            # Standalone face detection
├── logger.py                    # Violation logging
├── ui.py                        # UI components
├── proctoring_system.py         # System integration
├── requirements.txt             # Python dependencies
├── evidence/
│   ├── screenshots/             # Captured evidence images
│   └── clips/                   # Video clips
└── proctoring_audit_trail.csv   # Violation log
```

## 🐛 Troubleshooting

### Camera Not Working
```bash
python test_camera.py
```

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

### Permission Issues (Screenshots)
- Ensure `evidence/` folder exists and is writable
- System auto-creates on startup

### High CPU Usage
- Reduce detection frequency in respective modules
- Lower cascade detection quality (`minNeighbors`)

## 📝 Violation Log Format

```csv
timestamp,violation_type,evidence_path,severity
2024-02-16T10:30:45.123,Face Not Visible,evidence/screenshots/SCR_20240216_103045_123.png,HIGH
2024-02-16T10:31:02.456,Tab Switch Detected,,MEDIUM
2024-02-16T10:32:10.789,Copy/Paste Detected,,MEDIUM
```

## 🔒 Privacy & Security

- All data stored locally in `evidence/` folder
- Violations logged to CSV (no cloud upload)
- Camera accessed only when exam active
- System stops monitoring on exam submit

## 📌 Python Version Support

✅ Python 3.11  
✅ Python 3.12  
✅ Python 3.13  
✅ Python 3.14+  

All dependencies tested and compatible with Python 3.11+

## 📦 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| OpenCV | 4.13.0 | Face/hand detection |
| NumPy | 2.3.5 | Numerical processing |
| Streamlit | 1.54.0 | Web interface |
| Pynput | 1.8.1 | Keyboard/mouse monitoring |
| PyPerclip | 1.11.0 | Clipboard monitoring |
| SoundDevice | 0.5.5 | Audio monitoring |
| Librosa | 0.11.0 | Audio analysis |

## ⚠️ Known Limitations

- Requires webcam for face detection
- Audio monitoring requires audio device
- System monitoring requires appropriate Windows permissions
- Best results with good lighting

## 🎯 Next Steps

1. ✅ Verify module tests pass
2. ✅ Test with your camera
3. ✅ Run exam session for testing
4. ✅ Adjust sensitivity as needed
5. ✅ Monitor audit trail for issues

---

**Last Updated**: February 16, 2026  
**System Status**: ✅ Fully Operational  
**All Issues Fixed**: ✅ Yes
