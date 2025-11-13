# ===========================
# src/models/fornecedor.py
# ===========================
"""
Model de Fornecedor.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Fornecedor:
    """Representa um fornecedor."""
    
    nome: str
    cnpj: str
    email: str
    telefone: str
    id: Optional[int] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    contato_principal: Optional[str] = None
    prazo_entrega_dias: int = 7
    ativo: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Converte fornecedor para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'contato_principal': self.contato_principal,
            'prazo_entrega_dias': self.prazo_entrega_dias,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }