# ===========================
# tests/integration/test_produto_integration.py
# ===========================
"""
Testes de integração para fluxo completo de produtos.
"""
import pytest
from datetime import date, datetime, timedelta
from src.models.produto import Produto
from src.models.categoria import Categoria
from src.models.fornecedor import Fornecedor


class TestProdutoIntegration:
    """Testes de integração do fluxo de produtos."""
    
    def test_fluxo_completo_criar_atualizar_deletar_produto(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Teste fluxo completo: criar -> atualizar -> deletar produto."""
        produto = produto_service.criar_produto(
            nome="Produto Integração",
            preco=200.00,
            quantidade=30,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id,
            codigo="INT-001"
        )
        
        assert produto.id is not None
        assert produto.nome == "Produto Integração"
        
        produto.nome = "Produto Atualizado"
        produto.preco = 250.00
        produto_atualizado = produto_service.atualizar_produto(produto)
        
        assert produto_atualizado.nome == "Produto Atualizado"
        assert produto_atualizado.preco == 250.00
        
        resultado = produto_service.deletar_produto(produto.id)
        assert resultado is True
    
    def test_fluxo_aplicar_desconto_e_verificar_margem(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Teste aplicar desconto e verificar margem de lucro."""
        produto = produto_service.criar_produto(
            nome="Produto Desconto",
            preco=200.00,
            preco_custo=100.00,
            quantidade=20,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        produto_com_desconto = produto_service.aplicar_desconto(produto.id, 20.0)
        
        assert produto_com_desconto.preco == 160.00
        
        margem = produto_com_desconto.calcular_margem_lucro()
        assert margem == 60.0
    
    def test_fluxo_busca_produtos_com_filtros(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Teste busca de produtos com múltiplos filtros."""
        for i in range(5):
            produto_service.criar_produto(
                nome=f"Produto Filtro {i}",
                preco=100.00 + (i * 50),
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
        
        produtos = produto_service.listar_produtos(
            categoria_id=categoria_sample.id,
            preco_min=150.0,
            preco_max=250.0,
            ordenar_por='preco',
            ordem='ASC'
        )
        
        assert len(produtos) > 0
        assert all(150 <= p.preco <= 250 for p in produtos)
        
        precos = [p.preco for p in produtos]
        assert precos == sorted(precos)
    
    def test_integracao_produto_com_data_validade(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Teste integração de produto com data de validade."""
        data_proxima = date.today() + timedelta(days=15)
        
        produto = produto_service.criar_produto(
            nome="Produto Perecível",
            preco=50.00,
            quantidade=100,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id,
            data_validade=data_proxima
        )
        
        alertas = produto_service.verificar_produtos_criticos()
        
        alertas_vencimento = [a for a in alertas if a.get('tipo_alerta') == 'PROXIMO_VENCIMENTO']
        assert len(alertas_vencimento) > 0


class TestMovimentoIntegration:
    """Testes de integração para movimentos de estoque."""
    
    def test_fluxo_completo_entrada_saida_estoque(
        self, movimento_service, produto_sample, usuario_sample, produto_repo
    ):
        """Teste fluxo completo: entrada -> consulta -> saída."""
        quantidade_inicial = produto_sample.quantidade
        
        mov_entrada = movimento_service.registrar_entrada(
            produto_id=produto_sample.id,
            quantidade=20,
            usuario_id=usuario_sample.id,
            observacao="Compra"
        )
        
        assert mov_entrada.quantidade == 20
        
        produto_atualizado = produto_repo.read(produto_sample.id)
        assert produto_atualizado.quantidade == quantidade_inicial + 20
        
        mov_saida = movimento_service.registrar_saida(
            produto_id=produto_sample.id,
            quantidade=10,
            usuario_id=usuario_sample.id,
            observacao="Venda"
        )
        
        assert mov_saida.quantidade == 10
        
        produto_final = produto_repo.read(produto_sample.id)
        assert produto_final.quantidade == quantidade_inicial + 20 - 10
    
    def test_fluxo_ajuste_estoque_com_observacao(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Teste ajuste de estoque com observação obrigatória."""
        mov_ajuste = movimento_service.registrar_ajuste(
            produto_id=produto_sample.id,
            nova_quantidade=50,
            usuario_id=usuario_sample.id,
            observacao="Inventário realizado"
        )
        
        assert mov_ajuste is not None
        assert "Ajuste de estoque" in mov_ajuste.observacao
    
    def test_fluxo_historico_movimentos_produto(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Teste histórico completo de movimentos de um produto."""
        movimento_service.registrar_entrada(produto_sample.id, 10, usuario_sample.id)
        movimento_service.registrar_saida(produto_sample.id, 5, usuario_sample.id)
        movimento_service.registrar_entrada(produto_sample.id, 20, usuario_sample.id)
        
        movimentos = movimento_service.listar_movimentos_produto(produto_sample.id)
        
        assert len(movimentos) >= 3
        
        tipos = [m.tipo.value for m in movimentos]
        assert 'ENTRADA' in tipos
        assert 'SAIDA' in tipos
    
    def test_fluxo_movimentos_por_periodo(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Teste consulta de movimentos por período."""
        movimento_service.registrar_entrada(produto_sample.id, 15, usuario_sample.id)
        
        data_inicio = datetime.now() - timedelta(hours=1)
        data_fim = datetime.now() + timedelta(hours=1)
        
        movimentos = movimento_service.listar_movimentos_periodo(data_inicio, data_fim)
        
        assert len(movimentos) > 0


class TestRelatorioIntegration:
    """Testes de integração para geração de relatórios."""
    
    def test_gerar_relatorio_estoque_completo(
        self, relatorio_service, produto_sample, categoria_sample, fornecedor_sample
    ):
        """Teste geração de relatório completo de estoque."""
        relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        
        assert 'data_geracao' in relatorio
        assert 'total_produtos' in relatorio
        assert 'valor_total_estoque' in relatorio
        assert relatorio['total_produtos'] >= 1
        assert len(relatorio['produtos']) >= 1
    
    def test_gerar_relatorio_movimentacao(
        self, relatorio_service, movimento_service, produto_sample, usuario_sample
    ):
        """Teste geração de relatório de movimentação."""
        movimento_service.registrar_entrada(produto_sample.id, 10, usuario_sample.id)
        movimento_service.registrar_saida(produto_sample.id, 5, usuario_sample.id)
        
        data_inicio = datetime.now() - timedelta(hours=1)
        data_fim = datetime.now() + timedelta(hours=1)
        
        relatorio = relatorio_service.gerar_relatorio_movimentacao(data_inicio, data_fim)
        
        assert 'total_movimentos' in relatorio
        assert 'movimentos_por_tipo' in relatorio
        assert relatorio['total_movimentos'] >= 2
    
    def test_gerar_relatorio_categorias(
        self, relatorio_service, produto_sample, categoria_sample
    ):
        """Teste geração de relatório por categorias."""
        relatorio = relatorio_service.gerar_relatorio_categorias()
        
        assert 'total_categorias' in relatorio
        assert 'categorias' in relatorio
        assert len(relatorio['categorias']) >= 1
        
        cat_dados = relatorio['categorias'][0]
        assert 'nome' in cat_dados
        assert 'total_produtos' in cat_dados
        assert 'valor_total' in cat_dados
    
    def test_gerar_relatorio_fornecedores(
        self, relatorio_service, produto_sample, fornecedor_sample
    ):
        """Teste geração de relatório por fornecedores."""
        relatorio = relatorio_service.gerar_relatorio_fornecedores()
        
        assert 'total_fornecedores' in relatorio
        assert 'fornecedores' in relatorio
        assert len(relatorio['fornecedores']) >= 1
        
        forn_dados = relatorio['fornecedores'][0]
        assert 'nome' in forn_dados
        assert 'cnpj' in forn_dados
        assert 'total_produtos_fornecidos' in forn_dados
    
    def test_exportar_relatorio_json(
        self, relatorio_service, produto_sample, tmp_path
    ):
        """Teste exportação de relatório para JSON."""
        relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        
        filepath = tmp_path / "relatorio_teste.json"
        sucesso = relatorio_service.exportar_relatorio_json(relatorio, str(filepath))
        
        assert sucesso is True
        assert filepath.exists()
    
    def test_exportar_relatorio_csv(
        self, relatorio_service, produto_sample, tmp_path
    ):
        """Teste exportação de relatório para CSV."""
        relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        
        filepath = tmp_path / "relatorio_teste.csv"
        sucesso = relatorio_service.exportar_relatorio_csv(relatorio, str(filepath))
        
        assert sucesso is True
        assert filepath.exists()


class TestFornecedorIntegration:
    """Testes de integração para fornecedores."""
    
    def test_fluxo_completo_fornecedor(self, fornecedor_service):
        """Teste fluxo completo de fornecedor."""
        fornecedor = fornecedor_service.criar_fornecedor(
            nome="Fornecedor Teste",
            cnpj="99999999000199",
            email="fornecedor@teste.com",
            telefone="11988888888",
            cidade="São Paulo",
            estado="SP",
            prazo_entrega_dias=10
        )
        
        assert fornecedor.id is not None
        
        fornecedor_buscado = fornecedor_service.buscar_fornecedor(fornecedor.id)
        assert fornecedor_buscado.nome == "Fornecedor Teste"
        
        fornecedor.prazo_entrega_dias = 5
        fornecedor_atualizado = fornecedor_service.atualizar_fornecedor(fornecedor)
        assert fornecedor_atualizado.prazo_entrega_dias == 5
        
        resultado = fornecedor_service.deletar_fornecedor(fornecedor.id)
        assert resultado is True
    
    def test_listar_fornecedores_ativos(self, fornecedor_service, fornecedor_sample):
        """Teste listagem de fornecedores ativos."""
        fornecedores = fornecedor_service.listar_fornecedores(incluir_inativos=False)
        
        assert len(fornecedores) > 0
        assert all(f.ativo for f in fornecedores)


class TestIntegracaoBancoDados:
    """Testes de integração com banco de dados."""
    
    def test_transacao_multiplas_entidades(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Teste transação envolvendo múltiplas entidades."""
        produtos_criados = []
        
        for i in range(5):
            produto = produto_service.criar_produto(
                nome=f"Produto Transação {i}",
                preco=100.00 * (i + 1),
                quantidade=10 * (i + 1),
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
            produtos_criados.append(produto)
        
        assert len(produtos_criados) == 5
        assert all(p.id is not None for p in produtos_criados)
        
        produtos_categoria = produto_service.listar_produtos(
            categoria_id=categoria_sample.id
        )
        
        assert len(produtos_categoria) >= 5
    
    def test_consistencia_estoque_apos_multiplas_operacoes(
        self, movimento_service, produto_sample, usuario_sample, produto_repo
    ):
        """Teste consistência do estoque após múltiplas operações."""
        quantidade_inicial = produto_sample.quantidade
        
        movimento_service.registrar_entrada(produto_sample.id, 50, usuario_sample.id)
        movimento_service.registrar_saida(produto_sample.id, 20, usuario_sample.id)
        movimento_service.registrar_entrada(produto_sample.id, 10, usuario_sample.id)
        movimento_service.registrar_saida(produto_sample.id, 15, usuario_sample.id)
        
        quantidade_esperada = quantidade_inicial + 25
        
        produto_final = produto_repo.read(produto_sample.id)
        
        assert produto_final.quantidade == quantidade_esperada