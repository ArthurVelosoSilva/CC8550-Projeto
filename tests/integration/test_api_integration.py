# ===========================
# tests/integration/test_api_integration.py
# ===========================
"""
Testes de integração da API REST.
"""
import pytest
import json
from src.api.routes import criar_app


@pytest.fixture
def client(db_path):
    """Fixture para cliente de teste da API."""
    app = criar_app(db_path)
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def categoria_api(client):
    """Fixture para criar categoria via API."""
    response = client.post('/api/categorias', 
        json={'nome': 'Categoria API', 'descricao': 'Teste'})
    return response.get_json()


@pytest.fixture
def fornecedor_api(client):
    """Fixture para criar fornecedor via API."""
    response = client.post('/api/fornecedores',
        json={
            'nome': 'Fornecedor API',
            'cnpj': '12345678000190',
            'email': 'api@fornecedor.com',
            'telefone': '11987654321'
        })
    return response.get_json()


class TestAPIIntegration:
    """Testes de integração da API REST."""
    
    def test_health_check(self, client):
        """Teste endpoint de health check."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_api_info(self, client):
        """Teste endpoint de informações da API."""
        response = client.get('/api')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'nome' in data
        assert 'endpoints' in data
    
    def test_fluxo_completo_produto_api(self, client, categoria_api, fornecedor_api):
        """Teste fluxo completo de produto via API."""
        # Criar produto
        response = client.post('/api/produtos', json={
            'nome': 'Produto API',
            'preco': 150.00,
            'quantidade': 20,
            'categoria_id': categoria_api['id'],
            'fornecedor_id': fornecedor_api['id'],
            'codigo': 'API-001'
        })
        
        assert response.status_code == 201
        produto = response.get_json()
        assert produto['nome'] == 'Produto API'
        produto_id = produto['id']
        
        # Buscar produto
        response = client.get(f'/api/produtos/{produto_id}')
        assert response.status_code == 200
        
        # Atualizar produto
        response = client.put(f'/api/produtos/{produto_id}', json={
            'nome': 'Produto API Atualizado',
            'preco': 200.00
        })
        assert response.status_code == 200
        produto_atualizado = response.get_json()
        assert produto_atualizado['nome'] == 'Produto API Atualizado'
        
        # Deletar produto
        response = client.delete(f'/api/produtos/{produto_id}')
        assert response.status_code == 200
    
    def test_listar_produtos_com_filtros_api(self, client, categoria_api, fornecedor_api):
        """Teste listagem de produtos com filtros via API."""
        # Criar vários produtos
        for i in range(3):
            client.post('/api/produtos', json={
                'nome': f'Produto Filtro {i}',
                'preco': 100.00 + (i * 50),
                'quantidade': 10,
                'categoria_id': categoria_api['id'],
                'fornecedor_id': fornecedor_api['id']
            })
        
        # Listar com filtros
        response = client.get('/api/produtos?preco_min=100&preco_max=200&ordenar_por=preco')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'produtos' in data
        assert len(data['produtos']) > 0
    
    def test_aplicar_desconto_api(self, client, categoria_api, fornecedor_api):
        """Teste aplicação de desconto via API."""
        # Criar produto
        response = client.post('/api/produtos', json={
            'nome': 'Produto Desconto',
            'preco': 200.00,
            'preco_custo': 100.00,
            'quantidade': 10,
            'categoria_id': categoria_api['id'],
            'fornecedor_id': fornecedor_api['id']
        })
        produto_id = response.get_json()['id']
        
        # Aplicar desconto
        response = client.post(f'/api/produtos/{produto_id}/desconto',
            json={'percentual_desconto': 15.0})
        
        assert response.status_code == 200
        produto = response.get_json()
        assert produto['preco'] == 170.00
    
    def test_fluxo_movimentos_api(self, client, categoria_api, fornecedor_api):
        """Teste fluxo de movimentos via API."""
        # Criar produto
        response = client.post('/api/produtos', json={
            'nome': 'Produto Movimento',
            'preco': 100.00,
            'quantidade': 50,
            'categoria_id': categoria_api['id'],
            'fornecedor_id': fornecedor_api['id']
        })
        produto_id = response.get_json()['id']
        
        # Criar usuário (simplificado)
        usuario_id = 1
        
        # Registrar entrada
        response = client.post('/api/movimentos/entrada', json={
            'produto_id': produto_id,
            'quantidade': 20,
            'usuario_id': usuario_id
        })
        assert response.status_code == 201
        
        # Registrar saída
        response = client.post('/api/movimentos/saida', json={
            'produto_id': produto_id,
            'quantidade': 10,
            'usuario_id': usuario_id
        })
        assert response.status_code == 201
        
        # Listar movimentos
        response = client.get(f'/api/movimentos?produto_id={produto_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 2
    
    def test_relatorios_api(self, client, categoria_api, fornecedor_api):
        """Teste geração de relatórios via API."""
        # Criar alguns produtos
        for i in range(3):
            client.post('/api/produtos', json={
                'nome': f'Produto Relatório {i}',
                'preco': 100.00,
                'quantidade': 10,
                'categoria_id': categoria_api['id'],
                'fornecedor_id': fornecedor_api['id']
            })
        
        # Gerar relatório de estoque
        response = client.get('/api/relatorios/estoque-atual')
        assert response.status_code == 200
        relatorio = response.get_json()
        assert 'total_produtos' in relatorio
        
        # Gerar relatório de categorias
        response = client.get('/api/relatorios/categorias')
        assert response.status_code == 200
        
        # Gerar relatório de fornecedores
        response = client.get('/api/relatorios/fornecedores')
        assert response.status_code == 200
    
    def test_erro_404_api(self, client):
        """Teste resposta 404 para endpoint inexistente."""
        response = client.get('/api/inexistente')
        assert response.status_code == 404
    
    def test_erro_produto_nao_encontrado_api(self, client):
        """Teste erro ao buscar produto inexistente."""
        response = client.get('/api/produtos/99999')
        assert response.status_code == 400  # Ou 404 dependendo da implementação