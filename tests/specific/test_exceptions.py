# ===========================
# tests/specific/test_exceptions.py
# ===========================
"""
Testes específicos para exceções personalizadas (requisito: pelo menos 2 tipos).
"""
import pytest
from src.exceptions.custom_exceptions import (
    ProdutoNaoEncontradoException,
    EstoqueInsuficienteException,
    ValidacaoException,
    PrecoInvalidoException,
    QuantidadeInvalidaException,
    OperacaoNaoPermitidaException
)


class TestExceptions:
    """Testes específicos para lançamento de exceções."""
    
    def test_excecao_produto_nao_encontrado_mensagem(self, produto_service):
        """Testa exceção ProdutoNaoEncontrado com mensagem específica."""
        with pytest.raises(ProdutoNaoEncontradoException) as exc_info:
            produto_service.buscar_produto(99999)
        
        assert "99999" in str(exc_info.value)
        assert "não encontrado" in str(exc_info.value).lower()
    
    def test_excecao_estoque_insuficiente_detalhes(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Testa exceção EstoqueInsuficiente contém detalhes."""
        quantidade_disponivel = produto_sample.quantidade
        quantidade_solicitada = quantidade_disponivel + 100
        
        with pytest.raises(EstoqueInsuficienteException) as exc_info:
            movimento_service.registrar_saida(
                produto_id=produto_sample.id,
                quantidade=quantidade_solicitada,
                usuario_id=usuario_sample.id
            )
        
        mensagem = str(exc_info.value)
        assert "Disponível" in mensagem or "disponível" in mensagem
        assert str(quantidade_disponivel) in mensagem
    
    def test_excecao_validacao_preco_negativo(self):
        """Testa exceção de preço negativo."""
        from src.utils.validators import Validators
        
        with pytest.raises(PrecoInvalidoException) as exc_info:
            Validators.validar_preco(-50.00)
        
        assert "negativo" in str(exc_info.value).lower()
    
    def test_excecao_quantidade_invalida_tipo(self):
        """Testa exceção de quantidade com tipo errado."""
        from src.utils.validators import Validators
        
        with pytest.raises(QuantidadeInvalidaException) as exc_info:
            Validators.validar_quantidade(10.5)
        
        assert "inteiro" in str(exc_info.value).lower()
    
    def test_excecao_operacao_nao_permitida_desconto(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa exceção de operação não permitida no desconto."""
        produto = produto_service.criar_produto(
            nome="Produto Teste",
            preco=110.00,
            preco_custo=100.00,
            quantidade=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        with pytest.raises(OperacaoNaoPermitidaException) as exc_info:
            produto_service.aplicar_desconto(produto.id, 20.0)
        
        assert "custo" in str(exc_info.value).lower()
    
    def test_excecao_validacao_email_invalido(self):
        """Testa exceção de email inválido."""
        from src.utils.validators import Validators
        
        with pytest.raises(ValidacaoException) as exc_info:
            Validators.validar_email("email_sem_arroba")
        
        assert "inválido" in str(exc_info.value).lower()
    
    def test_excecao_recuperacao_depois_erro(
        self, movimento_service, produto_sample, usuario_sample, produto_repo
    ):
        """Testa recuperação de estado após exceção."""
        quantidade_inicial = produto_sample.quantidade
        
        # Tentar operação que vai falhar
        try:
            movimento_service.registrar_saida(
                produto_id=produto_sample.id,
                quantidade=9999,  # Muito mais que disponível
                usuario_id=usuario_sample.id
            )
        except EstoqueInsuficienteException:
            pass
        
        # Verificar que quantidade não foi alterada
        produto = produto_repo.read(produto_sample.id)
        assert produto.quantidade == quantidade_inicial