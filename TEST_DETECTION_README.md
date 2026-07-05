# 🧪 DETECTION TESTING GUIDE

## Quick Test

Run this command to test both phone and tab switch detection:

```bash
python test_detection.py
```

This will:
1. **Test Tab Switch Detection** (10 seconds)
   - Quickly switch to another app (Explorer, Notepad, etc.)
   - Switch back to this window
   - Should show tab switch count

2. **Test Phone Detection** (10 seconds)  
   - Hold ANY object (phone, book, tablet) near your face
   - Keep it visible in the frame
   - Should trigger phone detection alert

---

## What Was Fixed

### 1. **Phone Detection** ✅
- **HUGELY SIMPLIFIED** from 3 complex methods to 1 simple method
- Now detects ANY dark object held near face (phones are typically dark)
- Threshold: Needs only 2 consecutive frames of detection
- Much more reliable and responsive

**How it works:**
- Scans left and right sides of face area
- Looks for dark pixels (grayscale value < 80)
- If >5% of side area is very dark = phone-like object
- Triggers on 2nd consecutive frame of detection

### 2. **Tab Switch Detection** ✅
- **Simplified** to count ANY window focus change
- No longer filters by specific keywords
- Counts every single switch with sequential numbering
- Faster debounce time (0.2 seconds vs 0.3)

**How it works:**
- Monitors active window title every 150ms
- Compares current window to previous window
- If different = increment counter
- Logs result: "TAB SWITCH #1", "TAB SWITCH #2", etc.

---

## Expected Behavior

### Phone Detection
When you hold an object (phone, tablet, book) near your face:
```
[PHONE] Dark object ratio: 0.07 (frames: 1)
[PHONE] Dark object ratio: 0.08 (frames: 2)
🔴 CRITICAL: 📱 Phone/Device Detected!
📸 Screenshot captured: evidence/screenshots/SCR_...png
```

### Tab Switch Detection
When you switch to another application:
```
🔴 TAB SWITCH #1 | From: 'cmd' To: 'File Explorer'
🚨 ALERT: Tab switch #1 detected!
📸 Screenshot captured: evidence/screenshots/SCR_...png
```

---

## If Detection Still Doesn't Work

### For Phone Detection:
1. ✅ Make sure object is visible in camera frame
2. ✅ Object should be dark (phones, tablets, books all work)
3. ✅ Hold it close to your head (near face area)
4. ✅ Keep it there for at least 2 frames (~0.07 seconds)

### For Tab Switch Detection:
1. ✅ Make sure you're actually switching windows
2. ✅ Switch to a different application completely
3. ✅ Wait at least 0.2 seconds before switching back
4. ✅ The new window must have a visible title in taskbar

### Debugging:
Check console output for `[PHONE]` debug messages:
- `[PHONE] Dark object ratio: X%` = Detection is working
- If you don't see these messages = detection code might not be executing

---

## File Changes Summary

- **behavior_detection.py** - Simplified `detect_phone_usage()` 
- **system_monitor.py** - Fixed `_monitor_active_window()` for cleaner detection
- **main.py** - Better alert logging and screenshot capture
- **test_detection.py** - New test script (this file)

---

## Quick Start

1. Run test: `python test_detection.py`
2. If both work → Use main.py normally
3. If phone detection fails → Hold darker object closer
4. If tab switch fails → Try switching apps more deliberately

---

**Last Updated:** February 16, 2026
