import uiautomator2 as u2
from core.config_manager import ConfigManager
from core.miniprogram import MiniProgram
from utils.logger import Logger

def test_launch_miniprogram():
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
        
        # 创建小程序实例
        miniprogram = MiniProgram(device, config_manager.config, logger)
        
        # 启动小程序
        if miniprogram.launch():
            logger.info("小程序启动测试成功!")
            return True
        else:
            logger.error("小程序启动测试失败!")
            return False
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_launch_miniprogram() 