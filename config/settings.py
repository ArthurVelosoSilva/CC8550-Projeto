# ===========================
# config/settings.py
# ===========================
"""
Configurações do sistema de estoque.
"""
import os
from typing import Dict, Any
import yaml
from pathlib import Path


class Settings:
    """Gerencia configurações da aplicação."""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        Inicializa configurações.
        
        Args:
            config_file: Caminho do arquivo de configuração
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega configurações de arquivo YAML ou variáveis de ambiente.
        
        Returns:
            Dicionário com configurações
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Configurações padrão
        return {
            'database': {
                'type': os.getenv('DB_TYPE', 'sqlite'),
                'name': os.getenv('DB_NAME', 'estoque.db'),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'user': os.getenv('DB_USER', ''),
                'password': os.getenv('DB_PASSWORD', '')
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'file': os.getenv('LOG_FILE', 'logs/estoque.log'),
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'api': {
                'host': os.getenv('API_HOST', '0.0.0.0'),
                'port': int(os.getenv('API_PORT', 5000)),
                'debug': os.getenv('API_DEBUG', 'False') == 'True'
            },
            'business_rules': {
                'min_estoque_critico': int(os.getenv('MIN_ESTOQUE_CRITICO', 10)),
                'max_desconto_percentual': float(os.getenv('MAX_DESCONTO', 30.0)),
                'dias_validade_alerta': int(os.getenv('DIAS_VALIDADE_ALERTA', 30))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração.
        
        Args:
            key: Chave de configuração (ex: 'database.type')
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value


# Instância global de configurações
settings = Settings()