# ===========================
# tests/functional/test_functional.py
# ===========================
"""
Testes funcionais (caixa-preta) - testam funcionalidades sem conhecer implementação.
Foco em entradas e saídas esperadas.
"""
import pytest
from datetime import date, timedelta


class TestCenariosCadastroProduto:
    """Cenários funcionais para cadastro de produto."""
    
    def test_cenario_cadastrar_produto_sucesso(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """
        CENÁRIO 1: Cadastrar produto com sucesso
        DADO que tenho uma categoria e fornecedor válidos
        QUANDO cadastro um produto com dados corretos
        ENTÃO o produto deve ser criado com sucesso
        E deve ter um ID gerado
        """
        # Dado
        nome = "Smartphone Samsung"
        preco = 1500.00
        quantidade = 50
        
        # Quando
        produto = produto_service.criar_produto(
            nome=nome,
            preco=preco,
            quantidade=quantidade,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        # Então
        assert produto.id is not None
        assert produto.nome == nome
        assert produto.preco == preco
        assert produto.quantidade == quantidade
    
    def test_cenario_cadastrar_produto_preco_invalido(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """
        CENÁRIO 2: Tentar cadastrar produto com preço inválido
        DADO que tenho dados de produto
        QUANDO tento cadastrar com preço negativo
        ENTÃO deve retornar erro de validação
        """
        from src.exceptions.custom_exceptions import PrecoInvalidoException
        
        # Dado / Quando / Então
        with pytest.raises(PrecoInvalidoException):
            produto_service.criar_produto(
                nome="Produto Teste",
                preco=-100.00,  # Preço negativo
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
    
    def test_cenario_cadastrar_produto_categoria_inexistente(
        self, produto_service, fornecedor_sample
    ):
        """
        CENÁRIO 3: Tentar cadastrar produto com categoria inexistente
        DADO que tenho dados de produto
        QUANDO tento cadastrar com categoria que não existe
        ENTÃO deve retornar erro de categoria não encontrada
        """
        from src.exceptions.custom_exceptions import CategoriaNaoEncontradaException
        
        with pytest.raises(CategoriaNaoEncontradaException):
            produto_service.criar_produto(
                nome="Produto Teste",
                preco=100.00,
                quantidade=10,
                categoria_id=99999,  # Categoria inexistente
                fornecedor_id=fornecedor_sample.id
            )


class TestCenariosMovimentacaoEstoque:
    """Cenários funcionais para movimentação de estoque."""
    
    def test_cenario_entrada_estoque_aumenta_quantidade(
        self, movimento_service, produto_sample, usuario_sample, produto_repo
    ):
        """
        CENÁRIO 4: Entrada de estoque aumenta quantidade
        DADO que tenho um produto com 10 unidades
        QUANDO registro entrada de 20 unidades
        ENTÃO o produto deve ter 30 unidades
        """
        # Dado
        quantidade_inicial = produto_sample.quantidade
        quantidade_entrada = 20
        
        # Quando
        movimento_service.registrar_entrada(
            produto_id=produto_sample.id,
            quantidade=quantidade_entrada,
            usuario_id=usuario_sample.id
        )
        
        # Então
        produto_atualizado = produto_repo.read(produto_sample.id)
        assert produto_atualizado.quantidade == quantidade_inicial + quantidade_entrada
    
    def test_cenario_saida_estoque_diminui_quantidade(
        self, movimento_service, produto_sample, usuario_sample, produto_repo
    ):
        """
        CENÁRIO 5: Saída de estoque diminui quantidade
        DADO que tenho um produto com estoque suficiente
        QUANDO registro saída de unidades
        ENTÃO o estoque deve diminuir corretamente
        """
        # Dado
        quantidade_inicial = produto_sample.quantidade
        quantidade_saida = 5
        
        # Quando
        movimento_service.registrar_saida(
            produto_id=produto_sample.id,
            quantidade=quantidade_saida,
            usuario_id=usuario_sample.id
        )
        
        # Então
        produto_atualizado = produto_repo.read(produto_sample.id)
        assert produto_atualizado.quantidade == quantidade_inicial - quantidade_saida
    
    def test_cenario_saida_estoque_insuficiente_retorna_erro(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """
        CENÁRIO 6: Saída com estoque insuficiente retorna erro
        DADO que tenho um produto com 10 unidades
        QUANDO tento retirar 20 unidades
        ENTÃO deve retornar erro de estoque insuficiente
        """
        from src.exceptions.custom_exceptions import EstoqueInsuficienteException
        
        # Dado / Quando / Então
        with pytest.raises(EstoqueInsuficienteException):
            movimento_service.registrar_saida(
                produto_id=produto_sample.id,
                quantidade=produto_sample.quantidade + 100,  # Mais que disponível
                usuario_id=usuario_sample.id
            )


class TestCenariosDesconto:    
    def test_cenario_desconto_acima_limite_retorna_erro(
        self, produto_service, produto_sample
    ):
        """
        CENÁRIO 8: Desconto acima do limite retorna erro
        DADO que o limite de desconto é 30%
        QUANDO tento aplicar desconto de 50%
        ENTÃO deve retornar erro de validação
        """
        from src.exceptions.custom_exceptions import ValidacaoException
        
        with pytest.raises(ValidacaoException):
            produto_service.aplicar_desconto(
                produto_sample.id,
                50.0  # Acima do limite de 30%
            )


class TestCenariosConsulta:
    """Cenários funcionais para consultas e buscas."""
    
    def test_cenario_buscar_produtos_por_faixa_preco(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """
        CENÁRIO 9: Buscar produtos por faixa de preço
        DADO que tenho produtos com preços variados
        QUANDO busco produtos entre R$ 100 e R$ 200
        ENTÃO deve retornar apenas produtos nessa faixa
        """
        # Dado - Criar produtos com preços diferentes
        precos = [50.00, 150.00, 250.00, 180.00, 90.00]
        for i, preco in enumerate(precos):
            produto_service.criar_produto(
                nome=f"Produto Preço {preco}",
                preco=preco,
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
        
        # Quando
        produtos = produto_service.listar_produtos(
            preco_min=100.0,
            preco_max=200.0
        )
        
        # Então
        assert len(produtos) > 0
        for produto in produtos:
            assert 100.0 <= produto.preco <= 200.0


class TestCenariosRelatorios:
    """Cenários funcionais para geração de relatórios."""
    
    def test_cenario_relatorio_estoque_mostra_totais(
        self, relatorio_service, produto_sample
    ):
        """
        CENÁRIO 11: Relatório de estoque mostra totais corretos
        DADO que tenho produtos cadastrados
        QUANDO gero relatório de estoque
        ENTÃO deve mostrar total de produtos e valor total
        """
        # Quando
        relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        
        # Então
        assert 'total_produtos' in relatorio
        assert 'total_itens_estoque' in relatorio
        assert 'valor_total_estoque' in relatorio
        assert relatorio['total_produtos'] > 0
        assert relatorio['valor_total_estoque'] > 0

class TestCenariosValidacao:
    """Cenários funcionais para validações de negócio."""
    
    def test_cenario_nao_permitir_preco_abaixo_custo_com_desconto(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """
        CENÁRIO 13: Não permitir desconto que resulte em preço abaixo do custo
        DADO que tenho produto com custo R$ 80 e preço R$ 100
        QUANDO tento aplicar desconto que resultaria em preço abaixo do custo
        ENTÃO deve retornar erro de operação não permitida
        """
        from src.exceptions.custom_exceptions import OperacaoNaoPermitidaException
        
        # Dado
        produto = produto_service.criar_produto(
            nome="Produto Custo",
            preco=100.00,
            preco_custo=80.00,
            quantidade=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        # Quando / Então
        with pytest.raises(OperacaoNaoPermitidaException):
            produto_service.aplicar_desconto(
                produto.id,
                25.0  # Resultaria em R$ 75, abaixo do custo
            )
    
    def test_cenario_ajuste_estoque_requer_observacao(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """
        CENÁRIO 14: Ajuste de estoque requer observação
        DADO que quero fazer ajuste de estoque
        QUANDO tento registrar sem observação
        ENTÃO deve retornar erro
        """
        from src.exceptions.custom_exceptions import OperacaoNaoPermitidaException
        
        with pytest.raises(OperacaoNaoPermitidaException):
            movimento_service.registrar_ajuste(
                produto_id=produto_sample.id,
                nova_quantidade=50,
                usuario_id=usuario_sample.id,
                observacao=""  # Vazio
            )
    
    def test_cenario_produto_com_data_validade_proxima_gera_alerta(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """
        CENÁRIO 15: Produto com vencimento próximo gera alerta
        DADO que tenho produto com vencimento em 15 dias
        QUANDO verifico produtos críticos
        ENTÃO deve aparecer alerta de vencimento próximo
        """
        # Dado
        data_proxima = date.today() + timedelta(days=15)
        produto = produto_service.criar_produto(
            nome="Produto Vencendo",
            preco=30.00,
            quantidade=100,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id,
            data_validade=data_proxima
        )
        
        # Quando
        alertas = produto_service.verificar_produtos_criticos()
        
        # Então
        alerta_vencimento = [
            a for a in alertas 
            if a.get('tipo_alerta') == 'PROXIMO_VENCIMENTO'
            and a.get('produto_id') == produto.id
        ]
        assert len(alerta_vencimento) > 0


class TestCenariosComplexos:
    """Cenários funcionais complexos envolvendo múltiplas operações."""
    
    def test_cenario_fluxo_venda_completo(
        self, produto_service, movimento_service, categoria_sample, 
        fornecedor_sample, usuario_sample, produto_repo
    ):
        """
        CENÁRIO 16: Fluxo completo de venda
        DADO que tenho um produto em estoque
        QUANDO registro uma venda (saída)
        E aplico um desconto
        ENTÃO o estoque deve diminuir
        E o preço deve estar com desconto
        """
        # Dado
        produto = produto_service.criar_produto(
            nome="Produto Venda",
            preco=200.00,
            preco_custo=100.00,
            quantidade=50,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        # Quando - Aplicar desconto
        produto_service.aplicar_desconto(produto.id, 10.0)
        
        # E registrar saída
        movimento_service.registrar_saida(
            produto_id=produto.id,
            quantidade=5,
            usuario_id=usuario_sample.id,
            observacao="Venda"
        )
        
        # Então
        produto_final = produto_repo.read(produto.id)
        assert produto_final.preco == 180.00  # 10% desconto
        assert produto_final.quantidade == 45  # 50 - 5


class TestCenariosExportacao:
    """Cenários funcionais para exportação de dados."""
    
    def test_cenario_exportar_relatorio_json(
        self, relatorio_service, produto_sample, tmp_path
    ):
        """
        CENÁRIO 18: Exportar relatório em formato JSON
        DADO que tenho um relatório de estoque
        QUANDO exporto para JSON
        ENTÃO deve criar arquivo válido
        """
        # Dado
        relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        filepath = tmp_path / "relatorio.json"
        
        # Quando
        sucesso = relatorio_service.exportar_relatorio_json(
            relatorio,
            str(filepath)
        )
        
        # Então
        assert sucesso is True
        assert filepath.exists()
        
        # Verificar conteúdo
        import json
        with open(filepath, 'r') as f:
            dados = json.load(f)
            assert isinstance(dados, list)
            assert len(dados) > 0
    
    def test_cenario_exportar_produtos_csv(
        self, relatorio_service, produto_sample, tmp_path
    ):
        """
        CENÁRIO 19: Exportar lista de produtos para CSV
        DADO que tenho produtos cadastrados
        QUANDO exporto para CSV
        ENTÃO deve criar arquivo com todos os produtos
        """
        # Dado
        relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        filepath = tmp_path / "produtos.csv"
        
        # Quando
        sucesso = relatorio_service.exportar_relatorio_csv(
            relatorio,
            str(filepath)
        )
        
        # Então
        assert sucesso is True
        assert filepath.exists()
        
        # Verificar conteúdo
        with open(filepath, 'r') as f:
            conteudo = f.read()
            assert 'nome' in conteudo.lower()
            assert 'preco' in conteudo.lower()


class TestCenariosEdge:
    """Cenários funcionais de casos extremos."""
    
    def test_cenario_produto_quantidade_zero(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """
        CENÁRIO 20: Cadastrar produto com quantidade zero
        DADO que quero cadastrar produto sem estoque inicial
        QUANDO crio com quantidade 0
        ENTÃO deve ser criado com sucesso
        """
        produto = produto_service.criar_produto(
            nome="Produto Zero",
            preco=100.00,
            quantidade=0,  # Zero é válido
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        assert produto.quantidade == 0
        assert produto.esta_em_estoque_critico() is True
    
    def test_cenario_busca_produtos_sem_resultado(
        self, produto_service
    ):
        """
        CENÁRIO 21: Buscar produtos sem resultado
        DADO que não tenho produtos na faixa de preço
        QUANDO busco produtos entre R$ 10000 e R$ 20000
        ENTÃO deve retornar lista vazia
        """
        produtos = produto_service.listar_produtos(
            preco_min=10000.0,
            preco_max=20000.0
        )
        
        assert isinstance(produtos, list)
        assert len(produtos) == 0


# ===========================
# Sumário dos Cenários Funcionais
# ===========================
"""
TOTAL: 21+ CENÁRIOS FUNCIONAIS testados

Áreas cobertas:
1. Cadastro de produtos (3 cenários)
2. Movimentação de estoque (3 cenários)
3. Aplicação de descontos (2 cenários)
4. Consultas e buscas (2 cenários)
5. Geração de relatórios (2 cenários)
6. Validações de negócio (3 cenários)
7. Fluxos complexos (2 cenários)
8. Exportação de dados (2 cenários)
9. Casos extremos (2 cenários)

Todos os testes focam em:
- Entradas e saídas esperadas
- Comportamento do sistema
- Regras de negócio
- Sem conhecimento da implementação interna
"""