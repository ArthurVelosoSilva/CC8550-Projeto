# ===========================
# tests/unit/test_models.py
# ===========================
"""
Testes unitários para os models.
"""
import pytest
from datetime import date, datetime, timedelta
from src.models.produto import Produto
from src.models.categoria import Categoria
from src.models.fornecedor import Fornecedor
from src.models.movimento import Movimento, TipoMovimento
from src.models.usuario import Usuario


class TestProdutoModel:
    """Testes para o model Produto."""
    
    def test_criar_produto_basico(self):
        """Teste criação de produto com dados básicos."""
        produto = Produto(
            nome="Notebook",
            preco=3500.00,
            quantidade=10,
            categoria_id=1,
            fornecedor_id=1
        )
        
        assert produto.nome == "Notebook"
        assert produto.preco == 3500.00
        assert produto.quantidade == 10
        assert produto.ativo is True
    
    def test_criar_produto_completo(self):
        """Teste criação de produto com todos os campos."""
        data_validade = date(2025, 12, 31)
        produto = Produto(
            nome="Mouse",
            preco=150.00,
            preco_custo=100.00,
            quantidade=50,
            categoria_id=1,
            fornecedor_id=1,
            codigo="MS-001",
            descricao="Mouse gamer",
            estoque_minimo=10,
            estoque_maximo=200,
            localizacao="A1-P1",
            data_validade=data_validade
        )
        
        assert produto.codigo == "MS-001"
        assert produto.preco_custo == 100.00
        assert produto.data_validade == data_validade
    
    def test_calcular_margem_lucro(self):
        """Teste cálculo de margem de lucro."""
        produto = Produto(
            nome="Teclado",
            preco=200.00,
            preco_custo=150.00,
            quantidade=20,
            categoria_id=1,
            fornecedor_id=1
        )
        
        margem = produto.calcular_margem_lucro()
        assert margem == 33.33
    
    def test_calcular_margem_lucro_sem_custo(self):
        """Teste cálculo de margem sem preço de custo."""
        produto = Produto(
            nome="Monitor",
            preco=800.00,
            quantidade=5,
            categoria_id=1,
            fornecedor_id=1
        )
        
        margem = produto.calcular_margem_lucro()
        assert margem == 0.0
    
    def test_esta_em_estoque_critico_verdadeiro(self):
        """Teste verificação de estoque crítico - caso verdadeiro."""
        produto = Produto(
            nome="Cabo HDMI",
            preco=30.00,
            quantidade=8,
            estoque_minimo=10,
            categoria_id=1,
            fornecedor_id=1
        )
        
        assert produto.esta_em_estoque_critico() is True
    
    def test_esta_em_estoque_critico_falso(self):
        """Teste verificação de estoque crítico - caso falso."""
        produto = Produto(
            nome="Pen Drive",
            preco=50.00,
            quantidade=25,
            estoque_minimo=10,
            categoria_id=1,
            fornecedor_id=1
        )
        
        assert produto.esta_em_estoque_critico() is False
    
    def test_esta_proximo_vencimento_verdadeiro(self):
        """Teste verificação de vencimento próximo - caso verdadeiro."""
        data_proxima = date.today() + timedelta(days=15)
        produto = Produto(
            nome="Alimento",
            preco=20.00,
            quantidade=50,
            categoria_id=1,
            fornecedor_id=1,
            data_validade=data_proxima
        )
        
        assert produto.esta_proximo_vencimento(30) is True
    
    def test_esta_proximo_vencimento_falso(self):
        """Teste verificação de vencimento próximo - caso falso."""
        data_distante = date.today() + timedelta(days=90)
        produto = Produto(
            nome="Alimento",
            preco=20.00,
            quantidade=50,
            categoria_id=1,
            fornecedor_id=1,
            data_validade=data_distante
        )
        
        assert produto.esta_proximo_vencimento(30) is False
    
    def test_esta_proximo_vencimento_sem_data(self):
        """Teste verificação de vencimento sem data de validade."""
        produto = Produto(
            nome="Produto Durável",
            preco=100.00,
            quantidade=10,
            categoria_id=1,
            fornecedor_id=1
        )
        
        assert produto.esta_proximo_vencimento() is False
    
    def test_to_dict(self):
        """Teste conversão de produto para dicionário."""
        produto = Produto(
            id=1,
            nome="Item",
            preco=50.00,
            quantidade=10,
            categoria_id=1,
            fornecedor_id=1
        )
        
        dict_produto = produto.to_dict()
        
        assert isinstance(dict_produto, dict)
        assert dict_produto['id'] == 1
        assert dict_produto['nome'] == "Item"
        assert dict_produto['preco'] == 50.00


class TestCategoriaModel:
    """Testes para o model Categoria."""
    
    def test_criar_categoria(self):
        """Teste criação de categoria."""
        categoria = Categoria(
            nome="Eletrônicos",
            descricao="Produtos eletrônicos"
        )
        
        assert categoria.nome == "Eletrônicos"
        assert categoria.descricao == "Produtos eletrônicos"
        assert categoria.ativo is True
    
    def test_to_dict(self):
        """Teste conversão para dicionário."""
        categoria = Categoria(id=1, nome="Ferramentas")
        dict_cat = categoria.to_dict()
        
        assert dict_cat['id'] == 1
        assert dict_cat['nome'] == "Ferramentas"


class TestFornecedorModel:
    """Testes para o model Fornecedor."""
    
    def test_criar_fornecedor_completo(self):
        """Teste criação de fornecedor completo."""
        fornecedor = Fornecedor(
            nome="Tech LTDA",
            cnpj="12345678000190",
            email="contato@tech.com",
            telefone="11987654321",
            cidade="São Paulo",
            estado="SP",
            prazo_entrega_dias=5
        )
        
        assert fornecedor.nome == "Tech LTDA"
        assert fornecedor.cnpj == "12345678000190"
        assert fornecedor.prazo_entrega_dias == 5
    
    def test_to_dict(self):
        """Teste conversão para dicionário."""
        fornecedor = Fornecedor(
            id=1,
            nome="Fornecedor X",
            cnpj="11111111000111",
            email="x@email.com",
            telefone="1199999999"
        )
        
        dict_forn = fornecedor.to_dict()
        assert dict_forn['id'] == 1
        assert dict_forn['cnpj'] == "11111111000111"


class TestMovimentoModel:
    """Testes para o model Movimento."""
    
    def test_criar_movimento_entrada(self):
        """Teste criação de movimento de entrada."""
        movimento = Movimento(
            produto_id=1,
            tipo=TipoMovimento.ENTRADA,
            quantidade=10,
            usuario_id=1,
            observacao="Compra"
        )
        
        assert movimento.tipo == TipoMovimento.ENTRADA
        assert movimento.quantidade == 10
    
    def test_criar_movimento_saida(self):
        """Teste criação de movimento de saída."""
        movimento = Movimento(
            produto_id=1,
            tipo=TipoMovimento.SAIDA,
            quantidade=5,
            usuario_id=1
        )
        
        assert movimento.tipo == TipoMovimento.SAIDA
        assert movimento.quantidade == 5
    
    def test_to_dict(self):
        """Teste conversão para dicionário."""
        movimento = Movimento(
            id=1,
            produto_id=2,
            tipo=TipoMovimento.AJUSTE,
            quantidade=3,
            usuario_id=1
        )
        
        dict_mov = movimento.to_dict()
        assert dict_mov['id'] == 1
        assert dict_mov['tipo'] == 'AJUSTE'


class TestUsuarioModel:
    """Testes para o model Usuario."""
    
    def test_criar_usuario(self):
        """Teste criação de usuário."""
        usuario = Usuario(
            nome="João Silva",
            email="joao@email.com",
            senha_hash="hash123"
        )
        
        assert usuario.nome == "João Silva"
        assert usuario.email == "joao@email.com"
        assert usuario.ativo is True
    
    def test_to_dict_nao_expoe_senha(self):
        """Teste que to_dict não expõe senha."""
        usuario = Usuario(
            id=1,
            nome="Maria",
            email="maria@email.com",
            senha_hash="hash_secreto"
        )
        
        dict_user = usuario.to_dict()
        assert 'senha_hash' not in dict_user
        assert dict_user['nome'] == "Maria"