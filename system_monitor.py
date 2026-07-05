"""
System-level monitoring for:
- Mouse clicks
- Copy/Paste operations
- Tab switching
- Keyboard activity
"""

import threading
import time
from datetime import datetime
from collections import defaultdict
import subprocess
import sys

try:
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("⚠️ pynput not installed - system monitoring disabled")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    print("⚠️ pyperclip not installed - clipboard monitoring disabled")

try:
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️ win32gui not installed - window monitoring limited")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not installed - process monitoring limited")


class SystemMonitor:
    """Monitor system-level events (mouse, keyboard, clipboard, windows)"""
    
    def __init__(self):
        self.mouse_clicks = 0
        self.copy_paste_count = 0
        self.tab_switches = 0
        self.keyboard_presses = defaultdict(int)
        self.last_clipboard = ""
        self.clipboard_change_time = 0
        
        # Control flag
        self.monitoring = False
        self.threads = []
        
        # Detect copy/paste key combinations
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        self.last_ctrl_c_time = 0
        self.last_ctrl_v_time = 0
        self.ctrl_c_presses = 0
        self.ctrl_v_presses = 0
        
        # Window/tab switching tracking
        self.last_window = None
        self.last_window_check = time.time()
        self.browser_keywords = ['Chrome', 'Firefox', 'Edge', 'Safari', 'localhost', 'localhost:8501', '127.0.0.1']
        
    # ==================== MOUSE MONITORING ==================== #
    def _on_click(self, x, y, button, pressed):
        """Track mouse clicks"""
        if pressed:  # Only count when button is pressed
            self.mouse_clicks += 1
            
    def _start_mouse_monitor(self):
        """Run mouse listener in background thread"""
        try:
            if not PYNPUT_AVAILABLE:
                return
                
            listener = mouse.Listener(on_click=self._on_click)
            listener.start()
            self.threads.append(listener)
            print("✅ Mouse monitoring started")
        except Exception as e:
            print(f"❌ Mouse monitoring error: {e}")

    # ==================== KEYBOARD MONITORING ==================== #
    def _on_press(self, key):
        """Track keyboard presses, especially Ctrl+C and Ctrl+V"""
        try:
            # Detect modifier keys
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift:
                self.shift_pressed = True
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = True
                
            # Detect Ctrl+C (Copy)
            if self.ctrl_pressed:
                try:
                    if hasattr(key, 'char') and key.char == 'c':
                        current_time = time.time()
                        if current_time - self.last_ctrl_c_time > 0.3:  # Debounce
                            self.ctrl_c_presses += 1
                            self.copy_paste_count += 1
                            self.last_ctrl_c_time = current_time
                            print(f"🔴 COPY detected (Total: {self.copy_paste_count})")
                            
                    # Detect Ctrl+V (Paste)
                    elif hasattr(key, 'char') and key.char == 'v':
                        current_time = time.time()
                        if current_time - self.last_ctrl_v_time > 0.3:  # Debounce
                            self.ctrl_v_presses += 1
                            self.copy_paste_count += 1
                            self.last_ctrl_v_time = current_time
                            print(f"🔴 PASTE detected (Total: {self.copy_paste_count})")
                            
                    # Detect Ctrl+X (Cut)
                    elif hasattr(key, 'char') and key.char == 'x':
                        current_time = time.time()
                        if current_time - self.last_ctrl_c_time > 0.3:
                            self.copy_paste_count += 1
                            print(f"🔴 CUT detected (Total: {self.copy_paste_count})")
                except:
                    pass
                    
        except AttributeError:
            pass
            
    def _on_release(self, key):
        """Track when modifier keys are released"""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == keyboard.Key.shift:
                self.shift_pressed = False
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = False
        except:
            pass
            
    def _start_keyboard_monitor(self):
        """Run keyboard listener in background thread"""
        try:
            if not PYNPUT_AVAILABLE:
                return
                
            listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            listener.start()
            self.threads.append(listener)
            print("✅ Keyboard monitoring started")
        except Exception as e:
            print(f"❌ Keyboard monitoring error: {e}")

    # ==================== CLIPBOARD MONITORING ==================== #
    def _monitor_clipboard(self):
        """Monitor clipboard changes to detect copy/paste via GUI"""
        while self.monitoring:
            try:
                if not PYPERCLIP_AVAILABLE:
                    time.sleep(1)
                    continue
                    
                current_clipboard = pyperclip.paste()
                
                # Compare with last clipboard content
                if current_clipboard != self.last_clipboard and len(current_clipboard) > 0:
                    self.copy_paste_count += 1
                    print(f"📋 Clipboard change detected (Total: {self.copy_paste_count})")
                    self.last_clipboard = current_clipboard
                    self.clipboard_change_time = time.time()
                    
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                print(f"⚠️ Clipboard monitoring error: {e}")
                time.sleep(1)

    def _start_clipboard_monitor(self):
        """Run clipboard monitor in background thread"""
        try:
            thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
            thread.start()
            self.threads.append(thread)
            print("✅ Clipboard monitoring started")
        except Exception as e:
            print(f"❌ Clipboard monitoring error: {e}")

    # ==================== TAB SWITCHING DETECTION (IMPROVED) ==================== #
    def _monitor_active_window(self):
        """Monitor window focus changes to detect tab/app switching"""
        last_window = None
        last_switch_time = time.time()
        switch_logged = False
        
        while self.monitoring:
            try:
                if WIN32_AVAILABLE:
                    try:
                        hwnd = win32gui.GetForegroundWindow()
                        current_window = win32gui.GetWindowText(hwnd)
                        
                        # Current time
                        current_time = time.time()
                        
                        # Real window switch detected
                        if current_window and last_window is not None:
                            if current_window != last_window:
                                # Simple debounce: wait 0.2 seconds
                                if current_time - last_switch_time > 0.2 and not switch_logged:
                                    # Increment counter for ANY window switch
                                    self.tab_switches += 1
                                    last_switch_time = current_time
                                    switch_logged = True
                                    
                                    # Log the switch
                                    from_name = last_window[:50] if last_window else "Unknown"
                                    to_name = current_window[:50] if current_window else "Unknown"
                                    print(f"🔴 TAB SWITCH #{self.tab_switches} | From: '{from_name}' To: '{to_name}'")
                        
                        # Update window reference only after switch is logged
                        if current_window and current_window != last_window:
                            last_window = current_window
                            switch_logged = False  # Reset for next switch
                        
                    except Exception as e:
                        pass
                        
                time.sleep(0.15)  # Check every 150ms for faster response
                
            except Exception as e:
                print(f"⚠️ Window monitoring error: {e}")
                time.sleep(1)

    def _start_window_monitor(self):
        """Run window monitor in background thread"""
        try:
            thread = threading.Thread(target=self._monitor_active_window, daemon=True)
            thread.start()
            self.threads.append(thread)
            print("✅ Window/Tab monitoring started")
        except Exception as e:
            print(f"⚠️ Window monitoring may not be fully available: {e}")

    # ==================== MAIN CONTROL ==================== #
    def start_monitoring(self):
        """Start all system monitoring"""
        if self.monitoring:
            print("⚠️ Monitoring already active")
            return
            
        self.monitoring = True
        print("🎯 Starting system monitoring...")
        
        # Start all monitors
        self._start_mouse_monitor()
        self._start_keyboard_monitor()
        self._start_clipboard_monitor()
        self._start_window_monitor()
        
        print("✅ All system monitors activated")
        
    def stop_monitoring(self):
        """Stop all system monitoring"""
        self.monitoring = False
        print("⏹️ Monitoring stopped")
        
    def get_stats(self):
        """Get current statistics"""
        return {
            "mouse_clicks": self.mouse_clicks,
            "copy_paste_attempts": self.copy_paste_count,
            "tab_switches": self.tab_switches,
            "ctrl_c_presses": self.ctrl_c_presses,
            "ctrl_v_presses": self.ctrl_v_presses,
        }
        
    def reset_stats(self):
        """Reset all counters"""
        self.mouse_clicks = 0
        self.copy_paste_count = 0
        self.tab_switches = 0
        self.ctrl_c_presses = 0
        self.ctrl_v_presses = 0


# Global instance
system_monitor = SystemMonitor()


if __name__ == "__main__":
    # Test the monitor
    monitor = SystemMonitor()
    monitor.start_monitoring()
    
    print("\n🔍 Monitoring active. Test your actions...")
    print("- Click your mouse")
    print("- Press Ctrl+C (Copy)")
    print("- Press Ctrl+V (Paste)")
    print("- Switch browser tabs or applications")
