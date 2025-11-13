# ===========================
# src/utils/logger.py
# ===========================
"""
Sistema de logging da aplicação.
"""
import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """Gerenciador de logs do sistema."""
    
    _instances = {}
    
    def __new__(cls, name: str):
        """Implementa padrão Singleton por nome."""
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[name] = instance
        return cls._instances[name]
    
    def __init__(self, name: str):
        """
        Inicializa logger.
        
        Args:
            name: Nome do logger
        """
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Configura logger com handlers e formatters."""
        from config.settings import settings
        
        log_level = getattr(logging, settings.get('logging.level', 'INFO'))
        self.logger.setLevel(log_level)
        
        # Remove handlers existentes
        self.logger.handlers.clear()
        
        # Handler para arquivo
        log_file = settings.get('logging.file', 'logs/estoque.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        log_format = settings.get('logging.format')
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log nível DEBUG."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log nível INFO."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log nível WARNING."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log nível ERROR."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log nível CRITICAL."""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)


def get_logger(name: str) -> Logger:
    """
    Obtém instância de logger.
    
    Args:
        name: Nome do logger
        
    Returns:
        Instância do Logger
    """
    return Logger(name)