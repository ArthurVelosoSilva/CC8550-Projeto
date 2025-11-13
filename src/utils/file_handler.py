# ===========================
# src/utils/file_handler.py
# ===========================
"""
Manipulação de arquivos do sistema.
"""
import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from src.utils.logger import get_logger


logger = get_logger(__name__)


class FileHandler:
    """Gerenciador de operações com arquivos."""
    
    @staticmethod
    def exportar_json(data: List[Dict[str, Any]], filepath: str) -> bool:
        """
        Exporta dados para arquivo JSON.
        
        Args:
            data: Lista de dicionários para exportar
            filepath: Caminho do arquivo
            
        Returns:
            True se sucesso
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Dados exportados para {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar JSON: {e}", exc_info=True)
            return False
    
    @staticmethod
    def importar_json(filepath: str) -> List[Dict[str, Any]]:
        """
        Importa dados de arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Lista de dicionários
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Dados importados de {filepath}")
            return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"Erro ao importar JSON: {e}", exc_info=True)
            return []
    
    @staticmethod
    def exportar_csv(data: List[Dict[str, Any]], filepath: str) -> bool:
        """
        Exporta dados para arquivo CSV.
        
        Args:
            data: Lista de dicionários para exportar
            filepath: Caminho do arquivo
            
        Returns:
            True se sucesso
        """
        try:
            if not data:
                logger.warning("Nenhum dado para exportar")
                return False
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Dados exportados para {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {e}", exc_info=True)
            return False
    
    @staticmethod
    def importar_csv(filepath: str) -> List[Dict[str, Any]]:
        """
        Importa dados de arquivo CSV.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Lista de dicionários
        """
        try:
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            logger.info(f"Dados importados de {filepath}: {len(data)} registros")
            return data
        except Exception as e:
            logger.error(f"Erro ao importar CSV: {e}", exc_info=True)
            return []