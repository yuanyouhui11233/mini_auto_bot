from core.config_manager import ConfigManager
from utils.logger import Logger

def main():
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 获取日志配置并初始化日志系统
    logging_config = config_manager.get_logging_config()
    logger = Logger(logging_config)
    
    # 测试配置读取
    logger.info("开始测试配置管理器...")
    
    # 测试时间窗口配置
    time_windows = config_manager.get_time_windows()
    logger.info(f"时间窗口配置: {time_windows}")
    
    # 测试搜索配置
    search_config = config_manager.get_search_config()
    logger.info(f"搜索配置: {search_config}")
    
    # 测试设备配置
    devices = config_manager.get_devices()
    logger.info(f"设备配置: {devices}")
    
    # 测试获取特定设备
    try:
        device = config_manager.get_device_by_name("mumu_1")
        logger.info(f"找到设备 mumu_1: {device}")
    except ValueError as e:
        logger.error(f"获取设备配置失败: {e}")
    
    logger.info("配置测试完成!")

if __name__ == "__main__":
    main() 