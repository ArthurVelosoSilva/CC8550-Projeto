# ===========================
# src/repositories/movimento_repository.py
# ===========================
"""
Repository de Movimento de Estoque.
"""
from typing import Optional, List
from datetime import datetime
from src.models.movimento import Movimento, TipoMovimento
from src.repositories.base_repository import BaseRepository
from src.utils.logger import get_logger


logger = get_logger(__name__)


class MovimentoRepository(BaseRepository[Movimento]):
    """Repository para operações com movimentos de estoque."""
    
    def _initialize_table(self) -> None:
        """Cria tabela de movimentos."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS movimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    observacao TEXT,
                    data_movimento TEXT NOT NULL,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_movimento_produto ON movimentos(produto_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_movimento_data ON movimentos(data_movimento)')
            logger.info("Tabela de movimentos inicializada")
    
    def create(self, movimento: Movimento) -> Movimento:
        """Cria novo movimento."""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO movimentos (
                    produto_id, tipo, quantidade, usuario_id, observacao, data_movimento
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                movimento.produto_id,
                movimento.tipo.value if isinstance(movimento.tipo, TipoMovimento) else movimento.tipo,
                movimento.quantidade,
                movimento.usuario_id,
                movimento.observacao,
                movimento.data_movimento.isoformat()
            ))
            
            movimento.id = cursor.lastrowid
            logger.info(f"Movimento criado: {movimento.id} - {movimento.tipo}")
            return movimento
    
    def read(self, id: int) -> Optional[Movimento]:
        """Busca movimento por ID."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM movimentos WHERE id = ?', (id,))
            row = cursor.fetchone()
            return self._row_to_movimento(row) if row else None
    
    def update(self, movimento: Movimento) -> Movimento:
        """Atualiza movimento."""
        with self._get_connection() as conn:
            conn.execute('''
                UPDATE movimentos SET
                    produto_id = ?, tipo = ?, quantidade = ?,
                    usuario_id = ?, observacao = ?, data_movimento = ?
                WHERE id = ?
            ''', (
                movimento.produto_id,
                movimento.tipo.value if isinstance(movimento.tipo, TipoMovimento) else movimento.tipo,
                movimento.quantidade,
                movimento.usuario_id,
                movimento.observacao,
                movimento.data_movimento.isoformat(),
                movimento.id
            ))
            
            logger.info(f"Movimento atualizado: {movimento.id}")
            return movimento
    
    def delete(self, id: int) -> bool:
        """Deleta movimento."""
        with self._get_connection() as conn:
            cursor = conn.execute('DELETE FROM movimentos WHERE id = ?', (id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Movimento deletado: {id}")
            return deleted
    
    def list_all(self) -> List[Movimento]:
        """Lista todos movimentos."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM movimentos ORDER BY data_movimento DESC')
            return [self._row_to_movimento(row) for row in cursor.fetchall()]
    
    def buscar_por_produto(self, produto_id: int, limite: Optional[int] = None) -> List[Movimento]:
        """
        Busca movimentos de um produto.
        
        Args:
            produto_id: ID do produto
            limite: Limite de resultados
            
        Returns:
            Lista de movimentos
        """
        query = 'SELECT * FROM movimentos WHERE produto_id = ? ORDER BY data_movimento DESC'
        if limite:
            query += f' LIMIT {limite}'
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, (produto_id,))
            return [self._row_to_movimento(row) for row in cursor.fetchall()]
    
    def buscar_por_periodo(self, data_inicio: datetime, data_fim: datetime) -> List[Movimento]:
        """
        Busca movimentos em um período.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            Lista de movimentos
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM movimentos
                WHERE data_movimento BETWEEN ? AND ?
                ORDER BY data_movimento DESC
            ''', (data_inicio.isoformat(), data_fim.isoformat()))
            
            return [self._row_to_movimento(row) for row in cursor.fetchall()]
    
    def _row_to_movimento(self, row) -> Movimento:
        """Converte row para Movimento."""
        return Movimento(
            id=row['id'],
            produto_id=row['produto_id'],
            tipo=TipoMovimento(row['tipo']),
            quantidade=row['quantidade'],
            usuario_id=row['usuario_id'],
            observacao=row['observacao'],
            data_movimento=datetime.fromisoformat(row['data_movimento'])
        )