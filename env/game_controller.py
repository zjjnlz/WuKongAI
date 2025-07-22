import time
import keyboard
from typing import Dict, Optional, List

class GameController:
    def __init__(self, key_mapping: Dict[str, Optional[str]]):
        """
        初始化游戏控制器
        :param key_mapping: 动作到键盘按键的映射
        """
        self.key_mapping = key_mapping
        self.ai_control_active = False
        self.last_action_time = 0
        self.action_cooldown = 0.1  # 动作冷却时间(秒)
        self.currently_pressed_keys = []  # 跟踪当前按下的键
        
        # 注册热键释放回调
        keyboard.on_release(self._on_key_release)
    
    def _on_key_release(self, event):
        """处理按键释放事件"""
        if event.name in self.currently_pressed_keys:
            self.currently_pressed_keys.remove(event.name)
    
    def start_ai_control(self):
        """开始AI控制"""
        self.ai_control_active = True
        print("AI control started")
        print(f"AI control status: {self.ai_control_active}")  # 添加调试信息
    
    def stop_ai_control(self):
        """停止AI控制"""
        self.ai_control_active = False
        # 释放所有AI按下的键
        for key in list(self.currently_pressed_keys):
            keyboard.release(key)
            print(f"Released lingering key: {key}")
        self.currently_pressed_keys.clear()
        print("AI control stopped")
    
    def execute_action(self, action: str):
        """执行动作"""
        if not self.ai_control_active:
            return
        
        # 检查动作冷却
        current_time = time.time()
        if current_time - self.last_action_time < self.action_cooldown:
            return
        
        # 获取按键映射
        key = self.key_mapping.get(action)
        if not key:
            return
        
        # 执行按键（模拟按下和释放）
        keyboard.press(key)
        self.currently_pressed_keys.append(key)
        
        # 对于瞬时动作，立即释放
        if action == "dodge":
            keyboard.release(key)
            if key in self.currently_pressed_keys:
                self.currently_pressed_keys.remove(key)
        
        self.last_action_time = current_time
        print(f"Executed action: {action} (Key: {key})")
    
    def is_ai_control_active(self):
        """检查AI控制是否激活"""
        return self.ai_control_active
    
    def cleanup(self):
        """清理资源"""
        keyboard.unhook_all()