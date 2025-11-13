# ===========================
# src/repositories/base_repository.py
# ===========================
"""
Repository base com operações CRUD genéricas.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
import sqlite3
from contextlib import contextmanager
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import DatabaseException


T = TypeVar('T')
logger = get_logger(__name__)


class BaseRepository(ABC, Generic[T]):
    """Repository base com operações CRUD."""
    
    def __init__(self, db_path: str):
        """
        Inicializa repository.
        
        Args:
            db_path: Caminho do banco de dados
        """
        self.db_path = db_path
        self._initialize_table()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexões de banco."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro no banco de dados: {e}", exc_info=True)
            raise DatabaseException(f"Erro no banco de dados: {e}")
        finally:
            if conn:
                conn.close()
    
    @abstractmethod
    def _initialize_table(self) -> None:
        """Cria tabela se não existir."""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Cria nova entidade."""
        pass
    
    @abstractmethod
    def read(self, id: int) -> Optional[T]:
        """Lê entidade por ID."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Atualiza entidade."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Deleta entidade."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[T]:
        """Lista todas entidades."""
        pass