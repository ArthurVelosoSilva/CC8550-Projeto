# ===========================
# tests/unit/test_validators.py
# ===========================
"""
Testes unitários para validadores.
"""
import pytest
from datetime import date, timedelta
from src.utils.validators import Validators
from src.exceptions.custom_exceptions import (
    ValidacaoException, PrecoInvalidoException, QuantidadeInvalidaException
)


class TestValidators:
    """Testes para classe Validators."""
    
    def test_validar_preco_valido(self):
        """Teste validação de preço válido."""
        preco = Validators.validar_preco(100.50)
        assert preco == 100.50
    
    def test_validar_preco_inteiro(self):
        """Teste validação de preço inteiro."""
        preco = Validators.validar_preco(100)
        assert preco == 100.00
    
    def test_validar_preco_negativo(self):
        """Teste validação de preço negativo."""
        with pytest.raises(PrecoInvalidoException):
            Validators.validar_preco(-10.00)
    
    def test_validar_preco_zero_nao_permitido(self):
        """Teste validação de preço zero quando não permitido."""
        with pytest.raises(PrecoInvalidoException):
            Validators.validar_preco(0.00, permitir_zero=False)
    
    def test_validar_preco_zero_permitido(self):
        """Teste validação de preço zero quando permitido."""
        preco = Validators.validar_preco(0.00, permitir_zero=True)
        assert preco == 0.00
    
    def test_validar_preco_tipo_invalido(self):
        """Teste validação de preço com tipo inválido."""
        with pytest.raises(PrecoInvalidoException):
            Validators.validar_preco("abc")
    
    def test_validar_quantidade_valida(self):
        """Teste validação de quantidade válida."""
        qtd = Validators.validar_quantidade(50)
        assert qtd == 50
    
    def test_validar_quantidade_negativa(self):
        """Teste validação de quantidade negativa."""
        with pytest.raises(QuantidadeInvalidaException):
            Validators.validar_quantidade(-5)
    
    def test_validar_quantidade_zero_permitido(self):
        """Teste validação de quantidade zero permitida."""
        qtd = Validators.validar_quantidade(0, permitir_zero=True)
        assert qtd == 0
    
    def test_validar_quantidade_zero_nao_permitido(self):
        """Teste validação de quantidade zero não permitida."""
        with pytest.raises(QuantidadeInvalidaException):
            Validators.validar_quantidade(0, permitir_zero=False)
    
    def test_validar_quantidade_tipo_invalido(self):
        """Teste validação de quantidade com tipo inválido."""
        with pytest.raises(QuantidadeInvalidaException):
            Validators.validar_quantidade(10.5)
    
    def test_validar_email_valido(self):
        """Teste validação de email válido."""
        email = Validators.validar_email("teste@example.com")
        assert email == "teste@example.com"
    
    def test_validar_email_invalido(self):
        """Teste validação de email inválido."""
        with pytest.raises(ValidacaoException):
            Validators.validar_email("email_invalido")
    
    def test_validar_email_vazio(self):
        """Teste validação de email vazio."""
        with pytest.raises(ValidacaoException):
            Validators.validar_email("")
    
    def test_validar_cnpj_valido(self):
        """Teste validação de CNPJ válido."""
        cnpj = Validators.validar_cnpj("12.345.678/0001-90")
        assert cnpj == "12345678000190"
    
    def test_validar_cnpj_invalido(self):
        """Teste validação de CNPJ com tamanho inválido."""
        with pytest.raises(ValidacaoException):
            Validators.validar_cnpj("123456")
    
    def test_validar_telefone_valido(self):
        """Teste validação de telefone válido."""
        tel = Validators.validar_telefone("(11) 98765-4321")
        assert tel == "11987654321"
    
    def test_validar_telefone_invalido(self):
        """Teste validação de telefone inválido."""
        with pytest.raises(ValidacaoException):
            Validators.validar_telefone("123")
    
    def test_validar_string_nao_vazia(self):
        """Teste validação de string não vazia."""
        texto = Validators.validar_string_nao_vazia("  Teste  ", "Campo")
        assert texto == "Teste"
    
    def test_validar_string_vazia(self):
        """Teste validação de string vazia."""
        with pytest.raises(ValidacaoException):
            Validators.validar_string_nao_vazia("", "Campo")
    
    def test_validar_data_validade_futura(self):
        """Teste validação de data de validade futura."""
        data_futura = date.today() + timedelta(days=30)
        data = Validators.validar_data_validade(data_futura)
        assert data == data_futura
    
    def test_validar_data_validade_passada(self):
        """Teste validação de data de validade passada."""
        data_passada = date.today() - timedelta(days=1)
        with pytest.raises(ValidacaoException):
            Validators.validar_data_validade(data_passada)
    
    def test_validar_data_validade_none(self):
        """Teste validação de data de validade None."""
        data = Validators.validar_data_validade(None)
        assert data is None