# ===========================
# src/api/routes.py
# ===========================
"""
API REST para o sistema de estoque usando Flask.
"""
from flask import Flask, request, jsonify
from typing import Dict, Any
from datetime import datetime, date
from functools import wraps
from src.repositories.produto_repository import ProdutoRepository
from src.repositories.categoria_repository import CategoriaRepository
from src.repositories.fornecedor_repository import FornecedorRepository
from src.repositories.movimento_repository import MovimentoRepository
from src.repositories.usuario_repository import UsuarioRepository
from src.services.produto_service import ProdutoService
from src.services.fornecedor_service import FornecedorService
from src.services.movimento_service import MovimentoService
from src.services.relatorio_service import RelatorioService
from src.utils.logger import get_logger
from src.exceptions.custom_exceptions import EstoqueException
from config.settings import settings


logger = get_logger(__name__)


def criar_app(db_path: str = 'estoque.db') -> Flask:
    """
    Factory para criar aplicação Flask.
    
    Args:
        db_path: Caminho do banco de dados
        
    Returns:
        Aplicação Flask configurada
    """
    app = Flask(__name__)
    
    # Configurações
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Inicializar repositories
    produto_repo = ProdutoRepository(db_path)
    categoria_repo = CategoriaRepository(db_path)
    fornecedor_repo = FornecedorRepository(db_path)
    movimento_repo = MovimentoRepository(db_path)
    usuario_repo = UsuarioRepository(db_path)
    
    # Inicializar services
    produto_service = ProdutoService(produto_repo, categoria_repo, fornecedor_repo)
    fornecedor_service = FornecedorService(fornecedor_repo)
    movimento_service = MovimentoService(movimento_repo, produto_repo)
    relatorio_service = RelatorioService(
        produto_repo, movimento_repo, categoria_repo, fornecedor_repo
    )
    
    # Decorator para tratamento de erros
    def handle_errors(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except EstoqueException as e:
                logger.error(f"Erro de negócio: {e}", exc_info=True)
                return jsonify({
                    'erro': type(e).__name__,
                    'mensagem': str(e)
                }), 400
            except Exception as e:
                logger.error(f"Erro inesperado: {e}", exc_info=True)
                return jsonify({
                    'erro': 'ErroInterno',
                    'mensagem': 'Erro interno no servidor'
                }), 500
        return decorated_function
    
    # ===========================
    # ROTAS - PRODUTOS
    # ===========================
    
    @app.route('/api/produtos', methods=['GET'])
    @handle_errors
    def listar_produtos():
        """Lista produtos com filtros opcionais."""
        categoria_id = request.args.get('categoria_id', type=int)
        fornecedor_id = request.args.get('fornecedor_id', type=int)
        preco_min = request.args.get('preco_min', type=float)
        preco_max = request.args.get('preco_max', type=float)
        ordenar_por = request.args.get('ordenar_por', default='nome')
        ordem = request.args.get('ordem', default='ASC')
        
        produtos = produto_service.listar_produtos(
            categoria_id=categoria_id,
            fornecedor_id=fornecedor_id,
            preco_min=preco_min,
            preco_max=preco_max,
            ordenar_por=ordenar_por,
            ordem=ordem
        )
        
        return jsonify({
            'total': len(produtos),
            'produtos': [p.to_dict() for p in produtos]
        }), 200
    
    @app.route('/api/produtos/<int:produto_id>', methods=['GET'])
    @handle_errors
    def buscar_produto(produto_id: int):
        """Busca produto por ID."""
        produto = produto_service.buscar_produto(produto_id)
        return jsonify(produto.to_dict()), 200
    
    @app.route('/api/produtos', methods=['POST'])
    @handle_errors
    def criar_produto():
        """Cria novo produto."""
        dados = request.get_json()
        
        # Converter data_validade se fornecida
        data_validade = None
        if 'data_validade' in dados and dados['data_validade']:
            data_validade = date.fromisoformat(dados['data_validade'])
        
        produto = produto_service.criar_produto(
            nome=dados['nome'],
            preco=dados['preco'],
            quantidade=dados['quantidade'],
            categoria_id=dados['categoria_id'],
            fornecedor_id=dados['fornecedor_id'],
            codigo=dados.get('codigo'),
            descricao=dados.get('descricao'),
            preco_custo=dados.get('preco_custo'),
            estoque_minimo=dados.get('estoque_minimo', 10),
            estoque_maximo=dados.get('estoque_maximo', 1000),
            localizacao=dados.get('localizacao'),
            data_validade=data_validade
        )
        
        return jsonify(produto.to_dict()), 201
    
    @app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
    @handle_errors
    def atualizar_produto(produto_id: int):
        """Atualiza produto."""
        dados = request.get_json()
        produto = produto_service.buscar_produto(produto_id)
        
        # Atualizar campos
        produto.nome = dados.get('nome', produto.nome)
        produto.preco = dados.get('preco', produto.preco)
        produto.quantidade = dados.get('quantidade', produto.quantidade)
        produto.categoria_id = dados.get('categoria_id', produto.categoria_id)
        produto.fornecedor_id = dados.get('fornecedor_id', produto.fornecedor_id)
        produto.codigo = dados.get('codigo', produto.codigo)
        produto.descricao = dados.get('descricao', produto.descricao)
        produto.preco_custo = dados.get('preco_custo', produto.preco_custo)
        produto.estoque_minimo = dados.get('estoque_minimo', produto.estoque_minimo)
        produto.estoque_maximo = dados.get('estoque_maximo', produto.estoque_maximo)
        produto.localizacao = dados.get('localizacao', produto.localizacao)
        
        if 'data_validade' in dados and dados['data_validade']:
            produto.data_validade = date.fromisoformat(dados['data_validade'])
        
        produto = produto_service.atualizar_produto(produto)
        return jsonify(produto.to_dict()), 200
    
    @app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
    @handle_errors
    def deletar_produto(produto_id: int):
        """Deleta produto."""
        produto_service.deletar_produto(produto_id)
        return jsonify({'mensagem': 'Produto deletado com sucesso'}), 200
    
    @app.route('/api/produtos/<int:produto_id>/desconto', methods=['POST'])
    @handle_errors
    def aplicar_desconto(produto_id: int):
        """Aplica desconto a um produto."""
        dados = request.get_json()
        percentual = dados.get('percentual_desconto')
        
        if not percentual:
            return jsonify({'erro': 'percentual_desconto é obrigatório'}), 400
        
        produto = produto_service.aplicar_desconto(produto_id, percentual)
        return jsonify(produto.to_dict()), 200
    
    @app.route('/api/produtos/criticos', methods=['GET'])
    @handle_errors
    def produtos_criticos():
        """Lista produtos em situação crítica."""
        alertas = produto_service.verificar_produtos_criticos()
        return jsonify({
            'total_alertas': len(alertas),
            'alertas': alertas
        }), 200
    
    @app.route('/api/produtos/buscar', methods=['GET'])
    @handle_errors
    def buscar_produtos_por_nome():
        """Busca produtos por nome."""
        nome = request.args.get('nome', '')
        if not nome:
            return jsonify({'erro': 'Parâmetro nome é obrigatório'}), 400
        
        produtos = produto_repo.buscar_por_nome(nome)
        return jsonify({
            'total': len(produtos),
            'produtos': [p.to_dict() for p in produtos]
        }), 200
    
    # ===========================
    # ROTAS - CATEGORIAS
    # ===========================
    
    @app.route('/api/categorias', methods=['GET'])
    @handle_errors
    def listar_categorias():
        """Lista todas categorias."""
        categorias = categoria_repo.list_all()
        return jsonify({
            'total': len(categorias),
            'categorias': [c.to_dict() for c in categorias]
        }), 200
    
    @app.route('/api/categorias/<int:categoria_id>', methods=['GET'])
    @handle_errors
    def buscar_categoria(categoria_id: int):
        """Busca categoria por ID."""
        from src.models.categoria import Categoria
        categoria = categoria_repo.read(categoria_id)
        if not categoria:
            return jsonify({'erro': 'Categoria não encontrada'}), 404
        return jsonify(categoria.to_dict()), 200
    
    @app.route('/api/categorias', methods=['POST'])
    @handle_errors
    def criar_categoria():
        """Cria nova categoria."""
        from src.models.categoria import Categoria
        dados = request.get_json()
        
        categoria = Categoria(
            nome=dados['nome'],
            descricao=dados.get('descricao')
        )
        
        categoria = categoria_repo.create(categoria)
        return jsonify(categoria.to_dict()), 201
    
    @app.route('/api/categorias/<int:categoria_id>', methods=['PUT'])
    @handle_errors
    def atualizar_categoria(categoria_id: int):
        """Atualiza categoria."""
        dados = request.get_json()
        categoria = categoria_repo.read(categoria_id)
        
        if not categoria:
            return jsonify({'erro': 'Categoria não encontrada'}), 404
        
        categoria.nome = dados.get('nome', categoria.nome)
        categoria.descricao = dados.get('descricao', categoria.descricao)
        
        categoria = categoria_repo.update(categoria)
        return jsonify(categoria.to_dict()), 200
    
    @app.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
    @handle_errors
    def deletar_categoria(categoria_id: int):
        """Deleta categoria."""
        categoria_repo.delete(categoria_id)
        return jsonify({'mensagem': 'Categoria deletada com sucesso'}), 200
    
    # ===========================
    # ROTAS - FORNECEDORES
    # ===========================
    
    @app.route('/api/fornecedores', methods=['GET'])
    @handle_errors
    def listar_fornecedores():
        """Lista todos fornecedores."""
        fornecedores = fornecedor_service.listar_fornecedores()
        return jsonify({
            'total': len(fornecedores),
            'fornecedores': [f.to_dict() for f in fornecedores]
        }), 200
    
    @app.route('/api/fornecedores/<int:fornecedor_id>', methods=['GET'])
    @handle_errors
    def buscar_fornecedor(fornecedor_id: int):
        """Busca fornecedor por ID."""
        fornecedor = fornecedor_service.buscar_fornecedor(fornecedor_id)
        return jsonify(fornecedor.to_dict()), 200
    
    @app.route('/api/fornecedores', methods=['POST'])
    @handle_errors
    def criar_fornecedor():
        """Cria novo fornecedor."""
        dados = request.get_json()
        
        fornecedor = fornecedor_service.criar_fornecedor(
            nome=dados['nome'],
            cnpj=dados['cnpj'],
            email=dados['email'],
            telefone=dados['telefone'],
            endereco=dados.get('endereco'),
            cidade=dados.get('cidade'),
            estado=dados.get('estado'),
            cep=dados.get('cep'),
            contato_principal=dados.get('contato_principal'),
            prazo_entrega_dias=dados.get('prazo_entrega_dias', 7)
        )
        
        return jsonify(fornecedor.to_dict()), 201
    
    @app.route('/api/fornecedores/<int:fornecedor_id>', methods=['PUT'])
    @handle_errors
    def atualizar_fornecedor(fornecedor_id: int):
        """Atualiza fornecedor."""
        dados = request.get_json()
        fornecedor = fornecedor_service.buscar_fornecedor(fornecedor_id)
        
        fornecedor.nome = dados.get('nome', fornecedor.nome)
        fornecedor.cnpj = dados.get('cnpj', fornecedor.cnpj)
        fornecedor.email = dados.get('email', fornecedor.email)
        fornecedor.telefone = dados.get('telefone', fornecedor.telefone)
        fornecedor.endereco = dados.get('endereco', fornecedor.endereco)
        fornecedor.cidade = dados.get('cidade', fornecedor.cidade)
        fornecedor.estado = dados.get('estado', fornecedor.estado)
        fornecedor.cep = dados.get('cep', fornecedor.cep)
        fornecedor.contato_principal = dados.get('contato_principal', fornecedor.contato_principal)
        fornecedor.prazo_entrega_dias = dados.get('prazo_entrega_dias', fornecedor.prazo_entrega_dias)
        
        fornecedor = fornecedor_service.atualizar_fornecedor(fornecedor)
        return jsonify(fornecedor.to_dict()), 200
    
    @app.route('/api/fornecedores/<int:fornecedor_id>', methods=['DELETE'])
    @handle_errors
    def deletar_fornecedor(fornecedor_id: int):
        """Deleta fornecedor."""
        fornecedor_service.deletar_fornecedor(fornecedor_id)
        return jsonify({'mensagem': 'Fornecedor deletado com sucesso'}), 200
    
    # ===========================
    # ROTAS - MOVIMENTOS
    # ===========================
    
    @app.route('/api/movimentos', methods=['GET'])
    @handle_errors
    def listar_movimentos():
        """Lista movimentos com filtros opcionais."""
        produto_id = request.args.get('produto_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if data_inicio and data_fim:
            data_inicio = datetime.fromisoformat(data_inicio)
            data_fim = datetime.fromisoformat(data_fim)
            movimentos = movimento_service.listar_movimentos_periodo(data_inicio, data_fim)
        elif produto_id:
            movimentos = movimento_service.listar_movimentos_produto(produto_id)
        else:
            movimentos = movimento_repo.list_all()
        
        return jsonify({
            'total': len(movimentos),
            'movimentos': [m.to_dict() for m in movimentos]
        }), 200
    
    @app.route('/api/movimentos/entrada', methods=['POST'])
    @handle_errors
    def registrar_entrada():
        """Registra entrada de estoque."""
        dados = request.get_json()
        
        movimento = movimento_service.registrar_entrada(
            produto_id=dados['produto_id'],
            quantidade=dados['quantidade'],
            usuario_id=dados['usuario_id'],
            observacao=dados.get('observacao')
        )
        
        return jsonify(movimento.to_dict()), 201
    
    @app.route('/api/movimentos/saida', methods=['POST'])
    @handle_errors
    def registrar_saida():
        """Registra saída de estoque."""
        dados = request.get_json()
        
        movimento = movimento_service.registrar_saida(
            produto_id=dados['produto_id'],
            quantidade=dados['quantidade'],
            usuario_id=dados['usuario_id'],
            observacao=dados.get('observacao')
        )
        
        return jsonify(movimento.to_dict()), 201
    
    @app.route('/api/movimentos/ajuste', methods=['POST'])
    @handle_errors
    def registrar_ajuste():
        """Registra ajuste de estoque."""
        dados = request.get_json()
        
        movimento = movimento_service.registrar_ajuste(
            produto_id=dados['produto_id'],
            nova_quantidade=dados['nova_quantidade'],
            usuario_id=dados['usuario_id'],
            observacao=dados['observacao']
        )
        
        return jsonify(movimento.to_dict()), 201
    
    # ===========================
    # ROTAS - RELATÓRIOS
    # ===========================
    
    @app.route('/api/relatorios/estoque-atual', methods=['GET'])
    @handle_errors
    def relatorio_estoque_atual():
        """Gera relatório do estoque atual."""
        relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        return jsonify(relatorio), 200
    
    @app.route('/api/relatorios/movimentacao', methods=['GET'])
    @handle_errors
    def relatorio_movimentacao():
        """Gera relatório de movimentação."""
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'erro': 'data_inicio e data_fim são obrigatórios'}), 400
        
        data_inicio = datetime.fromisoformat(data_inicio)
        data_fim = datetime.fromisoformat(data_fim)
        
        relatorio = relatorio_service.gerar_relatorio_movimentacao(data_inicio, data_fim)
        return jsonify(relatorio), 200
    
    @app.route('/api/relatorios/categorias', methods=['GET'])
    @handle_errors
    def relatorio_categorias():
        """Gera relatório por categorias."""
        relatorio = relatorio_service.gerar_relatorio_categorias()
        return jsonify(relatorio), 200
    
    @app.route('/api/relatorios/fornecedores', methods=['GET'])
    @handle_errors
    def relatorio_fornecedores():
        """Gera relatório por fornecedores."""
        relatorio = relatorio_service.gerar_relatorio_fornecedores()
        return jsonify(relatorio), 200
    
    @app.route('/api/relatorios/exportar', methods=['POST'])
    @handle_errors
    def exportar_relatorio():
        """Exporta relatório para arquivo."""
        dados = request.get_json()
        tipo_relatorio = dados.get('tipo_relatorio')
        formato = dados.get('formato', 'json')
        filepath = dados.get('filepath')
        
        if not tipo_relatorio or not filepath:
            return jsonify({'erro': 'tipo_relatorio e filepath são obrigatórios'}), 400
        
        # Gerar relatório apropriado
        if tipo_relatorio == 'estoque':
            relatorio = relatorio_service.gerar_relatorio_estoque_atual()
        elif tipo_relatorio == 'categorias':
            relatorio = relatorio_service.gerar_relatorio_categorias()
        elif tipo_relatorio == 'fornecedores':
            relatorio = relatorio_service.gerar_relatorio_fornecedores()
        else:
            return jsonify({'erro': 'tipo_relatorio inválido'}), 400
        
        # Exportar
        if formato == 'json':
            sucesso = relatorio_service.exportar_relatorio_json(relatorio, filepath)
        elif formato == 'csv':
            sucesso = relatorio_service.exportar_relatorio_csv(relatorio, filepath)
        else:
            return jsonify({'erro': 'formato inválido'}), 400
        
        if sucesso:
            return jsonify({'mensagem': 'Relatório exportado com sucesso', 'filepath': filepath}), 200
        else:
            return jsonify({'erro': 'Falha ao exportar relatório'}), 500
    
    # ===========================
    # ROTAS - UTILITÁRIAS
    # ===========================
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check da API."""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }), 200
    
    @app.route('/api', methods=['GET'])
    def api_info():
        """Informações sobre a API."""
        return jsonify({
            'nome': 'Sistema de Gerenciamento de Estoque',
            'versao': '1.0.0',
            'endpoints': {
                'produtos': '/api/produtos',
                'categorias': '/api/categorias',
                'fornecedores': '/api/fornecedores',
                'movimentos': '/api/movimentos',
                'relatorios': '/api/relatorios'
            }
        }), 200
    
    @app.errorhandler(404)
    def not_found(error):
        """Handler para 404."""
        return jsonify({'erro': 'Endpoint não encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handler para 500."""
        logger.error(f"Erro interno: {error}", exc_info=True)
        return jsonify({'erro': 'Erro interno no servidor'}), 500
    
    return app