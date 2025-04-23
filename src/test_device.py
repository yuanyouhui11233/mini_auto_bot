import uiautomator2 as u2
from core.config_manager import ConfigManager
from utils.logger import Logger
import time

def test_device_connection():
    # 初始化配置和日志
    config_manager = ConfigManager()
    logging_config = config_manager.get_logging_config()
    logger = Logger(logging_config)
    
    # 获取设备配置
    device_config = config_manager.get_device_by_name("mumu_1")
    
    try:
        # 连接设备
        logger.info(f"尝试连接设备: {device_config['name']}")
        device = u2.connect(f"127.0.0.1:{device_config['port']}")
        
        # 等待设备就绪
        logger.info("等待设备就绪...")
        time.sleep(2)
        
        # 获取设备信息
        info = device.info
        logger.info(f"设备信息: {info}")
        
        # 获取屏幕分辨率
        width, height = device.window_size()
        logger.info(f"屏幕分辨率: {width}x{height}")
        
        # 检查是否已解锁
        # if device.info.get('screenOn'):
            # logger.info("设备已解锁")
        # else:
            # logger.info("设备未解锁")
            
        # 测试简单操作
        logger.info("测试按Home键...")
        device.press("home")
        time.sleep(1)
            
        logger.info("设备连接测试完成!")
        return True
        
    except Exception as e:
        logger.error(f"连接设备失败: {str(e)}")
        logger.error("请确保：")
        logger.error("1. 雷电模拟器已启动")
        logger.error("2. 模拟器设置中的USB调试已开启")
        logger.error("3. 模拟器ADB端口（默认5554）未被占用")
        return False

if __name__ == "__main__":
    test_device_connection() 