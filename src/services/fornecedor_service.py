# ===========================
# src/services/fornecedor_service.py
# ===========================
"""
Serviço de lógica de negócio para Fornecedores.
"""
from typing import List, Optional
from src.models.fornecedor import Fornecedor
from src.repositories.fornecedor_repository import FornecedorRepository
from src.utils.validators import Validators
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import (
    ValidacaoException, FornecedorNaoEncontradoException
)


logger = get_logger(__name__)


class FornecedorService:
    """Serviço para gerenciar fornecedores."""
    
    def __init__(self, fornecedor_repo: FornecedorRepository):
        """
        Inicializa serviço de fornecedores.
        
        Args:
            fornecedor_repo: Repository de fornecedores
        """
        self.fornecedor_repo = fornecedor_repo
        self.validators = Validators()
    
    def criar_fornecedor(
        self,
        nome: str,
        cnpj: str,
        email: str,
        telefone: str,
        endereco: Optional[str] = None,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        cep: Optional[str] = None,
        contato_principal: Optional[str] = None,
        prazo_entrega_dias: int = 7
    ) -> Fornecedor:
        """
        Cria novo fornecedor com validações.
        
        Args:
            nome: Nome do fornecedor
            cnpj: CNPJ do fornecedor
            email: Email de contato
            telefone: Telefone de contato
            endereco: Endereço
            cidade: Cidade
            estado: Estado (UF)
            cep: CEP
            contato_principal: Nome do contato principal
            prazo_entrega_dias: Prazo médio de entrega em dias
            
        Returns:
            Fornecedor criado
            
        Raises:
            ValidacaoException: Se validações falharem
        """
        # Validar campos obrigatórios
        nome = self.validators.validar_string_nao_vazia(nome, "Nome")
        cnpj = self.validators.validar_cnpj(cnpj)
        email = self.validators.validar_email(email)
        telefone = self.validators.validar_telefone(telefone)
        
        # Verificar CNPJ único
        fornecedor_existente = self.fornecedor_repo.buscar_por_cnpj(cnpj)
        if fornecedor_existente:
            raise ValidacaoException(f"Já existe fornecedor com CNPJ {cnpj}")
        
        # Validar prazo de entrega
        if prazo_entrega_dias < 0:
            raise ValidacaoException("Prazo de entrega não pode ser negativo")
        
        # Criar fornecedor
        fornecedor = Fornecedor(
            nome=nome,
            cnpj=cnpj,
            email=email,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cep=cep,
            contato_principal=contato_principal,
            prazo_entrega_dias=prazo_entrega_dias
        )
        
        fornecedor = self.fornecedor_repo.create(fornecedor)
        logger.info(f"Fornecedor criado: {fornecedor.id} - {fornecedor.nome}")
        
        return fornecedor
    
    def atualizar_fornecedor(self, fornecedor: Fornecedor) -> Fornecedor:
        """
        Atualiza fornecedor.
        
        Args:
            fornecedor: Fornecedor a ser atualizado
            
        Returns:
            Fornecedor atualizado
            
        Raises:
            FornecedorNaoEncontradoException: Se fornecedor não existir
        """
        # Verificar se existe
        fornecedor_existente = self.fornecedor_repo.read(fornecedor.id)
        if not fornecedor_existente:
            raise FornecedorNaoEncontradoException(f"Fornecedor {fornecedor.id} não encontrado")
        
        # Validações
        fornecedor.nome = self.validators.validar_string_nao_vazia(fornecedor.nome, "Nome")
        fornecedor.cnpj = self.validators.validar_cnpj(fornecedor.cnpj)
        fornecedor.email = self.validators.validar_email(fornecedor.email)
        fornecedor.telefone = self.validators.validar_telefone(fornecedor.telefone)
        
        # Atualizar
        fornecedor = self.fornecedor_repo.update(fornecedor)
        logger.info(f"Fornecedor atualizado: {fornecedor.id}")
        
        return fornecedor
    
    def deletar_fornecedor(self, fornecedor_id: int) -> bool:
        """
        Deleta fornecedor (soft delete).
        
        Args:
            fornecedor_id: ID do fornecedor
            
        Returns:
            True se deletado
        """
        fornecedor = self.fornecedor_repo.read(fornecedor_id)
        if not fornecedor:
            raise FornecedorNaoEncontradoException(f"Fornecedor {fornecedor_id} não encontrado")
        
        sucesso = self.fornecedor_repo.delete(fornecedor_id)
        if sucesso:
            logger.info(f"Fornecedor deletado: {fornecedor_id}")
        
        return sucesso
    
    def buscar_fornecedor(self, fornecedor_id: int) -> Fornecedor:
        """
        Busca fornecedor por ID.
        
        Args:
            fornecedor_id: ID do fornecedor
            
        Returns:
            Fornecedor encontrado
        """
        fornecedor = self.fornecedor_repo.read(fornecedor_id)
        if not fornecedor:
            raise FornecedorNaoEncontradoException(f"Fornecedor {fornecedor_id} não encontrado")
        
        return fornecedor
    
    def listar_fornecedores(self, incluir_inativos: bool = False) -> List[Fornecedor]:
        """
        Lista todos fornecedores.
        
        Args:
            incluir_inativos: Se deve incluir inativos
            
        Returns:
            Lista de fornecedores
        """
        return self.fornecedor_repo.list_all(incluir_inativos)