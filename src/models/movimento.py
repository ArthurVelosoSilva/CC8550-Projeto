# ===========================
# src/models/movimento.py
# ===========================
"""
Model de Movimento de Estoque.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class TipoMovimento(Enum):
    """Tipos de movimento de estoque."""
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"
    DEVOLUCAO = "DEVOLUCAO"
    TRANSFERENCIA = "TRANSFERENCIA"


@dataclass
class Movimento:
    """Representa um movimento de estoque."""
    
    produto_id: int
    tipo: TipoMovimento
    quantidade: int
    usuario_id: int
    id: Optional[int] = None
    observacao: Optional[str] = None
    data_movimento: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Converte movimento para dicionário."""
        return {
            'id': self.id,
            'produto_id': self.produto_id,
            'tipo': self.tipo.value if isinstance(self.tipo, TipoMovimento) else self.tipo,
            'quantidade': self.quantidade,
            'usuario_id': self.usuario_id,
            'observacao': self.observacao,
            'data_movimento': self.data_movimento.isoformat() if self.data_movimento else None
        }