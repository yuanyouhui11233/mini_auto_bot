import os
import yaml
from typing import Dict, Any, List

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config: Dict[str, Any] = {}
        self.devices: List[Dict[str, Any]] = []
        self._load_configs()

    def _load_configs(self) -> None:
        """加载所有配置文件"""
        # 加载主配置文件
        config_path = os.path.join(self.config_dir, "config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 加载设备配置文件
        devices_path = os.path.join(self.config_dir, "devices.yaml")
        with open(devices_path, 'r', encoding='utf-8') as f:
            devices_config = yaml.safe_load(f)
            self.devices = devices_config.get('devices', [])

    def get_time_windows(self) -> List[Dict[str, Any]]:
        """获取时间窗口配置"""
        return self.config.get('time_windows', [])

    def get_search_config(self) -> Dict[str, Any]:
        """获取搜索配置"""
        return self.config.get('search', {})

    def get_operation_config(self) -> Dict[str, Any]:
        """获取操作配置"""
        return self.config.get('operation', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get('logging', {})

    def get_devices(self) -> List[Dict[str, Any]]:
        """获取设备配置列表"""
        return self.devices

    def get_device_by_name(self, name: str) -> Dict[str, Any]:
        """根据名称获取设备配置"""
        for device in self.devices:
            if device['name'] == name:
                return device
        raise ValueError(f"Device {name} not found in configuration")
