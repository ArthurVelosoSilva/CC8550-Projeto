# ===========================
# src/services/movimento_service.py
# ===========================
"""
Serviço de lógica de negócio para Movimentos de Estoque.
"""
from typing import List, Optional
from datetime import datetime
from src.models.movimento import Movimento, TipoMovimento
from src.repositories.movimento_repository import MovimentoRepository
from src.repositories.produto_repository import ProdutoRepository
from src.utils.validators import Validators
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import (
    EstoqueInsuficienteException, ProdutoNaoEncontradoException,
    QuantidadeInvalidaException, OperacaoNaoPermitidaException
)


logger = get_logger(__name__)


class MovimentoService:
    """Serviço para gerenciar movimentos de estoque."""
    
    def __init__(
        self,
        movimento_repo: MovimentoRepository,
        produto_repo: ProdutoRepository
    ):
        """
        Inicializa serviço de movimentos.
        
        Args:
            movimento_repo: Repository de movimentos
            produto_repo: Repository de produtos
        """
        self.movimento_repo = movimento_repo
        self.produto_repo = produto_repo
        self.validators = Validators()
    
    def registrar_entrada(
        self,
        produto_id: int,
        quantidade: int,
        usuario_id: int,
        observacao: Optional[str] = None
    ) -> Movimento:
        """
        Registra entrada de produtos no estoque.
        
        Args:
            produto_id: ID do produto
            quantidade: Quantidade a adicionar
            usuario_id: ID do usuário
            observacao: Observação sobre o movimento
            
        Returns:
            Movimento criado
            
        Raises:
            ProdutoNaoEncontradoException: Se produto não existir
            QuantidadeInvalidaException: Se quantidade inválida
        """
        # Validar quantidade
        quantidade = self.validators.validar_quantidade(quantidade, permitir_zero=False)
        
        # Buscar produto
        produto = self.produto_repo.read(produto_id)
        if not produto:
            raise ProdutoNaoEncontradoException(f"Produto {produto_id} não encontrado")
        
        # Atualizar estoque do produto
        nova_quantidade = produto.quantidade + quantidade
        
        # Verificar se não excede estoque máximo
        if nova_quantidade > produto.estoque_maximo:
            logger.warning(
                f"Entrada resultaria em estoque acima do máximo: "
                f"{nova_quantidade} > {produto.estoque_maximo}"
            )
        
        self.produto_repo.atualizar_quantidade(produto_id, nova_quantidade)
        
        # Registrar movimento
        movimento = Movimento(
            produto_id=produto_id,
            tipo=TipoMovimento.ENTRADA,
            quantidade=quantidade,
            usuario_id=usuario_id,
            observacao=observacao
        )
        
        movimento = self.movimento_repo.create(movimento)
        logger.info(
            f"Entrada registrada: Produto {produto_id}, "
            f"Quantidade {quantidade}, Novo total: {nova_quantidade}"
        )
        
        return movimento
    
    def registrar_saida(
        self,
        produto_id: int,
        quantidade: int,
        usuario_id: int,
        observacao: Optional[str] = None
    ) -> Movimento:
        """
        Registra saída de produtos do estoque.
        
        Args:
            produto_id: ID do produto
            quantidade: Quantidade a retirar
            usuario_id: ID do usuário
            observacao: Observação sobre o movimento
            
        Returns:
            Movimento criado
            
        Raises:
            ProdutoNaoEncontradoException: Se produto não existir
            EstoqueInsuficienteException: Se estoque insuficiente
        """
        # Validar quantidade
        quantidade = self.validators.validar_quantidade(quantidade, permitir_zero=False)
        
        # Buscar produto
        produto = self.produto_repo.read(produto_id)
        if not produto:
            raise ProdutoNaoEncontradoException(f"Produto {produto_id} não encontrado")
        
        # Verificar estoque suficiente
        if produto.quantidade < quantidade:
            raise EstoqueInsuficienteException(
                f"Estoque insuficiente. Disponível: {produto.quantidade}, "
                f"Solicitado: {quantidade}"
            )
        
        # Atualizar estoque
        nova_quantidade = produto.quantidade - quantidade
        self.produto_repo.atualizar_quantidade(produto_id, nova_quantidade)
        
        # Verificar se ficou em estoque crítico
        if nova_quantidade <= produto.estoque_minimo:
            logger.warning(
                f"ALERTA: Produto {produto_id} ({produto.nome}) em estoque crítico: "
                f"{nova_quantidade} unidades"
            )
        
        # Registrar movimento
        movimento = Movimento(
            produto_id=produto_id,
            tipo=TipoMovimento.SAIDA,
            quantidade=quantidade,
            usuario_id=usuario_id,
            observacao=observacao
        )
        
        movimento = self.movimento_repo.create(movimento)
        logger.info(
            f"Saída registrada: Produto {produto_id}, "
            f"Quantidade {quantidade}, Novo total: {nova_quantidade}"
        )
        
        return movimento
    
    def registrar_ajuste(
        self,
        produto_id: int,
        nova_quantidade: int,
        usuario_id: int,
        observacao: str
    ) -> Movimento:
        """
        Registra ajuste manual de estoque.
        
        Args:
            produto_id: ID do produto
            nova_quantidade: Nova quantidade do estoque
            usuario_id: ID do usuário
            observacao: Motivo do ajuste (obrigatório)
            
        Returns:
            Movimento criado
            
        Raises:
            ValidacaoException: Se observação não fornecida
        """
        # Validar observação obrigatória
        if not observacao or not observacao.strip():
            raise OperacaoNaoPermitidaException(
                "Observação é obrigatória para ajustes de estoque"
            )
        
        # Validar quantidade
        nova_quantidade = self.validators.validar_quantidade(nova_quantidade, permitir_zero=True)
        
        # Buscar produto
        produto = self.produto_repo.read(produto_id)
        if not produto:
            raise ProdutoNaoEncontradoException(f"Produto {produto_id} não encontrado")
        
        # Calcular diferença
        diferenca = nova_quantidade - produto.quantidade
        
        # Atualizar estoque
        self.produto_repo.atualizar_quantidade(produto_id, nova_quantidade)
        
        # Registrar movimento
        movimento = Movimento(
            produto_id=produto_id,
            tipo=TipoMovimento.AJUSTE,
            quantidade=diferenca,
            usuario_id=usuario_id,
            observacao=f"Ajuste de estoque: {observacao}"
        )
        
        movimento = self.movimento_repo.create(movimento)
        logger.info(
            f"Ajuste registrado: Produto {produto_id}, "
            f"Diferença: {diferenca:+d}, Novo total: {nova_quantidade}"
        )
        
        return movimento
    
    def listar_movimentos_produto(
        self,
        produto_id: int,
        limite: Optional[int] = None
    ) -> List[Movimento]:
        """
        Lista movimentos de um produto.
        
        Args:
            produto_id: ID do produto
            limite: Número máximo de movimentos
            
        Returns:
            Lista de movimentos
        """
        return self.movimento_repo.buscar_por_produto(produto_id, limite)
    
    def listar_movimentos_periodo(
        self,
        data_inicio: datetime,
        data_fim: datetime
    ) -> List[Movimento]:
        """
        Lista movimentos em um período.
        
        FUNCIONALIDADE DE CONSULTA/BUSCA 2: Movimentos por período
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            Lista de movimentos
        """
        if data_inicio > data_fim:
            raise ValidacaoException("Data inicial deve ser anterior à data final")
        
        return self.movimento_repo.buscar_por_periodo(data_inicio, data_fim)