# ===========================
# src/models/produto.py
# ===========================
"""
Model de Produto.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import date, datetime


@dataclass
class Produto:
    """Representa um produto no estoque."""
    
    nome: str
    preco: float
    quantidade: int
    categoria_id: int
    fornecedor_id: int
    id: Optional[int] = None
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    preco_custo: Optional[float] = None
    estoque_minimo: int = 10
    estoque_maximo: int = 1000
    localizacao: Optional[str] = None
    data_validade: Optional[date] = None
    ativo: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)
    data_atualizacao: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Converte produto para dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'preco': self.preco,
            'preco_custo': self.preco_custo,
            'quantidade': self.quantidade,
            'estoque_minimo': self.estoque_minimo,
            'estoque_maximo': self.estoque_maximo,
            'categoria_id': self.categoria_id,
            'fornecedor_id': self.fornecedor_id,
            'localizacao': self.localizacao,
            'data_validade': self.data_validade.isoformat() if self.data_validade else None,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }
    
    def calcular_margem_lucro(self) -> float:
        """
        Calcula margem de lucro do produto.
        
        Returns:
            Percentual de margem de lucro
        """
        if not self.preco_custo or self.preco_custo == 0:
            return 0.0
        
        margem = ((self.preco - self.preco_custo) / self.preco_custo) * 100
        return round(margem, 2)
    
    def esta_em_estoque_critico(self) -> bool:
        """Verifica se produto está em estoque crítico."""
        return self.quantidade <= self.estoque_minimo
    
    def esta_proximo_vencimento(self, dias: int = 30) -> bool:
        """
        Verifica se produto está próximo do vencimento.
        
        Args:
            dias: Número de dias para considerar próximo
            
        Returns:
            True se próximo do vencimento
        """
        if not self.data_validade:
            return False
        
        dias_restantes = (self.data_validade - date.today()).days
        return 0 <= dias_restantes <= dias