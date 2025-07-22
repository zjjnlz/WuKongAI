# WuKongAI/utils/window_utils.py
import time
import pygetwindow as gw
import ctypes

def activate_window_by_title(window_title: str) -> bool:
    """通过窗口标题激活窗口到前台"""
    try:
        # 查找游戏窗口
        game_window = gw.getWindowsWithTitle(window_title)[0]
        hwnd = game_window._hWnd
        
        # 确保窗口可见并激活
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, 5)  # SW_SHOW
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)  # 等待窗口激活
        
        return True
    except IndexError:
        print(f"未找到标题为 '{window_title}' 的窗口")
        return False
    except Exception as e:
        print(f"激活窗口失败: {e}")
        return False