# ===========================
# src/services/relatorio_service.py
# ===========================
"""
Serviço para geração de relatórios.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.movimento_repository import MovimentoRepository
from src.repositories.categoria_repository import CategoriaRepository
from src.repositories.fornecedor_repository import FornecedorRepository
from src.models.movimento import TipoMovimento
from src.utils.logger import get_logger
from src.utils.file_handler import FileHandler


logger = get_logger(__name__)


class RelatorioService:
    """Serviço para geração de relatórios e análises."""
    
    def __init__(
        self,
        produto_repo: ProdutoRepository,
        movimento_repo: MovimentoRepository,
        categoria_repo: CategoriaRepository,
        fornecedor_repo: FornecedorRepository
    ):
        """
        Inicializa serviço de relatórios.
        
        Args:
            produto_repo: Repository de produtos
            movimento_repo: Repository de movimentos
            categoria_repo: Repository de categorias
            fornecedor_repo: Repository de fornecedores
        """
        self.produto_repo = produto_repo
        self.movimento_repo = movimento_repo
        self.categoria_repo = categoria_repo
        self.fornecedor_repo = fornecedor_repo
        self.file_handler = FileHandler()
    
    def gerar_relatorio_estoque_atual(self) -> Dict[str, Any]:
        """
        Gera relatório do estoque atual.
        
        Returns:
            Dicionário com informações do estoque
        """
        produtos = self.produto_repo.list_all()
        
        valor_total = sum(p.preco * p.quantidade for p in produtos)
        valor_custo_total = sum(
            (p.preco_custo or 0) * p.quantidade for p in produtos if p.preco_custo
        )
        
        produtos_criticos = [p for p in produtos if p.esta_em_estoque_critico()]
        
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'total_produtos': len(produtos),
            'total_itens_estoque': sum(p.quantidade for p in produtos),
            'valor_total_estoque': round(valor_total, 2),
            'valor_custo_total': round(valor_custo_total, 2),
            'margem_lucro_media': round(
                ((valor_total - valor_custo_total) / valor_custo_total * 100) 
                if valor_custo_total > 0 else 0, 2
            ),
            'produtos_criticos': len(produtos_criticos),
            'produtos': [p.to_dict() for p in produtos]
        }
        
        logger.info("Relatório de estoque atual gerado")
        return relatorio
    
    def gerar_relatorio_movimentacao(
        self,
        data_inicio: datetime,
        data_fim: datetime
    ) -> Dict[str, Any]:
        """
        Gera relatório de movimentação em período.
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            Dicionário com análise de movimentações
        """
        movimentos = self.movimento_repo.buscar_por_periodo(data_inicio, data_fim)
        
        # Agrupar por tipo
        por_tipo = defaultdict(lambda: {'quantidade': 0, 'total_itens': 0})
        
        for mov in movimentos:
            tipo = mov.tipo.value if isinstance(mov.tipo, TipoMovimento) else mov.tipo
            por_tipo[tipo]['quantidade'] += 1
            por_tipo[tipo]['total_itens'] += abs(mov.quantidade)
        
        # Produtos mais movimentados
        por_produto = defaultdict(int)
        for mov in movimentos:
            por_produto[mov.produto_id] += abs(mov.quantidade)
        
        top_produtos = sorted(por_produto.items(), key=lambda x: x[1], reverse=True)[:10]
        
        produtos_info = []
        for produto_id, total in top_produtos:
            produto = self.produto_repo.read(produto_id)
            if produto:
                produtos_info.append({
                    'produto_id': produto_id,
                    'nome': produto.nome,
                    'total_movimentado': total
                })
        
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat()
            },
            'total_movimentos': len(movimentos),
            'movimentos_por_tipo': dict(por_tipo),
            'top_10_produtos_movimentados': produtos_info,
            'movimentos': [m.to_dict() for m in movimentos]
        }
        
        logger.info(f"Relatório de movimentação gerado: {len(movimentos)} movimentos")
        return relatorio
    
    def gerar_relatorio_categorias(self) -> Dict[str, Any]:
        """
        Gera relatório por categoria.
        
        Returns:
            Análise por categorias
        """
        categorias = self.categoria_repo.list_all()
        dados_categorias = []
        
        for categoria in categorias:
            produtos = self.produto_repo.buscar_por_categoria(categoria.id)
            
            total_produtos = len(produtos)
            total_itens = sum(p.quantidade for p in produtos)
            valor_total = sum(p.preco * p.quantidade for p in produtos)
            
            dados_categorias.append({
                'categoria_id': categoria.id,
                'nome': categoria.nome,
                'total_produtos': total_produtos,
                'total_itens_estoque': total_itens,
                'valor_total': round(valor_total, 2),
                'produtos': [p.to_dict() for p in produtos]
            })
        
        # Ordenar por valor total
        dados_categorias.sort(key=lambda x: x['valor_total'], reverse=True)
        
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'total_categorias': len(categorias),
            'categorias': dados_categorias
        }
        
        logger.info("Relatório por categorias gerado")
        return relatorio
    
    def gerar_relatorio_fornecedores(self) -> Dict[str, Any]:
        """
        Gera relatório por fornecedor.
        
        Returns:
            Análise por fornecedores
        """
        fornecedores = self.fornecedor_repo.list_all()
        dados_fornecedores = []
        
        for fornecedor in fornecedores:
            produtos = self.produto_repo.buscar_com_filtros(fornecedor_id=fornecedor.id)
            
            total_produtos = len(produtos)
            total_itens = sum(p.quantidade for p in produtos)
            valor_total = sum(p.preco * p.quantidade for p in produtos)
            
            dados_fornecedores.append({
                'fornecedor_id': fornecedor.id,
                'nome': fornecedor.nome,
                'cnpj': fornecedor.cnpj,
                'total_produtos_fornecidos': total_produtos,
                'total_itens_estoque': total_itens,
                'valor_total_estoque': round(valor_total, 2),
                'prazo_entrega_dias': fornecedor.prazo_entrega_dias,
                'produtos': [p.to_dict() for p in produtos]
            })
        
        # Ordenar por valor total
        dados_fornecedores.sort(key=lambda x: x['valor_total_estoque'], reverse=True)
        
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'total_fornecedores': len(fornecedores),
            'fornecedores': dados_fornecedores
        }
        
        logger.info("Relatório por fornecedores gerado")
        return relatorio
    
    def exportar_relatorio_json(self, relatorio: Dict[str, Any], filepath: str) -> bool:
        """
        Exporta relatório para JSON.
        
        Args:
            relatorio: Dados do relatório
            filepath: Caminho do arquivo
            
        Returns:
            True se sucesso
        """
        return self.file_handler.exportar_json([relatorio], filepath)
    
    def exportar_relatorio_csv(self, relatorio: Dict[str, Any], filepath: str) -> bool:
        """
        Exporta relatório para CSV.
        
        Args:
            relatorio: Dados do relatório
            filepath: Caminho do arquivo
            
        Returns:
            True se sucesso
        """
        # Extrair produtos ou movimentos do relatório
        if 'produtos' in relatorio:
            dados = relatorio['produtos']
        elif 'movimentos' in relatorio:
            dados = relatorio['movimentos']
        else:
            logger.warning("Relatório não contém dados exportáveis para CSV")
            return False
        
        return self.file_handler.exportar_csv(dados, filepath)