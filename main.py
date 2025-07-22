import yaml
import cv2
from env.screen_capturer import ScreenCapturer  # 修改导入路径

def main():
    # 读取配置文件
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # 获取截图配置
    screen_config = config.get('screen_capture', {})
    
    try:
        # 创建屏幕捕获器
        capturer = ScreenCapturer(
            window_title=screen_config.get('window_title', ''),
            offsets=screen_config.get('offsets', {}),
            output_size=tuple(screen_config.get('output_size')) if screen_config.get('output_size') else None,
            grayscale=screen_config.get('grayscale', False),
            black_threshold=screen_config.get('black_threshold', 30),
            black_percentage=screen_config.get('black_percentage', 0.9)
        )
        
        # 捕获截图
        screenshot = capturer.capture()
        
        if screenshot is not None:
            # 显示截图
            cv2.imshow("Game Screenshot", screenshot)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            # 保存截图
            cv2.imwrite("./game_screenshots/game_screenshot.png", screenshot)
            print("截图已保存")
            
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()