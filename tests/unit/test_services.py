# ===========================
# tests/unit/test_services.py
# ===========================
"""
Testes unitários para services com mocks.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date
from src.services.produto_service import ProdutoService
from src.services.fornecedor_service import FornecedorService
from src.services.movimento_service import MovimentoService
from src.models.produto import Produto
from src.models.categoria import Categoria
from src.models.fornecedor import Fornecedor
from src.exceptions.custom_exceptions import (
    ValidacaoException,
    ProdutoNaoEncontradoException,
    CategoriaNaoEncontradaException,
    EstoqueInsuficienteException,
    OperacaoNaoPermitidaException
)


class TestProdutoServiceMocks:
    """Testes para ProdutoService usando mocks."""
    
    def test_criar_produto_com_validacoes(self):
        """Teste criação de produto com validações usando mocks."""
        # Arrange
        produto_repo_mock = Mock()
        categoria_repo_mock = Mock()
        fornecedor_repo_mock = Mock()
        
        categoria_mock = Mock(spec=Categoria)
        categoria_mock.id = 1
        categoria_mock.ativo = True
        categoria_mock.nome = "Eletrônicos"
        
        fornecedor_mock = Mock(spec=Fornecedor)
        fornecedor_mock.id = 1
        fornecedor_mock.ativo = True
        fornecedor_mock.nome = "Fornecedor Teste"
        
        categoria_repo_mock.read.return_value = categoria_mock
        fornecedor_repo_mock.read.return_value = fornecedor_mock
        produto_repo_mock.buscar_por_codigo.return_value = None
        
        produto_criado = Mock(spec=Produto)
        produto_criado.id = 1
        produto_criado.nome = "Produto Teste"
        produto_repo_mock.create.return_value = produto_criado
        
        service = ProdutoService(produto_repo_mock, categoria_repo_mock, fornecedor_repo_mock)
        
        # Act
        resultado = service.criar_produto(
            nome="Produto Teste",
            preco=100.00,
            quantidade=10,
            categoria_id=1,
            fornecedor_id=1
        )
        
        # Assert
        assert resultado.id == 1
        produto_repo_mock.create.assert_called_once()
        categoria_repo_mock.read.assert_called_once_with(1)
        fornecedor_repo_mock.read.assert_called_once_with(1)
    
    def test_criar_produto_categoria_inexistente(self):
        """Teste criação de produto com categoria inexistente."""
        produto_repo_mock = Mock()
        categoria_repo_mock = Mock()
        fornecedor_repo_mock = Mock()
        
        categoria_repo_mock.read.return_value = None
        
        service = ProdutoService(produto_repo_mock, categoria_repo_mock, fornecedor_repo_mock)
        
        with pytest.raises(CategoriaNaoEncontradaException):
            service.criar_produto(
                nome="Produto",
                preco=100.00,
                quantidade=10,
                categoria_id=999,
                fornecedor_id=1
            )
    
    def test_aplicar_desconto_sucesso(self):
        """Teste aplicação de desconto com sucesso."""
        produto_repo_mock = Mock()
        categoria_repo_mock = Mock()
        fornecedor_repo_mock = Mock()
        
        produto_mock = Mock(spec=Produto)
        produto_mock.id = 1
        produto_mock.preco = 100.00
        produto_mock.preco_custo = 50.00
        
        produto_repo_mock.read.return_value = produto_mock
        produto_repo_mock.update.return_value = produto_mock
        
        service = ProdutoService(produto_repo_mock, categoria_repo_mock, fornecedor_repo_mock)
        
        # Aplicar 10% de desconto
        resultado = service.aplicar_desconto(1, 10.0)
        
        assert produto_mock.preco == 90.00
        produto_repo_mock.update.assert_called_once()
    
    def test_aplicar_desconto_acima_limite(self):
        """Teste aplicação de desconto acima do limite."""
        produto_repo_mock = Mock()
        categoria_repo_mock = Mock()
        fornecedor_repo_mock = Mock()
        
        service = ProdutoService(produto_repo_mock, categoria_repo_mock, fornecedor_repo_mock)
        
        with pytest.raises(ValidacaoException):
            service.aplicar_desconto(1, 50.0)  # Acima de 30%


class TestMovimentoServiceMocks:
    """Testes para MovimentoService usando mocks."""
    
    def test_registrar_entrada_sucesso(self):
        """Teste registro de entrada com sucesso."""
        movimento_repo_mock = Mock()
        produto_repo_mock = Mock()
        
        produto_mock = Mock(spec=Produto)
        produto_mock.id = 1
        produto_mock.quantidade = 10
        produto_mock.estoque_maximo = 100
        
        produto_repo_mock.read.return_value = produto_mock
        produto_repo_mock.atualizar_quantidade.return_value = True
        
        from src.models.movimento import Movimento
        movimento_mock = Mock(spec=Movimento)
        movimento_mock.id = 1
        movimento_repo_mock.create.return_value = movimento_mock
        
        service = MovimentoService(movimento_repo_mock, produto_repo_mock)
        
        resultado = service.registrar_entrada(1, 5, 1)
        
        assert resultado.id == 1
        produto_repo_mock.atualizar_quantidade.assert_called_once_with(1, 15)
    
    def test_registrar_saida_estoque_insuficiente(self):
        """Teste registro de saída com estoque insuficiente."""
        movimento_repo_mock = Mock()
        produto_repo_mock = Mock()
        
        produto_mock = Mock(spec=Produto)
        produto_mock.id = 1
        produto_mock.quantidade = 5
        
        produto_repo_mock.read.return_value = produto_mock
        
        service = MovimentoService(movimento_repo_mock, produto_repo_mock)
        
        with pytest.raises(EstoqueInsuficienteException):
            service.registrar_saida(1, 10, 1)  # Tentar retirar mais que disponível