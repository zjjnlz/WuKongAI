import keyboard
from typing import Callable
import time
import threading

class HotkeyListener:
    def __init__(self):
        self.listeners = {}
        self.is_listening = False
        self.listening_thread = None

    def register_hotkey(self, hotkey: str, callback: Callable):
        """注册热键和回调函数"""
        keyboard.add_hotkey(hotkey, callback, suppress=True)
        self.listeners[hotkey] = callback
        print(f"Registered hotkey: {hotkey}")

    def _listen(self):
        """内部监听方法，在线程中运行"""
        self.is_listening = True
        while self.is_listening:
            time.sleep(0.1)  # 减少 CPU 占用

    def start_listening(self):
        """开始监听热键"""
        print("Hotkey listener started.")
        self.listening_thread = threading.Thread(target=self._listen)
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def stop_listening(self):
        """停止监听并清理"""
        self.is_listening = False
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=1.0)
        for hotkey in list(self.listeners):  # 使用 list 复制一份键的列表，避免在迭代过程中修改字典
            try:
                keyboard.remove_hotkey(hotkey)
                del self.listeners[hotkey]
                print(f"Removed hotkey: {hotkey}")
            except ValueError:
                print(f"Hotkey {hotkey} was already removed or not registered properly.")
        print("Hotkey listener stopped.")