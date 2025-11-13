# ===========================
# src/services/produto_service.py
# ===========================
"""
Serviço de lógica de negócio para Produtos.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from src.models.produto import Produto
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.categoria_repository import CategoriaRepository
from src.repositories.fornecedor_repository import FornecedorRepository
from src.utils.validators import Validators
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import (
    ValidacaoException, ProdutoNaoEncontradoException,
    CategoriaNaoEncontradaException, FornecedorNaoEncontradoException,
    OperacaoNaoPermitidaException
)


logger = get_logger(__name__)


class ProdutoService:
    """Serviço para gerenciar produtos com regras de negócio."""
    
    def __init__(
        self,
        produto_repo: ProdutoRepository,
        categoria_repo: CategoriaRepository,
        fornecedor_repo: FornecedorRepository
    ):
        """
        Inicializa serviço de produtos.
        
        Args:
            produto_repo: Repository de produtos
            categoria_repo: Repository de categorias
            fornecedor_repo: Repository de fornecedores
        """
        self.produto_repo = produto_repo
        self.categoria_repo = categoria_repo
        self.fornecedor_repo = fornecedor_repo
        self.validators = Validators()
    
    def criar_produto(
        self,
        nome: str,
        preco: float,
        quantidade: int,
        categoria_id: int,
        fornecedor_id: int,
        codigo: Optional[str] = None,
        descricao: Optional[str] = None,
        preco_custo: Optional[float] = None,
        estoque_minimo: int = 10,
        estoque_maximo: int = 1000,
        localizacao: Optional[str] = None,
        data_validade: Optional[date] = None
    ) -> Produto:
        """
        Cria novo produto com validações.
        
        REGRA DE NEGÓCIO 1: Validação complexa de produto
        - Valida todos os campos obrigatórios
        - Verifica se categoria e fornecedor existem
        - Valida preço de custo menor que preço de venda
        - Valida estoque mínimo menor que máximo
        - Valida data de validade futura
        
        Args:
            nome: Nome do produto
            preco: Preço de venda
            quantidade: Quantidade inicial
            categoria_id: ID da categoria
            fornecedor_id: ID do fornecedor
            codigo: Código único do produto
            descricao: Descrição do produto
            preco_custo: Preço de custo
            estoque_minimo: Estoque mínimo
            estoque_maximo: Estoque máximo
            localizacao: Localização física no estoque
            data_validade: Data de validade
            
        Returns:
            Produto criado
            
        Raises:
            ValidacaoException: Se validações falharem
            CategoriaNaoEncontradaException: Se categoria não existir
            FornecedorNaoEncontradoException: Se fornecedor não existir
        """
        # Validar nome
        nome = self.validators.validar_string_nao_vazia(nome, "Nome")
        
        # Validar preço
        preco = self.validators.validar_preco(preco)
        
        # Validar quantidade
        quantidade = self.validators.validar_quantidade(quantidade, permitir_zero=True)
        
        # Validar categoria existe
        categoria = self.categoria_repo.read(categoria_id)
        if not categoria:
            raise CategoriaNaoEncontradaException(f"Categoria {categoria_id} não encontrada")
        
        if not categoria.ativo:
            raise ValidacaoException(f"Categoria {categoria.nome} está inativa")
        
        # Validar fornecedor existe
        fornecedor = self.fornecedor_repo.read(fornecedor_id)
        if not fornecedor:
            raise FornecedorNaoEncontradoException(f"Fornecedor {fornecedor_id} não encontrado")
        
        if not fornecedor.ativo:
            raise ValidacaoException(f"Fornecedor {fornecedor.nome} está inativo")
        
        # Validar código único se fornecido
        if codigo:
            produto_existente = self.produto_repo.buscar_por_codigo(codigo)
            if produto_existente:
                raise ValidacaoException(f"Já existe produto com código {codigo}")
        
        # Validar preço de custo
        if preco_custo is not None:
            preco_custo = self.validators.validar_preco(preco_custo, permitir_zero=True)
            if preco_custo > preco:
                raise ValidacaoException(
                    f"Preço de custo ({preco_custo}) não pode ser maior que preço de venda ({preco})"
                )
        
        # Validar estoques
        if estoque_minimo < 0:
            raise ValidacaoException("Estoque mínimo não pode ser negativo")
        
        if estoque_maximo < estoque_minimo:
            raise ValidacaoException(
                f"Estoque máximo ({estoque_maximo}) deve ser maior que estoque mínimo ({estoque_minimo})"
            )
        
        # Validar data de validade
        if data_validade:
            data_validade = self.validators.validar_data_validade(data_validade)
        
        # Criar produto
        produto = Produto(
            nome=nome,
            preco=preco,
            quantidade=quantidade,
            categoria_id=categoria_id,
            fornecedor_id=fornecedor_id,
            codigo=codigo,
            descricao=descricao,
            preco_custo=preco_custo,
            estoque_minimo=estoque_minimo,
            estoque_maximo=estoque_maximo,
            localizacao=localizacao,
            data_validade=data_validade
        )
        
        produto = self.produto_repo.create(produto)
        logger.info(f"Produto criado com sucesso: {produto.id} - {produto.nome}")
        
        return produto
    
    def atualizar_produto(self, produto: Produto) -> Produto:
        """
        Atualiza produto com validações.
        
        Args:
            produto: Produto a ser atualizado
            
        Returns:
            Produto atualizado
            
        Raises:
            ProdutoNaoEncontradoException: Se produto não existir
            ValidacaoException: Se validações falharem
        """
        # Verificar se produto existe
        produto_existente = self.produto_repo.read(produto.id)
        if not produto_existente:
            raise ProdutoNaoEncontradoException(f"Produto {produto.id} não encontrado")
        
        # Validações básicas
        produto.nome = self.validators.validar_string_nao_vazia(produto.nome, "Nome")
        produto.preco = self.validators.validar_preco(produto.preco)
        produto.quantidade = self.validators.validar_quantidade(produto.quantidade, permitir_zero=True)
        
        # Validar preço de custo
        if produto.preco_custo is not None:
            produto.preco_custo = self.validators.validar_preco(produto.preco_custo, permitir_zero=True)
            if produto.preco_custo > produto.preco:
                raise ValidacaoException("Preço de custo não pode ser maior que preço de venda")
        
        # Validar estoques
        if produto.estoque_maximo < produto.estoque_minimo:
            raise ValidacaoException("Estoque máximo deve ser maior que estoque mínimo")
        
        # Atualizar
        produto = self.produto_repo.update(produto)
        logger.info(f"Produto atualizado: {produto.id}")
        
        return produto
    
    def deletar_produto(self, produto_id: int) -> bool:
        """
        Deleta produto (soft delete).
        
        Args:
            produto_id: ID do produto
            
        Returns:
            True se deletado
            
        Raises:
            ProdutoNaoEncontradoException: Se produto não existir
        """
        produto = self.produto_repo.read(produto_id)
        if not produto:
            raise ProdutoNaoEncontradoException(f"Produto {produto_id} não encontrado")
        
        sucesso = self.produto_repo.delete(produto_id)
        if sucesso:
            logger.info(f"Produto deletado: {produto_id}")
        
        return sucesso
    
    def buscar_produto(self, produto_id: int) -> Produto:
        """
        Busca produto por ID.
        
        Args:
            produto_id: ID do produto
            
        Returns:
            Produto encontrado
            
        Raises:
            ProdutoNaoEncontradoException: Se não encontrado
        """
        produto = self.produto_repo.read(produto_id)
        if not produto:
            raise ProdutoNaoEncontradoException(f"Produto {produto_id} não encontrado")
        
        return produto
    
    def listar_produtos(
        self,
        categoria_id: Optional[int] = None,
        fornecedor_id: Optional[int] = None,
        preco_min: Optional[float] = None,
        preco_max: Optional[float] = None,
        ordenar_por: str = 'nome',
        ordem: str = 'ASC'
    ) -> List[Produto]:
        """
        Lista produtos com filtros e ordenação.
        
        FUNCIONALIDADE DE CONSULTA/BUSCA 1: Filtros e ordenação de produtos
        
        Args:
            categoria_id: Filtrar por categoria
            fornecedor_id: Filtrar por fornecedor
            preco_min: Preço mínimo
            preco_max: Preço máximo
            ordenar_por: Campo para ordenação
            ordem: ASC ou DESC
            
        Returns:
            Lista de produtos
        """
        return self.produto_repo.buscar_com_filtros(
            categoria_id=categoria_id,
            fornecedor_id=fornecedor_id,
            preco_min=preco_min,
            preco_max=preco_max,
            ordenar_por=ordenar_por,
            ordem=ordem
        )
    
    def aplicar_desconto(
        self,
        produto_id: int,
        percentual_desconto: float
    ) -> Produto:
        """
        Aplica desconto ao produto.
        
        REGRA DE NEGÓCIO 2: Aplicação de desconto com limites
        - Validar percentual entre 0 e 30%
        - Calcular novo preço
        - Não permitir preço abaixo do custo
        - Registrar alteração
        
        Args:
            produto_id: ID do produto
            percentual_desconto: Percentual de desconto (0-30)
            
        Returns:
            Produto atualizado
            
        Raises:
            ValidacaoException: Se desconto inválido
            OperacaoNaoPermitidaException: Se preço ficaria abaixo do custo
        """
        from config.settings import settings
        
        max_desconto = settings.get('business_rules.max_desconto_percentual', 30.0)
        
        # Validar percentual
        if percentual_desconto < 0 or percentual_desconto > max_desconto:
            raise ValidacaoException(
                f"Desconto deve estar entre 0% e {max_desconto}%"
            )
        
        # Buscar produto
        produto = self.buscar_produto(produto_id)
        
        # Calcular novo preço
        novo_preco = produto.preco * (1 - percentual_desconto / 100)
        novo_preco = round(novo_preco, 2)
        
        # Verificar se preço não fica abaixo do custo
        if produto.preco_custo and novo_preco < produto.preco_custo:
            raise OperacaoNaoPermitidaException(
                f"Desconto resultaria em preço ({novo_preco}) "
                f"abaixo do custo ({produto.preco_custo})"
            )
        
        # Atualizar preço
        preco_anterior = produto.preco
        produto.preco = novo_preco
        produto = self.produto_repo.update(produto)
        
        logger.info(
            f"Desconto aplicado ao produto {produto_id}: "
            f"{percentual_desconto}% (R$ {preco_anterior:.2f} -> R$ {novo_preco:.2f})"
        )
        
        return produto
    
    def verificar_produtos_criticos(self) -> List[Dict[str, Any]]:
        """
        Verifica produtos em situação crítica.
        
        REGRA DE NEGÓCIO 3: Análise de produtos críticos
        - Produtos com estoque baixo
        - Produtos próximos do vencimento
        - Produtos com margem de lucro baixa
        - Gera relatório com recomendações
        
        Returns:
            Lista de produtos críticos com detalhes
        """
        from config.settings import settings
        
        produtos_criticos = []
        
        # Produtos com estoque baixo
        produtos_estoque_baixo = self.produto_repo.buscar_estoque_critico()
        
        for produto in produtos_estoque_baixo:
            categoriaobj = self.categoria_repo.read(produto.categoria_id)
            fornecedor = self.fornecedor_repo.read(produto.fornecedor_id)
            
            info = {
                'produto_id': produto.id,
                'nome': produto.nome,
                'tipo_alerta': 'ESTOQUE_CRITICO',
                'quantidade_atual': produto.quantidade,
                'estoque_minimo': produto.estoque_minimo,
                'categorias': categoriaobj.nome if categoriaobj else 'N/A',
                'fornecedor': fornecedor.nome if fornecedor else 'N/A',
                'recomendacao': f'Repor estoque. Quantidade recomendada: {produto.estoque_maximo - produto.quantidade}'
            }
            produtos_criticos.append(info)
        
        # Produtos próximos do vencimento
        dias_alerta = settings.get('business_rules.dias_validade_alerta', 30)
        todos_produtos = self.produto_repo.list_all()
        
        for produto in todos_produtos:
            if produto.esta_proximo_vencimento(dias_alerta):
                dias_restantes = (produto.data_validade - date.today()).days
                
                info = {
                    'produto_id': produto.id,
                    'nome': produto.nome,
                    'tipo_alerta': 'PROXIMO_VENCIMENTO',
                    'data_validade': produto.data_validade.isoformat(),
                    'dias_restantes': dias_restantes,
                    'quantidade': produto.quantidade,
                    'recomendacao': 'Promover produto ou aplicar desconto para acelerar vendas'
                }
                produtos_criticos.append(info)
        
        # Produtos com margem baixa (< 10%)
        for produto in todos_produtos:
            if produto.preco_custo:
                margem = produto.calcular_margem_lucro()
                if margem < 10:
                    info = {
                        'produto_id': produto.id,
                        'nome': produto.nome,
                        'tipo_alerta': 'MARGEM_BAIXA',
                        'margem_lucro': margem,
                        'preco_custo': produto.preco_custo,
                        'preco_venda': produto.preco,
                        'recomendacao': 'Revisar preço de venda ou negociar preço de custo com fornecedor'
                    }
                    produtos_criticos.append(info)
        
        logger.info(f"Análise de produtos críticos: {len(produtos_criticos)} alertas encontrados")
        
        return produtos_criticos