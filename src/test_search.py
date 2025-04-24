import uiautomator2 as u2
from core.miniprogram import MiniProgram
from core.config_manager import ConfigManager
from utils.logger import Logger

def TestSearch():
    # 初始化配置和日志
    config_manager = ConfigManager()
    logging_config = config_manager.get_logging_config()
    logger = Logger(logging_config)

    # 获取设备配置
    device_config = config_manager.get_device_by_name("leidian_1")

    try:
        # 连接设备
        logger.info(f"尝试连接设备: {device_config['name']}")
        device = u2.connect(f"emulator-{device_config['port']}")
        
        # 创建小程序实例
        miniprogram = MiniProgram(device, config_manager.config, logger)
        # 调用小程序的输入关键词方法
        miniprogram.search_in_miniprogram("啤酒")

    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    TestSearch()