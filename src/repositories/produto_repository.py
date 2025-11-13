# ===========================
# src/repositories/produto_repository.py
# ===========================
"""
Repository de Produto.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from src.models.produto import Produto
from src.repositories.base_repository import BaseRepository
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import ProdutoNaoEncontradoException


logger = get_logger(__name__)


class ProdutoRepository(BaseRepository[Produto]):
    """Repository para operações com produtos."""
    
    def _initialize_table(self) -> None:
        """Cria tabela de produtos."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    codigo TEXT UNIQUE,
                    descricao TEXT,
                    preco REAL NOT NULL,
                    preco_custo REAL,
                    quantidade INTEGER NOT NULL DEFAULT 0,
                    estoque_minimo INTEGER DEFAULT 10,
                    estoque_maximo INTEGER DEFAULT 1000,
                    categoria_id INTEGER NOT NULL,
                    fornecedor_id INTEGER NOT NULL,
                    localizacao TEXT,
                    data_validade TEXT,
                    ativo INTEGER DEFAULT 1,
                    data_cadastro TEXT NOT NULL,
                    data_atualizacao TEXT,
                    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
                    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
                )
            ''')
            
            # Índices para melhorar performance de consultas
            conn.execute('CREATE INDEX IF NOT EXISTS idx_produto_nome ON produtos(nome)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_produto_codigo ON produtos(codigo)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_produto_categoria ON produtos(categoria_id)')
            
            logger.info("Tabela de produtos inicializada")
    
    def create(self, produto: Produto) -> Produto:
        """
        Cria novo produto.
        
        Args:
            produto: Produto a ser criado
            
        Returns:
            Produto criado com ID
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO produtos (
                    nome, codigo, descricao, preco, preco_custo, quantidade,
                    estoque_minimo, estoque_maximo, categoria_id, fornecedor_id,
                    localizacao, data_validade, ativo, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                produto.nome, produto.codigo, produto.descricao,
                produto.preco, produto.preco_custo, produto.quantidade,
                produto.estoque_minimo, produto.estoque_maximo,
                produto.categoria_id, produto.fornecedor_id,
                produto.localizacao,
                produto.data_validade.isoformat() if produto.data_validade else None,
                1 if produto.ativo else 0,
                produto.data_cadastro.isoformat()
            ))
            
            produto.id = cursor.lastrowid
            logger.info(f"Produto criado: {produto.id} - {produto.nome}")
            return produto
    
    def read(self, id: int) -> Optional[Produto]:
        """
        Busca produto por ID.
        
        Args:
            id: ID do produto
            
        Returns:
            Produto encontrado ou None
        """
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_produto(row)
            return None
    
    def update(self, produto: Produto) -> Produto:
        """
        Atualiza produto.
        
        Args:
            produto: Produto a ser atualizado
            
        Returns:
            Produto atualizado
            
        Raises:
            ProdutoNaoEncontradoException: Se produto não existe
        """
        if not self.read(produto.id):
            raise ProdutoNaoEncontradoException(f"Produto {produto.id} não encontrado")
        
        produto.data_atualizacao = datetime.now()
        
        with self._get_connection() as conn:
            conn.execute('''
                UPDATE produtos SET
                    nome = ?, codigo = ?, descricao = ?, preco = ?, preco_custo = ?,
                    quantidade = ?, estoque_minimo = ?, estoque_maximo = ?,
                    categoria_id = ?, fornecedor_id = ?, localizacao = ?,
                    data_validade = ?, ativo = ?, data_atualizacao = ?
                WHERE id = ?
            ''', (
                produto.nome, produto.codigo, produto.descricao,
                produto.preco, produto.preco_custo, produto.quantidade,
                produto.estoque_minimo, produto.estoque_maximo,
                produto.categoria_id, produto.fornecedor_id, produto.localizacao,
                produto.data_validade.isoformat() if produto.data_validade else None,
                1 if produto.ativo else 0,
                produto.data_atualizacao.isoformat(),
                produto.id
            ))
            
            logger.info(f"Produto atualizado: {produto.id}")
            return produto
    
    def delete(self, id: int) -> bool:
        """
        Deleta produto (soft delete).
        
        Args:
            id: ID do produto
            
        Returns:
            True se deletado
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                'UPDATE produtos SET ativo = 0 WHERE id = ?',
                (id,)
            )
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Produto deletado: {id}")
            return deleted
    
    def list_all(self, incluir_inativos: bool = False) -> List[Produto]:
        """
        Lista todos produtos.
        
        Args:
            incluir_inativos: Se deve incluir produtos inativos
            
        Returns:
            Lista de produtos
        """
        query = 'SELECT * FROM produtos'
        if not incluir_inativos:
            query += ' WHERE ativo = 1'
        query += ' ORDER BY nome'
        
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            return [self._row_to_produto(row) for row in cursor.fetchall()]
    
    def buscar_por_nome(self, nome: str) -> List[Produto]:
        """
        Busca produtos por nome (LIKE).
        
        Args:
            nome: Nome ou parte do nome
            
        Returns:
            Lista de produtos encontrados
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM produtos WHERE nome LIKE ? AND ativo = 1 ORDER BY nome',
                (f'%{nome}%',)
            )
            return [self._row_to_produto(row) for row in cursor.fetchall()]
    
    def buscar_por_codigo(self, codigo: str) -> Optional[Produto]:
        """
        Busca produto por código único.
        
        Args:
            codigo: Código do produto
            
        Returns:
            Produto encontrado ou None
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM produtos WHERE codigo = ? AND ativo = 1',
                (codigo,)
            )
            row = cursor.fetchone()
            return self._row_to_produto(row) if row else None
    
    def buscar_por_categoria(self, categoria_id: int) -> List[Produto]:
        """
        Busca produtos por categoria.
        
        Args:
            categoria_id: ID da categoria
            
        Returns:
            Lista de produtos
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM produtos WHERE categoria_id = ? AND ativo = 1 ORDER BY nome',
                (categoria_id,)
            )
            return [self._row_to_produto(row) for row in cursor.fetchall()]
    
    def buscar_estoque_critico(self) -> List[Produto]:
        """
        Busca produtos em estoque crítico.
        
        Returns:
            Lista de produtos com estoque baixo
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM produtos WHERE quantidade <= estoque_minimo AND ativo = 1'
            )
            return [self._row_to_produto(row) for row in cursor.fetchall()]
    
    def buscar_com_filtros(
        self,
        categoria_id: Optional[int] = None,
        fornecedor_id: Optional[int] = None,
        preco_min: Optional[float] = None,
        preco_max: Optional[float] = None,
        ordenar_por: str = 'nome',
        ordem: str = 'ASC'
    ) -> List[Produto]:
        """
        Busca produtos com múltiplos filtros e ordenação.
        
        Args:
            categoria_id: Filtrar por categoria
            fornecedor_id: Filtrar por fornecedor
            preco_min: Preço mínimo
            preco_max: Preço máximo
            ordenar_por: Campo para ordenação
            ordem: ASC ou DESC
            
        Returns:
            Lista de produtos filtrados
        """
        query = 'SELECT * FROM produtos WHERE ativo = 1'
        params = []
        
        if categoria_id:
            query += ' AND categoria_id = ?'
            params.append(categoria_id)
        
        if fornecedor_id:
            query += ' AND fornecedor_id = ?'
            params.append(fornecedor_id)
        
        if preco_min is not None:
            query += ' AND preco >= ?'
            params.append(preco_min)
        
        if preco_max is not None:
            query += ' AND preco <= ?'
            params.append(preco_max)
        
        # Validar campo de ordenação
        campos_validos = ['nome', 'preco', 'quantidade', 'data_cadastro']
        if ordenar_por not in campos_validos:
            ordenar_por = 'nome'
        
        ordem = 'DESC' if ordem.upper() == 'DESC' else 'ASC'
        query += f' ORDER BY {ordenar_por} {ordem}'
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_produto(row) for row in cursor.fetchall()]
    
    def atualizar_quantidade(self, produto_id: int, nova_quantidade: int) -> bool:
        """
        Atualiza apenas a quantidade de um produto.
        
        Args:
            produto_id: ID do produto
            nova_quantidade: Nova quantidade
            
        Returns:
            True se atualizado
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                'UPDATE produtos SET quantidade = ?, data_atualizacao = ? WHERE id = ?',
                (nova_quantidade, datetime.now().isoformat(), produto_id)
            )
            return cursor.rowcount > 0
    
    def _row_to_produto(self, row) -> Produto:
        """Converte row do banco para objeto Produto."""
        return Produto(
            id=row['id'],
            nome=row['nome'],
            codigo=row['codigo'],
            descricao=row['descricao'],
            preco=row['preco'],
            preco_custo=row['preco_custo'],
            quantidade=row['quantidade'],
            estoque_minimo=row['estoque_minimo'],
            estoque_maximo=row['estoque_maximo'],
            categoria_id=row['categoria_id'],
            fornecedor_id=row['fornecedor_id'],
            localizacao=row['localizacao'],
            data_validade=date.fromisoformat(row['data_validade']) if row['data_validade'] else None,
            ativo=bool(row['ativo']),
            data_cadastro=datetime.fromisoformat(row['data_cadastro']),
            data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None
        )