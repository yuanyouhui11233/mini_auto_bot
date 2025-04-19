import os
import sys
from loguru import logger
from typing import Dict, Any

class Logger:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._setup_logger()

    def _setup_logger(self) -> None:
        """配置日志系统"""
        # 移除默认的处理器
        logger.remove()

        # 确保日志目录存在
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 配置日志格式
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        # 添加控制台输出
        logger.add(
            sys.stderr,
            format=log_format,
            level=self.config.get('level', 'INFO'),
            colorize=True
        )

        # 添加文件输出
        logger.add(
            os.path.join(log_dir, "bot_{time}.log"),
            format=log_format,
            level=self.config.get('level', 'INFO'),
            rotation=self.config.get('rotation', "1 day"),
            retention=self.config.get('retention', "7 days"),
            compression="zip",
            encoding="utf-8"
        )

    @staticmethod
    def debug(message: str) -> None:
        """输出调试日志"""
        logger.debug(message)

    @staticmethod
    def info(message: str) -> None:
        """输出信息日志"""
        logger.info(message)

    @staticmethod
    def warning(message: str) -> None:
        """输出警告日志"""
        logger.warning(message)

    @staticmethod
    def error(message: str) -> None:
        """输出错误日志"""
        logger.error(message)

    @staticmethod
    def critical(message: str) -> None:
        """输出严重错误日志"""
        logger.critical(message)
