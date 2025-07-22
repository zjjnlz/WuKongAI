import keyboard
from typing import Callable

class HotkeyListener:
    def __init__(self):
        self.listeners = {}
    
    def register_hotkey(self, hotkey: str, callback: Callable):
        """注册热键和回调函数"""
        keyboard.add_hotkey(hotkey, callback, suppress=True)
        self.listeners[hotkey] = callback
        print(f"Registered hotkey: {hotkey}")
    
    def start_listening(self):
        """开始监听热键"""
        print("Hotkey listener started. Press ESC to stop.")
        keyboard.wait('esc')
    
    def stop_listening(self):
        """停止监听并清理"""
        for hotkey in self.listeners:
            keyboard.remove_hotkey(hotkey)
        print("Hotkey listener stopped.")