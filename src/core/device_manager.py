import time
import threading
import subprocess
import re
from typing import Dict, List, Tuple, Optional, Callable
import uiautomator2 as u2
from utils.logger import Logger
from core.miniprogram import MiniProgram

class DeviceManager:
    """设备管理器，用于管理多个设备的连接和操作"""
    
    def __init__(self, config: dict, logger: Logger):
        """初始化设备管理器
        
        Args:
            config: 配置信息，包含多个设备的配置
            logger: 日志记录器
        """
        self.config = config
        self.logger = logger
        self.devices: Dict[str, u2.Device] = {}  # 设备ID到设备实例的映射
        self.miniprograms: Dict[str, MiniProgram] = {}  # 设备ID到MiniProgram实例的映射
        self.device_configs: Dict[str, dict] = config.get('devices', {})  # 设备ID到设备配置的映射
        self.auto_discovery = config.get('options', {}).get('auto_discovery', True)  # 是否自动发现设备
        self.default_miniprogram_config = config.get('default_miniprogram', {
            "name": "胖东来",
            "package": "com.tencent.mm",
            "search_timeout": 5
        })
    
    def discover_devices(self) -> List[str]:
        """自动发现可连接的设备
        
        Returns:
            List[str]: 可连接设备的ADB设备ID列表
        """
        self.logger.info("正在自动发现可连接设备...")
        
        try:
            # 执行adb devices命令获取已连接设备列表
            result = subprocess.run(
                ["adb", "devices"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # 解析输出结果
            device_list = []
            lines = result.stdout.strip().split('\n')
            # 跳过第一行（标题行）
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == 'device':
                        device_id = parts[0]
                        device_list.append(device_id)
            
            self.logger.info(f"发现 {len(device_list)} 个设备: {device_list}")
            return device_list
            
        except Exception as e:
            self.logger.error(f"自动发现设备失败: {str(e)}")
            return []
    
    def create_device_config(self, device_id: str) -> dict:
        """为新发现的设备创建配置
        
        Args:
            device_id: 设备ID
            
        Returns:
            dict: 设备配置
        """
        return {
            "connect_info": device_id,
            "miniprogram": self.default_miniprogram_config.copy()
        }
        
    def connect_devices(self) -> bool:
        """连接所有可用设备
        
        如果启用了自动发现，则会自动发现并连接所有可用设备；
        否则使用配置文件中的设备信息进行连接。
        
        Returns:
            bool: 是否所有设备都成功连接
        """
        discovered_devices = []
        
        # 如果启用了自动发现，则自动发现设备
        if self.auto_discovery:
            discovered_devices = self.discover_devices()
            
            if not discovered_devices:
                self.logger.error("未发现可连接的设备")
                return False
                
            # 为发现的设备创建配置
            for i, device_id in enumerate(discovered_devices):
                device_name = f"device{i+1}"
                if device_name not in self.device_configs:
                    self.device_configs[device_name] = self.create_device_config(device_id)
                    self.logger.info(f"为设备 {device_id} 创建配置，命名为 {device_name}")
        
        # 如果没有设备配置，则失败
        if not self.device_configs:
            self.logger.error("配置中没有设备信息")
            return False
            
        # 连接所有设备
        expected_count = len(discovered_devices) if self.auto_discovery else len(self.device_configs)
        success_count = 0
        failed_devices = []
        
        for device_name, device_config in self.device_configs.items():
            try:
                self.logger.info(f"正在连接设备: {device_name}")
                # 设备连接信息，可以是序列号、IP地址或ADB设备ID
                connect_info = device_config.get('connect_info', device_name)
                device = u2.connect(connect_info)
                
                # 验证连接
                info = device.info
                self.logger.info(f"设备 {device_name} 连接成功，信息: {info}")
                
                # 存储设备实例
                self.devices[device_name] = device
                
                # 创建对应的MiniProgram实例
                device_logger = Logger(f"device_{device_name}")
                self.miniprograms[device_name] = MiniProgram(device, device_config, device_logger)
                
                success_count += 1
                
            except Exception as e:
                self.logger.error(f"连接设备 {device_name} 失败: {str(e)}")
                failed_devices.append(device_name)
        
        # 计算连接成功率
        if expected_count > 0:
            success_rate = (success_count / expected_count) * 100
            self.logger.info(f"设备连接成功率: {success_rate:.1f}% ({success_count}/{expected_count})")
        
        # 自动发现模式下，必须所有设备都连接成功
        if self.auto_discovery:
            if success_count < expected_count:
                self.logger.error(f"部分设备连接失败: {failed_devices}")
                return False
            return True
        
        # 配置模式下，至少要有一个设备连接成功
        return success_count > 0
    
    def disconnect_devices(self):
        """断开所有设备连接"""
        for device_id, device in self.devices.items():
            try:
                self.logger.info(f"断开设备 {device_id} 连接")
                # UIAutomator2没有显式的断开方法，这里可以执行一些清理操作
                # 例如停止uiautomator服务
                device.service("uiautomator").stop()
            except Exception as e:
                self.logger.error(f"断开设备 {device_id} 连接时出错: {str(e)}")
    
    def execute_on_device(self, device_id: str, action: Callable[[MiniProgram], bool]) -> bool:
        """在指定设备上执行操作
        
        Args:
            device_id: 设备ID
            action: 要执行的操作函数，接受MiniProgram实例作为参数
            
        Returns:
            bool: 操作是否成功
        """
        if device_id not in self.miniprograms:
            self.logger.error(f"设备 {device_id} 未连接")
            return False
            
        try:
            miniprogram = self.miniprograms[device_id]
            return action(miniprogram)
        except Exception as e:
            self.logger.error(f"在设备 {device_id} 上执行操作时出错: {str(e)}")
            return False
    
    def execute_on_all_devices(self, action: Callable[[MiniProgram], bool], parallel: bool = False) -> Dict[str, bool]:
        """在所有设备上执行操作
        
        Args:
            action: 要执行的操作函数，接受MiniProgram实例作为参数
            parallel: 是否并行执行
            
        Returns:
            Dict[str, bool]: 设备ID到操作结果的映射
        """
        results = {}
        
        if parallel:
            # 并行执行
            threads = []
            results_lock = threading.Lock()
            
            def thread_action(device_id: str):
                result = self.execute_on_device(device_id, action)
                with results_lock:
                    results[device_id] = result
            
            for device_id in self.miniprograms.keys():
                thread = threading.Thread(target=thread_action, args=(device_id,))
                threads.append(thread)
                thread.start()
                
            for thread in threads:
                thread.join()
        else:
            # 串行执行
            for device_id in self.miniprograms.keys():
                results[device_id] = self.execute_on_device(device_id, action)
                
        return results
    
    def launch_miniprogram_on_device(self, device_id: str) -> bool:
        """在指定设备上启动小程序
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 是否成功启动
        """
        return self.execute_on_device(device_id, lambda mp: mp.launch())
    
    def launch_miniprogram_on_all_devices(self, parallel: bool = False) -> Dict[str, bool]:
        """在所有设备上启动小程序
        
        Args:
            parallel: 是否并行执行
            
        Returns:
            Dict[str, bool]: 设备ID到启动结果的映射
        """
        return self.execute_on_all_devices(lambda mp: mp.launch(), parallel)
        
    def get_connected_device_count(self) -> int:
        """获取已连接的设备数量
        
        Returns:
            int: 已连接的设备数量
        """
        return len(self.devices) 