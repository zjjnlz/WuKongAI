import time
import pygetwindow as gw
import dxcam
import ctypes
import cv2
import numpy as np

class ScreenCapturer:
    def __init__(self, window_title: str, offsets: dict = None, output_size: tuple = None, 
                 grayscale: bool = False, black_threshold: int = 30, black_percentage: float = 0.9):
        """
        初始化屏幕捕获器
        
        参数:
            window_title: 窗口标题（精确匹配，自动去除前后空格）
            offsets: 窗口偏移配置 {left, top, right, bottom}
            output_size: 输出图像尺寸 (width, height)，None表示不调整尺寸
            grayscale: 是否转换为灰度图
            black_threshold: 黑边检测阈值
            black_percentage: 黑边检测百分比
        """
        self.window_title = window_title.strip()  # 去除前后空格
        self.offsets = offsets or {}
        self.output_size = output_size
        self.grayscale = grayscale
        self.hwnd = self._find_window_handle()
        
        if not self.hwnd:
            raise ValueError(f"Window not found: '{self.window_title}'")
            
        # 获取窗口对象
        self.window = gw.Window(self.hwnd)
        
        # 初始化屏幕捕获器
        self.camera = dxcam.create()
        
        # Windows API 常量
        self.user32 = ctypes.windll.user32
        self.SW_SHOW = 5
        self.SWP_NOMOVE = 0x0002
        self.SWP_NOSIZE = 0x0001
        
        # 黑边处理参数
        self.BLACK_THRESHOLD = black_threshold
        self.BLACK_PERCENTAGE = black_percentage
    
    def _find_window_handle(self):
        """查找游戏窗口句柄（精确匹配）"""
        try:
            # 查找所有匹配标题的窗口
            windows = [w for w in gw.getAllWindows() if w.title.strip() == self.window_title]
            return windows[0]._hWnd if windows else None
        except Exception as e:
            print(f"查找窗口时出错: {e}")
            return None
    
    def _activate_window(self):
        """激活游戏窗口到前台"""
        try:
            # 确保窗口可见
            self.user32.ShowWindow(self.hwnd, self.SW_SHOW)
            
            # 激活窗口
            self.user32.SetForegroundWindow(self.hwnd)
            
            time.sleep(0.1)  # 等待窗口激活
        except Exception as e:
            print(f"激活窗口失败: {e}")
    
    def _remove_black_borders(self, image):
        """消除图像上下的黑边"""
        if image is None or len(image) == 0:
            return None
            
        height, width = image.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算每一行的黑色像素比例
        row_black_percentage = np.sum(gray < self.BLACK_THRESHOLD, axis=1) / width
        
        # 找到顶部黑边的结束位置
        top = 0
        for i in range(height):
            if row_black_percentage[i] < self.BLACK_PERCENTAGE:
                top = i
                break
        
        # 找到底部黑边的开始位置
        bottom = height - 1
        for i in range(height - 1, -1, -1):
            if row_black_percentage[i] < self.BLACK_PERCENTAGE:
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
    
    def capture(self):
        """捕获游戏窗口截图（确保窗口可见）"""
        try:
            # 激活窗口
            self._activate_window()
            
            # 获取窗口位置
            left, top = self.window.topleft
            right, bottom = self.window.bottomright
            
            # 应用偏移
            left_offset = self.offsets.get('left', 0)
            top_offset = self.offsets.get('top', 0)
            right_offset = self.offsets.get('right', 0)
            bottom_offset = self.offsets.get('bottom', 0)
            
            # 计算捕获区域
            region_left = max(0, left + left_offset)
            region_top = max(0, top + top_offset)
            region_right = min(right, right - right_offset)
            region_bottom = min(bottom, bottom - bottom_offset)
            
            # 确保区域有效
            if region_left >= region_right or region_top >= region_bottom:
                raise ValueError("Invalid region coordinates after applying offsets")
            
            print(f"应用的偏移量: 左={left_offset}, 上={top_offset}, 右={right_offset}, 下={bottom_offset}")
            print(f"捕获区域: {region_left}, {region_top}, {region_right}, {region_bottom}")
            
            # 捕获图像
            img = self.camera.grab(region=(region_left, region_top, region_right, region_bottom))
            
            if img is not None:
                # 转换为OpenCV格式
                img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # 消除黑边
                img = self._remove_black_borders(img)
                
                # 调整大小
                if self.output_size:
                    img = cv2.resize(img, self.output_size, interpolation=cv2.INTER_AREA)
                
                # 转换为灰度图
                if self.grayscale:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                return img
            else:
                print("未能捕获到画面")
                return None
                
        except Exception as e:
            print(f"捕获截图时出错: {e}")
            return None