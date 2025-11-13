# ===========================
# src/repositories/fornecedor_repository.py
# ===========================
"""
Repository de Fornecedor.
"""
from typing import Optional, List
from datetime import datetime
from src.models.fornecedor import Fornecedor
from src.repositories.base_repository import BaseRepository
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import FornecedorNaoEncontradoException


logger = get_logger(__name__)


class FornecedorRepository(BaseRepository[Fornecedor]):
    """Repository para operações com fornecedores."""
    
    def _initialize_table(self) -> None:
        """Cria tabela de fornecedores."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fornecedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cnpj TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    endereco TEXT,
                    cidade TEXT,
                    estado TEXT,
                    cep TEXT,
                    contato_principal TEXT,
                    prazo_entrega_dias INTEGER DEFAULT 7,
                    ativo INTEGER DEFAULT 1,
                    data_cadastro TEXT NOT NULL
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_fornecedor_cnpj ON fornecedores(cnpj)')
            logger.info("Tabela de fornecedores inicializada")
    
    def create(self, fornecedor: Fornecedor) -> Fornecedor:
        """Cria novo fornecedor."""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO fornecedores (
                    nome, cnpj, email, telefone, endereco, cidade, estado, cep,
                    contato_principal, prazo_entrega_dias, ativo, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fornecedor.nome, fornecedor.cnpj, fornecedor.email,
                fornecedor.telefone, fornecedor.endereco, fornecedor.cidade,
                fornecedor.estado, fornecedor.cep, fornecedor.contato_principal,
                fornecedor.prazo_entrega_dias, 1 if fornecedor.ativo else 0,
                fornecedor.data_cadastro.isoformat()
            ))
            
            fornecedor.id = cursor.lastrowid
            logger.info(f"Fornecedor criado: {fornecedor.id} - {fornecedor.nome}")
            return fornecedor
    
    def read(self, id: int) -> Optional[Fornecedor]:
        """Busca fornecedor por ID."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM fornecedores WHERE id = ?', (id,))
            row = cursor.fetchone()
            return self._row_to_fornecedor(row) if row else None
    
    def update(self, fornecedor: Fornecedor) -> Fornecedor:
        """Atualiza fornecedor."""
        if not self.read(fornecedor.id):
            raise FornecedorNaoEncontradoException(f"Fornecedor {fornecedor.id} não encontrado")
        
        with self._get_connection() as conn:
            conn.execute('''
                UPDATE fornecedores SET
                    nome = ?, cnpj = ?, email = ?, telefone = ?, endereco = ?,
                    cidade = ?, estado = ?, cep = ?, contato_principal = ?,
                    prazo_entrega_dias = ?, ativo = ?
                WHERE id = ?
            ''', (
                fornecedor.nome, fornecedor.cnpj, fornecedor.email,
                fornecedor.telefone, fornecedor.endereco, fornecedor.cidade,
                fornecedor.estado, fornecedor.cep, fornecedor.contato_principal,
                fornecedor.prazo_entrega_dias, 1 if fornecedor.ativo else 0,
                fornecedor.id
            ))
            
            logger.info(f"Fornecedor atualizado: {fornecedor.id}")
            return fornecedor
    
    def delete(self, id: int) -> bool:
        """Deleta fornecedor (soft delete)."""
        with self._get_connection() as conn:
            cursor = conn.execute('UPDATE fornecedores SET ativo = 0 WHERE id = ?', (id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Fornecedor deletado: {id}")
            return deleted
    
    def list_all(self, incluir_inativos: bool = False) -> List[Fornecedor]:
        """Lista todos fornecedores."""
        query = 'SELECT * FROM fornecedores'
        if not incluir_inativos:
            query += ' WHERE ativo = 1'
        query += ' ORDER BY nome'
        
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            return [self._row_to_fornecedor(row) for row in cursor.fetchall()]
    
    def buscar_por_cnpj(self, cnpj: str) -> Optional[Fornecedor]:
        """Busca fornecedor por CNPJ."""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM fornecedores WHERE cnpj = ?', (cnpj,))
            row = cursor.fetchone()
            return self._row_to_fornecedor(row) if row else None
    
    def _row_to_fornecedor(self, row) -> Fornecedor:
        """Converte row para Fornecedor."""
        return Fornecedor(
            id=row['id'],
            nome=row['nome'],
            cnpj=row['cnpj'],
            email=row['email'],
            telefone=row['telefone'],
            endereco=row['endereco'],
            cidade=row['cidade'],
            estado=row['estado'],
            cep=row['cep'],
            contato_principal=row['contato_principal'],
            prazo_entrega_dias=row['prazo_entrega_dias'],
            ativo=bool(row['ativo']),
            data_cadastro=datetime.fromisoformat(row['data_cadastro'])
        )