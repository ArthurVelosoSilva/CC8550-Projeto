# ===========================
# src/repositories/usuario_repository.py
# ===========================
"""
Repository de Usuário.
"""
from typing import Optional, List
from datetime import datetime
from src.models.usuario import Usuario
from src.repositories.base_repository import BaseRepository
from src.utils.logger import get_logger


logger = get_logger(__name__)


class UsuarioRepository(BaseRepository[Usuario]):
    """Repository para operações com usuários."""
    
    def _initialize_table(self) -> None:
        """Cria tabela de usuários."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    ativo INTEGER DEFAULT 1,
                    data_cadastro TEXT NOT NULL
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuarios(email)')
            logger.info("Tabela de usuários inicializada")
    
    def create(self, usuario: Usuario) -> Usuario:
        """Cria novo usuário."""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO usuarios (nome, email, senha_hash, ativo, data_cadastro)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                usuario.nome, usuario.email, usuario.senha_hash,
                1 if usuario.ativo else 0,
                usuario.data_cadastro.isoformat()
            ))
            
            usuario.id = cursor.lastrowid
            logger.info(f"Usuário criado: {usuario.id} - {usuario.email}")
            return usuario
    
    def read(self, id: int) -> Optional[Usuario]:
        """Busca usuário por ID."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
            row = cursor.fetchone()
            return self._row_to_usuario(row) if row else None
    
    def update(self, usuario: Usuario) -> Usuario:
        """Atualiza usuário."""
        with self._get_connection() as conn:
            conn.execute('''
                UPDATE usuarios SET nome = ?, email = ?, senha_hash = ?, ativo = ?
                WHERE id = ?
            ''', (usuario.nome, usuario.email, usuario.senha_hash, 
                  1 if usuario.ativo else 0, usuario.id))
            
            logger.info(f"Usuário atualizado: {usuario.id}")
            return usuario
    
    def delete(self, id: int) -> bool:
        """Deleta usuário (soft delete)."""
        with self._get_connection() as conn:
            cursor = conn.execute('UPDATE usuarios SET ativo = 0 WHERE id = ?', (id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Usuário deletado: {id}")
            return deleted
    
    def list_all(self, incluir_inativos: bool = False) -> List[Usuario]:
        """Lista todos usuários."""
        query = 'SELECT * FROM usuarios'
        if not incluir_inativos:
            query += ' WHERE ativo = 1'
        query += ' ORDER BY nome'
        
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            return [self._row_to_usuario(row) for row in cursor.fetchall()]
    
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            row = cursor.fetchone()
            return self._row_to_usuario(row) if row else None
    
    def _row_to_usuario(self, row) -> Usuario:
        """Converte row para Usuario."""
        return Usuario(
            id=row['id'],
            nome=row['nome'],
            email=row['email'],
            senha_hash=row['senha_hash'],
            ativo=bool(row['ativo']),
            data_cadastro=datetime.fromisoformat(row['data_cadastro'])
        )