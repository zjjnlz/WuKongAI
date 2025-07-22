# test.py
import time
import yaml
from utils.window_utils import activate_window_by_title
from env.game_controller import GameController

def main():
    # 读取配置文件
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # 获取配置信息
    window_title = config['screen_capture']['window_title']
    key_mapping = config.get('key_mapping', {})
    
    # 激活游戏窗口
    if not activate_window_by_title(window_title):
        print("无法激活游戏窗口，程序退出")
        return
    
    # 创建游戏控制器实例
    controller = GameController(key_mapping)
    
    # 启动AI控制
    controller.start_ai_control()
    
    try:
        # 模拟执行闪避动作10次
        for _ in range(10):
            controller.execute_action("dodge")
            time.sleep(0.2)  # 每次动作间隔0.2秒
            
    except KeyboardInterrupt:
        print("操作被用户中断")
    finally:
        # 停止AI控制并清理资源
        controller.stop_ai_control()
        controller.cleanup()

if __name__ == "__main__":
    main()