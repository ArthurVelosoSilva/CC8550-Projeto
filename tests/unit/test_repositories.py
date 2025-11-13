# ===========================
# tests/unit/test_repositories.py
# ===========================
"""
Testes unitários para repositories.
"""
import pytest
from datetime import date
from src.models.produto import Produto
from src.models.categoria import Categoria
from src.models.fornecedor import Fornecedor
from src.models.usuario import Usuario
from src.exceptions.custom_exceptions import (
    ProdutoNaoEncontradoException,
    CategoriaNaoEncontradaException,
    FornecedorNaoEncontradoException
)


class TestProdutoRepository:
    """Testes para ProdutoRepository."""
    
    def test_create_produto(self, produto_repo, categoria_sample, fornecedor_sample):
        """Teste criação de produto."""
        produto = Produto(
            nome="Produto Teste",
            preco=100.00,
            quantidade=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        
        produto_criado = produto_repo.create(produto)
        
        assert produto_criado.id is not None
        assert produto_criado.nome == "Produto Teste"
    
    def test_read_produto_existente(self, produto_repo, produto_sample):
        """Teste leitura de produto existente."""
        produto = produto_repo.read(produto_sample.id)
        
        assert produto is not None
        assert produto.id == produto_sample.id
        assert produto.nome == produto_sample.nome
    
    def test_read_produto_inexistente(self, produto_repo):
        """Teste leitura de produto inexistente."""
        produto = produto_repo.read(99999)
        assert produto is None
    
    def test_update_produto(self, produto_repo, produto_sample):
        """Teste atualização de produto."""
        produto_sample.nome = "Nome Atualizado"
        produto_sample.preco = 4000.00
        
        produto_atualizado = produto_repo.update(produto_sample)
        
        assert produto_atualizado.nome == "Nome Atualizado"
        assert produto_atualizado.preco == 4000.00
    
    def test_delete_produto(self, produto_repo, produto_sample):
        """Teste deleção de produto (soft delete)."""
        resultado = produto_repo.delete(produto_sample.id)
        
        assert resultado is True
        
        # Verificar que está inativo
        produto = produto_repo.read(produto_sample.id)
        assert produto.ativo is False
    
    def test_list_all_produtos(self, produto_repo, categoria_sample, fornecedor_sample):
        """Teste listagem de todos produtos."""
        # Criar múltiplos produtos
        for i in range(3):
            produto = Produto(
                nome=f"Produto {i}",
                preco=100.00 * (i + 1),
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
            produto_repo.create(produto)
        
        produtos = produto_repo.list_all()
        assert len(produtos) >= 3
    
    def test_buscar_por_nome(self, produto_repo, produto_sample):
        """Teste busca por nome."""
        produtos = produto_repo.buscar_por_nome("Dell")
        
        assert len(produtos) > 0
        assert "Dell" in produtos[0].nome
    
    def test_buscar_por_codigo(self, produto_repo, produto_sample):
        """Teste busca por código único."""
        produto = produto_repo.buscar_por_codigo("NB-001")
        
        assert produto is not None
        assert produto.codigo == "NB-001"
    
    def test_buscar_por_categoria(self, produto_repo, produto_sample, categoria_sample):
        """Teste busca por categoria."""
        produtos = produto_repo.buscar_por_categoria(categoria_sample.id)
        
        assert len(produtos) > 0
        assert all(p.categoria_id == categoria_sample.id for p in produtos)
    
    def test_buscar_estoque_critico(self, produto_repo, categoria_sample, fornecedor_sample):
        """Teste busca produtos em estoque crítico."""
        # Criar produto com estoque baixo
        produto = Produto(
            nome="Produto Crítico",
            preco=50.00,
            quantidade=5,
            estoque_minimo=10,
            categoria_id=categoria_sample.id,
            fornecedor_id=fornecedor_sample.id
        )
        produto_repo.create(produto)
        
        produtos_criticos = produto_repo.buscar_estoque_critico()
        
        assert len(produtos_criticos) > 0
        assert any(p.nome == "Produto Crítico" for p in produtos_criticos)
    
    def test_buscar_com_filtros_preco(self, produto_repo, categoria_sample, fornecedor_sample):
        """Teste busca com filtros de preço."""
        # Criar produtos com preços diferentes
        for i, preco in enumerate([100, 200, 300]):
            produto = Produto(
                nome=f"Produto {preco}",
                preco=float(preco),
                quantidade=10,
                categoria_id=categoria_sample.id,
                fornecedor_id=fornecedor_sample.id
            )
            produto_repo.create(produto)
        
        produtos = produto_repo.buscar_com_filtros(preco_min=150.0, preco_max=250.0)
        
        assert len(produtos) > 0
        assert all(150 <= p.preco <= 250 for p in produtos)
    
    def test_atualizar_quantidade(self, produto_repo, produto_sample):
        """Teste atualização de quantidade."""
        sucesso = produto_repo.atualizar_quantidade(produto_sample.id, 50)
        
        assert sucesso is True
        
        produto = produto_repo.read(produto_sample.id)
        assert produto.quantidade == 50


class TestCategoriaRepository:
    """Testes para CategoriaRepository."""
    
    def test_create_categoria(self, categoria_repo):
        """Teste criação de categoria."""
        categoria = Categoria(nome="Nova Categoria", descricao="Teste")
        categoria_criada = categoria_repo.create(categoria)
        
        assert categoria_criada.id is not None
        assert categoria_criada.nome == "Nova Categoria"
    
    def test_read_categoria(self, categoria_repo, categoria_sample):
        """Teste leitura de categoria."""
        categoria = categoria_repo.read(categoria_sample.id)
        
        assert categoria is not None
        assert categoria.id == categoria_sample.id
    
    def test_update_categoria(self, categoria_repo, categoria_sample):
        """Teste atualização de categoria."""
        categoria_sample.nome = "Nome Atualizado"
        categoria_atualizada = categoria_repo.update(categoria_sample)
        
        assert categoria_atualizada.nome == "Nome Atualizado"
    
    def test_delete_categoria(self, categoria_repo, categoria_sample):
        """Teste deleção de categoria."""
        resultado = categoria_repo.delete(categoria_sample.id)
        assert resultado is True
    
    def test_list_all_categorias(self, categoria_repo):
        """Teste listagem de categorias."""
        # Criar algumas categorias
        for i in range(3):
            cat = Categoria(nome=f"Categoria {i}")
            categoria_repo.create(cat)
        
        categorias = categoria_repo.list_all()
        assert len(categorias) >= 3


class TestFornecedorRepository:
    """Testes para FornecedorRepository."""
    
    def test_create_fornecedor(self, fornecedor_repo):
        """Teste criação de fornecedor."""
        fornecedor = Fornecedor(
            nome="Novo Fornecedor",
            cnpj="11111111000111",
            email="novo@email.com",
            telefone="11999999999"
        )
        
        fornecedor_criado = fornecedor_repo.create(fornecedor)
        
        assert fornecedor_criado.id is not None
        assert fornecedor_criado.nome == "Novo Fornecedor"
    
    def test_read_fornecedor(self, fornecedor_repo, fornecedor_sample):
        """Teste leitura de fornecedor."""
        fornecedor = fornecedor_repo.read(fornecedor_sample.id)
        
        assert fornecedor is not None
        assert fornecedor.id == fornecedor_sample.id
    
    def test_update_fornecedor(self, fornecedor_repo, fornecedor_sample):
        """Teste atualização de fornecedor."""
        fornecedor_sample.nome = "Nome Atualizado"
        fornecedor_atualizado = fornecedor_repo.update(fornecedor_sample)
        
        assert fornecedor_atualizado.nome == "Nome Atualizado"
    
    def test_delete_fornecedor(self, fornecedor_repo, fornecedor_sample):
        """Teste deleção de fornecedor."""
        resultado = fornecedor_repo.delete(fornecedor_sample.id)
        assert resultado is True
    
    def test_buscar_por_cnpj(self, fornecedor_repo, fornecedor_sample):
        """Teste busca por CNPJ."""
        fornecedor = fornecedor_repo.buscar_por_cnpj("12345678000190")
        
        assert fornecedor is not None
        assert fornecedor.cnpj == "12345678000190"
    
    def test_list_all_fornecedores(self, fornecedor_repo):
        """Teste listagem de fornecedores."""
        fornecedores = fornecedor_repo.list_all()
        assert isinstance(fornecedores, list)


class TestMovimentoRepository:
    """Testes para MovimentoRepository."""
    
    def test_create_movimento(self, movimento_repo, produto_sample, usuario_sample):
        """Teste criação de movimento."""
        from src.models.movimento import Movimento, TipoMovimento
        
        movimento = Movimento(
            produto_id=produto_sample.id,
            tipo=TipoMovimento.ENTRADA,
            quantidade=10,
            usuario_id=usuario_sample.id,
            observacao="Teste"
        )
        
        movimento_criado = movimento_repo.create(movimento)
        
        assert movimento_criado.id is not None
        assert movimento_criado.quantidade == 10
    
    def test_read_movimento(self, movimento_repo, produto_sample, usuario_sample):
        """Teste leitura de movimento."""
        from src.models.movimento import Movimento, TipoMovimento
        
        movimento = Movimento(
            produto_id=produto_sample.id,
            tipo=TipoMovimento.SAIDA,
            quantidade=5,
            usuario_id=usuario_sample.id
        )
        movimento_criado = movimento_repo.create(movimento)
        
        movimento_lido = movimento_repo.read(movimento_criado.id)
        
        assert movimento_lido is not None
        assert movimento_lido.id == movimento_criado.id
    
    def test_buscar_por_produto(self, movimento_repo, produto_sample, usuario_sample):
        """Teste busca movimentos por produto."""
        from src.models.movimento import Movimento, TipoMovimento
        
        # Criar alguns movimentos
        for i in range(3):
            mov = Movimento(
                produto_id=produto_sample.id,
                tipo=TipoMovimento.ENTRADA,
                quantidade=10 * (i + 1),
                usuario_id=usuario_sample.id
            )
            movimento_repo.create(mov)
        
        movimentos = movimento_repo.buscar_por_produto(produto_sample.id)
        
        assert len(movimentos) >= 3
    
    def test_buscar_por_periodo(self, movimento_repo, produto_sample, usuario_sample):
        """Teste busca movimentos por período."""
        from src.models.movimento import Movimento, TipoMovimento
        from datetime import datetime, timedelta
        
        movimento = Movimento(
            produto_id=produto_sample.id,
            tipo=TipoMovimento.AJUSTE,
            quantidade=5,
            usuario_id=usuario_sample.id
        )
        movimento_repo.create(movimento)
        
        data_inicio = datetime.now() - timedelta(days=1)
        data_fim = datetime.now() + timedelta(days=1)
        
        movimentos = movimento_repo.buscar_por_periodo(data_inicio, data_fim)
        
        assert len(movimentos) > 0


class TestUsuarioRepository:
    """Testes para UsuarioRepository."""
    
    def test_create_usuario(self, usuario_repo):
        """Teste criação de usuário."""
        import hashlib
        senha_hash = hashlib.sha256("senha".encode()).hexdigest()
        
        usuario = Usuario(
            nome="Novo Usuario",
            email="novo@email.com",
            senha_hash=senha_hash
        )
        
        usuario_criado = usuario_repo.create(usuario)
        
        assert usuario_criado.id is not None
        assert usuario_criado.email == "novo@email.com"
    
    def test_read_usuario(self, usuario_repo, usuario_sample):
        """Teste leitura de usuário."""
        usuario = usuario_repo.read(usuario_sample.id)
        
        assert usuario is not None
        assert usuario.id == usuario_sample.id
    
    def test_buscar_por_email(self, usuario_repo, usuario_sample):
        """Teste busca por email."""
        usuario = usuario_repo.buscar_por_email("teste@email.com")
        
        assert usuario is not None
        assert usuario.email == "teste@email.com"
    
    def test_update_usuario(self, usuario_repo, usuario_sample):
        """Teste atualização de usuário."""
        usuario_sample.nome = "Nome Atualizado"
        usuario_atualizado = usuario_repo.update(usuario_sample)
        
        assert usuario_atualizado.nome == "Nome Atualizado"
    
    def test_delete_usuario(self, usuario_repo, usuario_sample):
        """Teste deleção de usuário."""
        resultado = usuario_repo.delete(usuario_sample.id)
        assert resultado is True