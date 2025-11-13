# ===========================
# src/models/usuario.py
# ===========================
"""
Model de Usuário.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Usuario:
    """Representa um usuário do sistema."""
    
    nome: str
    email: str
    senha_hash: str
    id: Optional[int] = None
    ativo: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Converte usuário para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }