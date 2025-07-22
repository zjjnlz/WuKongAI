import time
import pygetwindow as gw
import dxcam
import ctypes
import cv2
import numpy as np

# 黑神话悟空的窗口标题
GAME_TITLE = "b1  "

# 窗口偏移修正值
TITLE_BAR_HEIGHT = 84  # 标题栏高度 + 上边框
LEFT_BORDER = 11       # 左边框宽度
RIGHT_BORDER = 11      # 右边框宽度
BOTTOM_BORDER = 50     # 下边框高度

# 黑边检测参数
BLACK_THRESHOLD = 30   # 像素值低于此值被视为黑色
BLACK_PERCENTAGE = 0.9 # 一行/列中黑色像素比例超过此值被视为黑边

def disable_dpi_awareness():
    """禁用DPI感知，强制使用逻辑坐标"""
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
    except Exception as e:
        print(f"禁用DPI感知时出错: {e}")

def activate_and_top_window(hwnd):
    """激活窗口并将其置顶"""
    user32 = ctypes.windll.user32
    user32.ShowWindow(hwnd, 5)  # SW_SHOW
    user32.SetForegroundWindow(hwnd)
    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001)  # SWP_NOMOVE | SWP_NOSIZE
    time.sleep(0.5)

def remove_black_borders(image):
    """消除图像上下的黑边"""
    if image is None or len(image) == 0:
        return None
    
    height, width = image.shape[:2]
    
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 计算每一行的黑色像素比例
    row_black_percentage = np.sum(gray < BLACK_THRESHOLD, axis=1) / width
    
    # 找到顶部黑边的结束位置
    top = 0
    for i in range(height):
        if row_black_percentage[i] < BLACK_PERCENTAGE:
            top = i
            break
    
    # 找到底部黑边的开始位置
    bottom = height - 1
    for i in range(height - 1, -1, -1):
        if row_black_percentage[i] < BLACK_PERCENTAGE:
            bottom = i
            break
    
    # 裁剪图像
    if top < bottom:
        cropped = image[top:bottom+1, :]
        print(f"消除黑边: 顶部裁剪 {top} 像素, 底部裁剪 {height - bottom - 1} 像素")
        return cropped
    else:
        print("未检测到黑边或图像全部为黑色")
        return image

def capture_and_save_game_screenshot():
    try:
        # 禁用DPI感知，获取逻辑坐标
        disable_dpi_awareness()
        
        # 获取游戏窗口
        game_window = gw.getWindowsWithTitle(GAME_TITLE)[0]
        
        # 获取窗口句柄
        hwnd = game_window._hWnd
        
        # 激活并置顶窗口
        activate_and_top_window(hwnd)
        
        # 获取窗口的逻辑坐标
        left, top = game_window.topleft
        right, bottom = game_window.bottomright
        
        # 获取屏幕分辨率
        screen_width = 2560
        screen_height = 1600
        
        # 应用固定偏移
        adjusted_left = max(0, left + LEFT_BORDER)
        adjusted_top = max(0, top + TITLE_BAR_HEIGHT)
        adjusted_right = min(screen_width, right - RIGHT_BORDER)
        adjusted_bottom = min(screen_height, bottom - BOTTOM_BORDER)
        
        print(f"游戏窗口原始逻辑坐标: {game_window.left}, {game_window.top}, {game_window.right}, {game_window.bottom}")
        print(f"调整后的逻辑坐标: {adjusted_left}, {adjusted_top}, {adjusted_right}, {adjusted_bottom}")
        print(f"应用的固定偏移量: 左={LEFT_BORDER}, 上={TITLE_BAR_HEIGHT}, 右={RIGHT_BORDER}, 下={BOTTOM_BORDER}")
        
        # 初始化屏幕捕获器
        camera = dxcam.create()
        
        # 捕获窗口区域的画面
        frame = camera.grab(region=(adjusted_left, adjusted_top, adjusted_right, adjusted_bottom))
        
        # 取消窗口置顶
        user32 = ctypes.windll.user32
        user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0002 | 0x0001)
        
        if frame is not None:
            # 转换为OpenCV格式
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            
            # 消除黑边
            processed_frame = remove_black_borders(frame)
            
            # 保存截图
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            save_path = f"./game_screenshots/screenshot_{timestamp}.png"
            cv2.imwrite(save_path, processed_frame)
            
            print(f"截图已保存至: {save_path}")
            print(f"原始截图尺寸: {frame.shape[1]}x{frame.shape[0]}")
            print(f"处理后截图尺寸: {processed_frame.shape[1]}x{processed_frame.shape[0]}")
        else:
            print("未能捕获到画面。")
            
    except IndexError:
        print(f"未找到标题为 '{GAME_TITLE}' 的窗口。")
    except ValueError as e:
        print(f"区域错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    capture_and_save_game_screenshot()