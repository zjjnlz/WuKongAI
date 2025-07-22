import yaml
import cv2
import time
import threading
from datetime import datetime
from env.screen_capturer import ScreenCapturer
from env.game_controller import GameController
from utils.hotkey_listener import HotkeyListener
from utils.window_utils import activate_window_by_title

class GameAI:
    def __init__(self):
        # 读取配置文件
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        # 获取配置
        screen_config = self.config.get('screen_config', {})
        self.key_mapping = self.config.get('key_mapping', {})
        self.hotkeys = self.config.get('hotkeys', {})

        # 初始化组件
        self.window_title = screen_config.get('window_title', '')
        self.capturer = ScreenCapturer(
            window_title=self.window_title,
            offsets=screen_config.get('offsets', {}),
            output_size=tuple(screen_config.get('output_size')) if screen_config.get('output_size') else None,
            grayscale=screen_config.get('grayscale', False),
            black_threshold=screen_config.get('black_threshold', 30),
            black_percentage=screen_config.get('black_percentage', 0.9)
        )

        self.controller = GameController(self.key_mapping)
        self.hotkey_listener = HotkeyListener()

        # 线程和状态
        self.ai_thread = None
        self.is_running = False

    def _ai_control_loop(self):
        """AI控制循环，在线程中运行"""
        while self.is_running:
            if self.controller.is_ai_control_active():
                self.controller.execute_action("dodge")
                time.sleep(0.2)  # 每次动作间隔
            time.sleep(0.01)  # 减少CPU占用

    def start_ai_control(self):
        """启动AI控制"""
        self.controller.start_ai_control()
        print("AI控制已启动")

    def stop_ai_control(self):
        """停止AI控制"""
        self.controller.stop_ai_control()
        print("AI控制已停止")
        self.printHotKeys()

    def take_screenshot(self):
        """拍摄并保存游戏截图"""
        screenshot = self.capturer.capture()
        if screenshot is not None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"./game_screenshots/game_screenshot_{timestamp}.png"
            cv2.imwrite(filename, screenshot)
            print(f"截图已保存到 {filename}")

    def setup_hotkeys(self):
        """设置热键监听"""
        self.hotkey_listener.register_hotkey(
            self.hotkeys.get('ai_control_start', 'ctrl+shift+a'),
            self.start_ai_control
        )
        self.hotkey_listener.register_hotkey(
            self.hotkeys.get('ai_control_stop', 'ctrl+shift+d'),
            self.stop_ai_control
        )
        self.hotkey_listener.register_hotkey(
            self.hotkeys.get('screen_capture', 'ctrl+shift+p'),
            self.take_screenshot
        )
        self.hotkey_listener.register_hotkey(
            self.hotkeys.get('exit_program', 'ctrl+shift+q'),
            self.stop
        )

    def printHotKeys(self):
        print(f"AI控制热键: {self.hotkeys.get('ai_control_start', 'ctrl+shift+a')}")
        print(f"AI控制热键: {self.hotkeys.get('ai_control_stop', 'ctrl+shift+d')}")
        print(f"截图热键: {self.hotkeys.get('screen_capture', 'ctrl+shift+p')}")
        print(f"退出程序热键: {self.hotkeys.get('exit_program', 'ctrl+shift+q')}")

    def start(self):
        # 激活游戏窗口
        if not activate_window_by_title(self.window_title):
            print("无法激活游戏窗口，程序退出")
            return

        # 设置热键
        self.setup_hotkeys()

        # 启动热键监听
        self.hotkey_listener.start_listening()

        # 启动AI控制线程
        self.is_running = True
        self.ai_thread = threading.Thread(target=self._ai_control_loop)
        self.ai_thread.daemon = True
        self.ai_thread.start()
        
        print("游戏AI已启动")
        self.printHotKeys()

        # 保持主线程运行
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.is_running = False

        if self.ai_thread and self.ai_thread.is_alive():
            self.ai_thread.join(timeout=1.0)

        self.controller.stop_ai_control()
        self.controller.cleanup()
        self.hotkey_listener.stop_listening()

        print("游戏AI已停止")

def main():
    game_ai = GameAI()
    game_ai.start()

if __name__ == "__main__":
    main()