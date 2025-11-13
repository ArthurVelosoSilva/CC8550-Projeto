# ===========================
# src/repositories/categoria_repository.py
# ===========================
"""
Repository de Categoria.
"""
from typing import Optional, List
from datetime import datetime
from src.models.categoria import Categoria
from src.repositories.base_repository import BaseRepository
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import CategoriaNaoEncontradaException


logger = get_logger(__name__)


class CategoriaRepository(BaseRepository[Categoria]):
    """Repository para operações com categorias."""
    
    def _initialize_table(self) -> None:
        """Cria tabela de categorias."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    descricao TEXT,
                    ativo INTEGER DEFAULT 1,
                    data_cadastro TEXT NOT NULL
                )
            ''')
            logger.info("Tabela de categorias inicializada")
    
    def create(self, categoria: Categoria) -> Categoria:
        """Cria nova categoria."""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO categorias (nome, descricao, ativo, data_cadastro)
                VALUES (?, ?, ?, ?)
            ''', (
                categoria.nome, categoria.descricao,
                1 if categoria.ativo else 0,
                categoria.data_cadastro.isoformat()
            ))
            
            categoria.id = cursor.lastrowid
            logger.info(f"Categoria criada: {categoria.id} - {categoria.nome}")
            return categoria
    
    def read(self, id: int) -> Optional[Categoria]:
        """Busca categoria por ID."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM categorias WHERE id = ?', (id,))
            row = cursor.fetchone()
            return self._row_to_categoria(row) if row else None
    
    def update(self, categoria: Categoria) -> Categoria:
        """Atualiza categoria."""
        if not self.read(categoria.id):
            raise CategoriaNaoEncontradaException(f"Categoria {categoria.id} não encontrada")
        
        with self._get_connection() as conn:
            conn.execute('''
                UPDATE categorias SET nome = ?, descricao = ?, ativo = ?
                WHERE id = ?
            ''', (categoria.nome, categoria.descricao, 1 if categoria.ativo else 0, categoria.id))
            
            logger.info(f"Categoria atualizada: {categoria.id}")
            return categoria
    
    def delete(self, id: int) -> bool:
        """Deleta categoria (soft delete)."""
        with self._get_connection() as conn:
            cursor = conn.execute('UPDATE categorias SET ativo = 0 WHERE id = ?', (id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Categoria deletada: {id}")
            return deleted
    
    def list_all(self, incluir_inativos: bool = False) -> List[Categoria]:
        """Lista todas categorias."""
        query = 'SELECT * FROM categorias'
        if not incluir_inativos:
            query += ' WHERE ativo = 1'
        query += ' ORDER BY nome'
        
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            return [self._row_to_categoria(row) for row in cursor.fetchall()]
    
    def _row_to_categoria(self, row) -> Categoria:
        """Converte row para Categoria."""
        return Categoria(
            id=row['id'],
            nome=row['nome'],
            descricao=row['descricao'],
            ativo=bool(row['ativo']),
            data_cadastro=datetime.fromisoformat(row['data_cadastro'])
        )