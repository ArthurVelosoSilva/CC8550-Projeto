# ===========================
# tests/specific/test_performance.py
# ===========================
"""
Testes de performance (requisito: pelo menos 2 tipos).
"""
import pytest
import time


class TestPerformance:
    """Testes de performance e carga."""
    
    def test_criar_produto_tempo_maximo(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa que criação de produto não excede tempo máximo."""
        inicio = time.time()
        
        produto_service.criar_produto(
            nome="Produto Performance",
            preco=100.00,
            quantidade=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        tempo_decorrido = time.time() - inicio
        
        # Deve executar em menos de 1 segundo
        assert tempo_decorrido < 1.0
    
    def test_listar_produtos_grande_volume(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa performance com grande volume de produtos."""
        # Criar 100 produtos
        for i in range(100):
            produto_service.criar_produto(
                nome=f"Produto Volume {i}",
                preco=100.00 + i,
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
        
        # Medir tempo de listagem
        inicio = time.time()
        produtos = produto_service.listar_produtos()
        tempo_decorrido = time.time() - inicio
        
        # Deve listar em menos de 2 segundos
        assert tempo_decorrido < 2.0
        assert len(produtos) >= 100
    
    def test_busca_com_filtros_performance(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa performance de busca com filtros."""
        # Criar produtos
        for i in range(50):
            produto_service.criar_produto(
                nome=f"Produto Busca {i}",
                preco=50.00 + (i * 10),
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
        
        # Medir tempo de busca com filtros
        inicio = time.time()
        produtos = produto_service.listar_produtos(
            preco_min=200.0,
            preco_max=400.0,
            ordenar_por='preco'
        )
        tempo_decorrido = time.time() - inicio
        
        # Deve buscar em menos de 1 segundo
        assert tempo_decorrido < 1.0
    
    @pytest.mark.benchmark
    def test_benchmark_criar_produto(
        self, benchmark, produto_service, categoria_sample, fornecedor_sample
    ):
        """Benchmark de criação de produto usando pytest-benchmark."""
        def criar():
            return produto_service.criar_produto(
                nome="Produto Benchmark",
                preco=100.00,
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
        
        resultado = benchmark(criar)
        assert resultado.id is not None
    
    def test_multiplas_operacoes_sequenciais(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Testa performance de múltiplas operações sequenciais."""
        inicio = time.time()
        
        # Realizar 50 operações
        for i in range(50):
            if i % 2 == 0:
                movimento_service.registrar_entrada(
                    produto_sample.id, 1, usuario_sample.id
                )
            else:
                movimento_service.registrar_saida(
                    produto_sample.id, 1, usuario_sample.id
                )
        
        tempo_decorrido = time.time() - inicio
        
        # Deve executar em menos de 5 segundos
        assert tempo_decorrido < 5.0