# ===========================
# src/models/categoria.py
# ===========================
"""
Model de Categoria.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Categoria:
    """Representa uma categoria de produtos."""
    
    nome: str
    id: Optional[int] = None
    descricao: Optional[str] = None
    ativo: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Converte categoria para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }