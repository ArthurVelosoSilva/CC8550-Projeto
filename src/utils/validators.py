# ===========================
# src/utils/validators.py
# ===========================
"""
Validadores de dados do sistema.
"""
from typing import Any, Optional
from datetime import datetime, date
import re
from src.exceptions.custom_exceptions import ValidacaoException, PrecoInvalidoException, QuantidadeInvalidaException


class Validators:
    """Classe com métodos de validação."""
    
    @staticmethod
    def validar_preco(preco: float, permitir_zero: bool = False) -> float:
        """
        Valida valor de preço.
        
        Args:
            preco: Valor a validar
            permitir_zero: Se permite preço zero
            
        Returns:
            Preço validado
            
        Raises:
            PrecoInvalidoException: Se preço inválido
        """
        if not isinstance(preco, (int, float)):
            raise PrecoInvalidoException(f"Preço deve ser numérico: {preco}")
        
        if preco < 0:
            raise PrecoInvalidoException(f"Preço não pode ser negativo: {preco}")
        
        if not permitir_zero and preco == 0:
            raise PrecoInvalidoException("Preço não pode ser zero")
        
        return round(float(preco), 2)
    
    @staticmethod
    def validar_quantidade(quantidade: int, permitir_zero: bool = True) -> int:
        """
        Valida quantidade.
        
        Args:
            quantidade: Quantidade a validar
            permitir_zero: Se permite quantidade zero
            
        Returns:
            Quantidade validada
            
        Raises:
            QuantidadeInvalidaException: Se quantidade inválida
        """
        if not isinstance(quantidade, int):
            raise QuantidadeInvalidaException(f"Quantidade deve ser inteiro: {quantidade}")
        
        if quantidade < 0:
            raise QuantidadeInvalidaException(f"Quantidade não pode ser negativa: {quantidade}")
        
        if not permitir_zero and quantidade == 0:
            raise QuantidadeInvalidaException("Quantidade não pode ser zero")
        
        return quantidade
    
    @staticmethod
    def validar_email(email: str) -> str:
        """
        Valida formato de email.
        
        Args:
            email: Email a validar
            
        Returns:
            Email validado
            
        Raises:
            ValidacaoException: Se email inválido
        """
        if not email or not isinstance(email, str):
            raise ValidacaoException("Email não pode ser vazio")
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidacaoException(f"Email inválido: {email}")
        
        return email.lower().strip()
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> str:
        """
        Valida formato de CNPJ.
        
        Args:
            cnpj: CNPJ a validar
            
        Returns:
            CNPJ validado
            
        Raises:
            ValidacaoException: Se CNPJ inválido
        """
        if not cnpj:
            raise ValidacaoException("CNPJ não pode ser vazio")
        
        # Remove caracteres não numéricos
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        
        if len(cnpj_limpo) != 14:
            raise ValidacaoException(f"CNPJ deve ter 14 dígitos: {cnpj}")
        
        return cnpj_limpo
    
    @staticmethod
    def validar_telefone(telefone: str) -> str:
        """
        Valida formato de telefone.
        
        Args:
            telefone: Telefone a validar
            
        Returns:
            Telefone validado
            
        Raises:
            ValidacaoException: Se telefone inválido
        """
        if not telefone:
            raise ValidacaoException("Telefone não pode ser vazio")
        
        # Remove caracteres não numéricos
        telefone_limpo = re.sub(r'[^0-9]', '', telefone)
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValidacaoException(f"Telefone deve ter 10 ou 11 dígitos: {telefone}")
        
        return telefone_limpo
    
    @staticmethod
    def validar_string_nao_vazia(valor: str, campo: str) -> str:
        """
        Valida string não vazia.
        
        Args:
            valor: Valor a validar
            campo: Nome do campo
            
        Returns:
            String validada
            
        Raises:
            ValidacaoException: Se string vazia
        """
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ValidacaoException(f"{campo} não pode ser vazio")
        
        return valor.strip()
    
    @staticmethod
    def validar_data_validade(data_validade: Optional[date]) -> Optional[date]:
        """
        Valida data de validade.
        
        Args:
            data_validade: Data a validar
            
        Returns:
            Data validada
            
        Raises:
            ValidacaoException: Se data inválida
        """
        if data_validade is None:
            return None
        
        if not isinstance(data_validade, (date, datetime)):
            raise ValidacaoException("Data de validade inválida")
        
        if isinstance(data_validade, datetime):
            data_validade = data_validade.date()
        
        if data_validade < date.today():
            raise ValidacaoException(f"Data de validade não pode ser no passado: {data_validade}")
        
        return data_validade