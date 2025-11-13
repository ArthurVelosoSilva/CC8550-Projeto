# ===========================
# tests/conftest.py
# ===========================
"""
Configurações e fixtures globais para os testes.
"""
import pytest
import os
import sys
from datetime import datetime, date
import tempfile

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repositories.produto_repository import ProdutoRepository
from src.repositories.categoria_repository import CategoriaRepository
from src.repositories.fornecedor_repository import FornecedorRepository
from src.repositories.movimento_repository import MovimentoRepository
from src.repositories.usuario_repository import UsuarioRepository
from src.services.produto_service import ProdutoService
from src.services.fornecedor_service import FornecedorService
from src.services.movimento_service import MovimentoService
from src.services.relatorio_service import RelatorioService
from src.models.categoria import Categoria
from src.models.fornecedor import Fornecedor
from src.models.produto import Produto
from src.models.usuario import Usuario


@pytest.fixture(scope="function")
def db_path():
    """Cria banco de dados temporário para testes."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_file = f.name
    
    yield db_file
    
    # Cleanup
    if os.path.exists(db_file):
        os.unlink(db_file)


@pytest.fixture
def categoria_repo(db_path):
    """Fixture para repository de categorias."""
    return CategoriaRepository(db_path)


@pytest.fixture
def fornecedor_repo(db_path):
    """Fixture para repository de fornecedores."""
    return FornecedorRepository(db_path)


@pytest.fixture
def produto_repo(db_path):
    """Fixture para repository de produtos."""
    return ProdutoRepository(db_path)


@pytest.fixture
def movimento_repo(db_path):
    """Fixture para repository de movimentos."""
    return MovimentoRepository(db_path)


@pytest.fixture
def usuario_repo(db_path):
    """Fixture para repository de usuários."""
    return UsuarioRepository(db_path)


@pytest.fixture
def categoria_sample(categoria_repo):
    """Fixture para categoria de exemplo."""
    categoria = Categoria(nome="Eletrônicos", descricao="Produtos eletrônicos")
    return categoria_repo.create(categoria)


@pytest.fixture
def fornecedor_sample(fornecedor_repo):
    """Fixture para fornecedor de exemplo."""
    fornecedor = Fornecedor(
        nome="Tech Distribuidora",
        cnpj="12345678000190",
        email="contato@tech.com",
        telefone="11987654321"
    )
    return fornecedor_repo.create(fornecedor)


@pytest.fixture
def produto_sample(produto_repo, categoria_sample, fornecedor_sample):
    """Fixture para produto de exemplo."""
    produto = Produto(
        nome="Notebook Dell",
        preco=3500.00,
        preco_custo=2800.00,
        quantidade=10,
        categoria_id=categoria_sample.id,
        fornecedor_id=fornecedor_sample.id,
        codigo="NB-001"
    )
    return produto_repo.create(produto)


@pytest.fixture
def usuario_sample(usuario_repo):
    """Fixture para usuário de exemplo."""
    import hashlib
    senha_hash = hashlib.sha256("senha123".encode()).hexdigest()
    usuario = Usuario(
        nome="Usuario Teste",
        email="teste@email.com",
        senha_hash=senha_hash
    )
    return usuario_repo.create(usuario)


@pytest.fixture
def produto_service(produto_repo, categoria_repo, fornecedor_repo):
    """Fixture para serviço de produtos."""
    return ProdutoService(produto_repo, categoria_repo, fornecedor_repo)


@pytest.fixture
def fornecedor_service(fornecedor_repo):
    """Fixture para serviço de fornecedores."""
    return FornecedorService(fornecedor_repo)


@pytest.fixture
def movimento_service(movimento_repo, produto_repo):
    """Fixture para serviço de movimentos."""
    return MovimentoService(movimento_repo, produto_repo)


@pytest.fixture
def relatorio_service(produto_repo, movimento_repo, categoria_repo, fornecedor_repo):
    """Fixture para serviço de relatórios."""
    return RelatorioService(produto_repo, movimento_repo, categoria_repo, fornecedor_repo)