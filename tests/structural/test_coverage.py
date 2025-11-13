# ===========================
# tests/structural/test_coverage.py
# ===========================
"""
Testes estruturais (caixa-branca) focados em cobertura de código.
Objetivo: Atingir 80%+ de cobertura testando todos os caminhos críticos.
"""
import pytest
from datetime import date, datetime, timedelta


class TestCoberturaProdutoService:
    """Testes de cobertura para ProdutoService."""
    
    def test_caminho_criar_produto_sucesso(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa caminho de sucesso na criação de produto."""
        produto = produto_service.criar_produto(
            nome="Teste Cobertura",
            preco=100.00,
            quantidade=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        assert produto.id is not None
    
    def test_caminho_criar_produto_com_codigo_duplicado(
        self, produto_service, categoria_sample, fornecedor_sample, produto_sample
    ):
        """Testa caminho de erro: código duplicado."""
        from src.exceptions.custom_exceptions import ValidacaoException
        
        with pytest.raises(ValidacaoException):
            produto_service.criar_produto(
                nome="Outro Produto",
                preco=100.00,
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id,
                codigo=produto_sample.codigo  # Código já existe
            )
    
    def test_caminho_criar_produto_categoria_inativa(
        self, produto_service, categoria_sample, fornecedor_sample, categoria_repo
    ):
        """Testa caminho de erro: categoria inativa."""
        from src.exceptions.custom_exceptions import ValidacaoException
        
        # Desativar categoria
        categoria_sample.ativo = False
        categoria_repo.update(categoria_sample)
        
        with pytest.raises(ValidacaoException):
            produto_service.criar_produto(
                nome="Produto",
                preco=100.00,
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
    
    def test_caminho_criar_produto_fornecedor_inativo(
        self, produto_service, categoria_sample, fornecedor_sample, fornecedor_repo
    ):
        """Testa caminho de erro: fornecedor inativo."""
        from src.exceptions.custom_exceptions import ValidacaoException
        
        # Desativar fornecedor
        fornecedor_sample.ativo = False
        fornecedor_repo.update(fornecedor_sample)
        
        with pytest.raises(ValidacaoException):
            produto_service.criar_produto(
                nome="Produto",
                preco=100.00,
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
    
    def test_caminho_criar_produto_preco_custo_maior_venda(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa caminho de erro: preço de custo maior que venda."""
        from src.exceptions.custom_exceptions import ValidacaoException
        
        with pytest.raises(ValidacaoException):
            produto_service.criar_produto(
                nome="Produto",
                preco=100.00,
                preco_custo=150.00,  # Maior que preço de venda
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
    
    def test_caminho_criar_produto_estoque_maximo_menor_minimo(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa caminho de erro: estoque máximo menor que mínimo."""
        from src.exceptions.custom_exceptions import ValidacaoException
        
        with pytest.raises(ValidacaoException):
            produto_service.criar_produto(
                nome="Produto",
                preco=100.00,
                quantidade=10,
                estoque_minimo=50,
                estoque_maximo=30,  # Menor que mínimo
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
    
    def test_caminho_aplicar_desconto_limite_sucesso(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa caminho de sucesso: desconto no limite."""
        produto = produto_service.criar_produto(
            nome="Produto Desconto",
            preco=200.00,
            preco_custo=100.00,
            quantidade=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        # Desconto de 30% (limite)
        produto_com_desconto = produto_service.aplicar_desconto(produto.id, 30.0)
        assert produto_com_desconto.preco == 140.00
    
    def test_caminho_aplicar_desconto_abaixo_custo(
        self, produto_service, categoria_sample, fornecedor_sample
    ):
        """Testa caminho de erro: desconto resultaria em preço abaixo do custo."""
        from src.exceptions.custom_exceptions import OperacaoNaoPermitidaException
        
        produto = produto_service.criar_produto(
            nome="Produto",
            preco=110.00,
            preco_custo=100.00,
            quantidade=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        with pytest.raises(OperacaoNaoPermitidaException):
            produto_service.aplicar_desconto(produto.id, 15.0)  # Resultaria em 93.50

class TestCoberturaMovimentoService:
    """Testes de cobertura para MovimentoService."""
    
    def test_caminho_entrada_alerta_estoque_maximo(
        self, movimento_service, produto_sample, usuario_sample, produto_repo
    ):
        """Testa caminho de alerta: entrada excede estoque máximo."""
        # Entrada que vai exceder o máximo (gera warning no log)
        movimento_service.registrar_entrada(
            produto_id=produto_sample.id,
            quantidade=2000,  # Vai exceder estoque_maximo
            usuario_id=usuario_sample.id
        )
        
        # Verificar que a entrada foi registrada mesmo assim
        produto = produto_repo.read(produto_sample.id)
        assert produto.quantidade > produto_sample.quantidade
    
    def test_caminho_saida_estoque_critico(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Testa caminho: saída deixa estoque crítico (gera warning)."""
        # Deixar próximo do estoque mínimo
        quantidade_deixar = produto_sample.estoque_minimo - 1
        quantidade_retirar = produto_sample.quantidade - quantidade_deixar
        
        if quantidade_retirar > 0:
            movimento_service.registrar_saida(
                produto_id=produto_sample.id,
                quantidade=quantidade_retirar,
                usuario_id=usuario_sample.id
            )
    
    def test_caminho_ajuste_sem_observacao(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Testa caminho de erro: ajuste sem observação."""
        from src.exceptions.custom_exceptions import OperacaoNaoPermitidaException
        
        with pytest.raises(OperacaoNaoPermitidaException):
            movimento_service.registrar_ajuste(
                produto_id=produto_sample.id,
                nova_quantidade=50,
                usuario_id=usuario_sample.id,
                observacao=""
            )
    
    def test_caminho_ajuste_com_observacao_valida(
        self, movimento_service, produto_sample, usuario_sample
    ):
        """Testa caminho de sucesso: ajuste com observação."""
        movimento = movimento_service.registrar_ajuste(
            produto_id=produto_sample.id,
            nova_quantidade=75,
            usuario_id=usuario_sample.id,
            observacao="Inventário mensal"
        )
        
        assert movimento is not None
        assert "Ajuste de estoque" in movimento.observacao


class TestCoberturaValidators:
    """Testes de cobertura para todos os caminhos dos Validators."""
    
    def test_validar_preco_todos_caminhos(self):
        """Testa todos os caminhos de validação de preço."""
        from src.utils.validators import Validators
        from src.exceptions.custom_exceptions import PrecoInvalidoException
        
        # Caminho sucesso: preço válido
        assert Validators.validar_preco(100.50) == 100.50
        
        # Caminho sucesso: inteiro convertido para float
        assert Validators.validar_preco(100) == 100.00
        
        # Caminho sucesso: zero permitido
        assert Validators.validar_preco(0, permitir_zero=True) == 0.00
        
        # Caminho erro: zero não permitido
        with pytest.raises(PrecoInvalidoException):
            Validators.validar_preco(0, permitir_zero=False)
        
        # Caminho erro: negativo
        with pytest.raises(PrecoInvalidoException):
            Validators.validar_preco(-10)
        
        # Caminho erro: tipo inválido
        with pytest.raises(PrecoInvalidoException):
            Validators.validar_preco("abc")
    
    def test_validar_cnpj_todos_caminhos(self):
        """Testa todos os caminhos de validação de CNPJ."""
        from src.utils.validators import Validators
        from src.exceptions.custom_exceptions import ValidacaoException
        
        # Caminho sucesso: CNPJ formatado
        assert Validators.validar_cnpj("12.345.678/0001-90") == "12345678000190"
        
        # Caminho sucesso: CNPJ sem formatação
        assert Validators.validar_cnpj("12345678000190") == "12345678000190"
        
        # Caminho erro: tamanho inválido
        with pytest.raises(ValidacaoException):
            Validators.validar_cnpj("123456")
        
        # Caminho erro: vazio
        with pytest.raises(ValidacaoException):
            Validators.validar_cnpj("")
    
    def test_validar_data_validade_todos_caminhos(self):
        """Testa todos os caminhos de validação de data."""
        from src.utils.validators import Validators
        from src.exceptions.custom_exceptions import ValidacaoException
        
        # Caminho sucesso: None
        assert Validators.validar_data_validade(None) is None
        
        # Caminho sucesso: data futura
        data_futura = date.today() + timedelta(days=30)
        assert Validators.validar_data_validade(data_futura) == data_futura
        
        # Caminho sucesso: datetime convertido para date
        dt_futuro = datetime.now() + timedelta(days=30)
        resultado = Validators.validar_data_validade(dt_futuro)
        assert isinstance(resultado, date)
        
        # Caminho erro: data passada
        data_passada = date.today() - timedelta(days=1)
        with pytest.raises(ValidacaoException):
            Validators.validar_data_validade(data_passada)
        
        # Caminho erro: tipo inválido
        with pytest.raises(ValidacaoException):
            Validators.validar_data_validade("2025-12-31")


class TestCoberturaModels:
    """Testes de cobertura para métodos dos models."""
    
    def test_produto_calcular_margem_todos_caminhos(self):
        """Testa todos os caminhos de cálculo de margem."""
        from src.models.produto import Produto
        
        # Caminho: com preço de custo
        p1 = Produto(
            nome="P1", preco=200.00, preco_custo=150.00,
            quantidade=10, categoria_id=1, fornecedor_id=1
        )
        assert p1.calcular_margem_lucro() == 33.33
        
        # Caminho: sem preço de custo (None)
        p2 = Produto(
            nome="P2", preco=200.00, preco_custo=None,
            quantidade=10, categoria_id=1, fornecedor_id=1
        )
        assert p2.calcular_margem_lucro() == 0.0
        
        # Caminho: preço de custo zero
        p3 = Produto(
            nome="P3", preco=200.00, preco_custo=0.0,
            quantidade=10, categoria_id=1, fornecedor_id=1
        )
        assert p3.calcular_margem_lucro() == 0.0
    
    def test_produto_esta_em_estoque_critico_branches(self):
        """Testa branches de estoque crítico."""
        from src.models.produto import Produto
        
        # Branch: quantidade <= estoque_minimo
        p1 = Produto(
            nome="P1", preco=100.00, quantidade=5, estoque_minimo=10,
            categoria_id=1, fornecedor_id=1
        )
        assert p1.esta_em_estoque_critico() is True
        
        # Branch: quantidade == estoque_minimo (exatamente no limite)
        p2 = Produto(
            nome="P2", preco=100.00, quantidade=10, estoque_minimo=10,
            categoria_id=1, fornecedor_id=1
        )
        assert p2.esta_em_estoque_critico() is True
        
        # Branch: quantidade > estoque_minimo
        p3 = Produto(
            nome="P3", preco=100.00, quantidade=20, estoque_minimo=10,
            categoria_id=1, fornecedor_id=1
        )
        assert p3.esta_em_estoque_critico() is False
    
    def test_produto_esta_proximo_vencimento_branches(self):
        """Testa branches de vencimento próximo."""
        from src.models.produto import Produto
        
        # Branch: sem data de validade
        p1 = Produto(
            nome="P1", preco=100.00, quantidade=10,
            categoria_id=1, fornecedor_id=1, data_validade=None
        )
        assert p1.esta_proximo_vencimento() is False
        
        # Branch: dentro do período
        data_proxima = date.today() + timedelta(days=15)
        p2 = Produto(
            nome="P2", preco=100.00, quantidade=10,
            categoria_id=1, fornecedor_id=1, data_validade=data_proxima
        )
        assert p2.esta_proximo_vencimento(30) is True
        
        # Branch: fora do período
        data_distante = date.today() + timedelta(days=60)
        p3 = Produto(
            nome="P3", preco=100.00, quantidade=10,
            categoria_id=1, fornecedor_id=1, data_validade=data_distante
        )
        assert p3.esta_proximo_vencimento(30) is False
        
        # Branch: vencido (dias restantes < 0)
        data_vencida = date.today() - timedelta(days=1)
        p4 = Produto(
            nome="P4", preco=100.00, quantidade=10,
            categoria_id=1, fornecedor_id=1, data_validade=data_vencida
        )
        assert p4.esta_proximo_vencimento(30) is False


class TestCoberturaFileHandler:
    """Testes de cobertura para FileHandler."""
    
    def test_exportar_json_sucesso(self, tmp_path):
        """Testa caminho de sucesso de exportação JSON."""
        from src.utils.file_handler import FileHandler
        
        dados = [{'id': 1, 'nome': 'Teste'}]
        filepath = tmp_path / "teste.json"
        
        sucesso = FileHandler.exportar_json(dados, str(filepath))
        assert sucesso is True
        assert filepath.exists()
    
    def test_importar_json_arquivo_inexistente(self):
        """Testa caminho de erro: arquivo não existe."""
        from src.utils.file_handler import FileHandler
        
        dados = FileHandler.importar_json("arquivo_inexistente.json")
        assert dados == []
    
    def test_exportar_csv_dados_vazios(self, tmp_path):
        """Testa caminho: dados vazios."""
        from src.utils.file_handler import FileHandler
        
        filepath = tmp_path / "vazio.csv"
        sucesso = FileHandler.exportar_csv([], str(filepath))
        assert sucesso is False
    
    def test_importar_csv_arquivo_inexistente(self):
        """Testa caminho de erro: arquivo CSV não existe."""
        from src.utils.file_handler import FileHandler
        
        dados = FileHandler.importar_csv("inexistente.csv")
        assert dados == []