# ===========================
# src/exceptions/custom_exceptions.py
# ===========================
"""
Exceções personalizadas do sistema.
"""


class EstoqueException(Exception):
    """Exceção base do sistema de estoque."""
    pass


class ProdutoNaoEncontradoException(EstoqueException):
    """Produto não encontrado no sistema."""
    pass


class EstoqueInsuficienteException(EstoqueException):
    """Estoque insuficiente para operação."""
    pass


class ValidacaoException(EstoqueException):
    """Erro de validação de dados."""
    pass


class FornecedorNaoEncontradoException(EstoqueException):
    """Fornecedor não encontrado."""
    pass


class CategoriaNaoEncontradaException(EstoqueException):
    """Categoria não encontrada."""
    pass


class PrecoInvalidoException(ValidacaoException):
    """Preço inválido."""
    pass


class QuantidadeInvalidaException(ValidacaoException):
    """Quantidade inválida."""
    pass


class DatabaseException(EstoqueException):
    """Erro relacionado ao banco de dados."""
    pass


class OperacaoNaoPermitidaException(EstoqueException):
    """Operação não permitida pelas regras de negócio."""
    pass