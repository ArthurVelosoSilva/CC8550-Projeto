# ===========================
# main.py
# ===========================
"""
Ponto de entrada principal do sistema de estoque.
"""
import sys
import os
from datetime import datetime, date
from src.api.routes import criar_app
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
from src.utils.logger import get_logger
from config.settings import settings
import hashlib


logger = get_logger(__name__)

def inicializar_dados_exemplo(db_path: str = 'estoque.db'):
    """
    Inicializa banco com dados de exemplo.
    
    Args:
        db_path: Caminho do banco de dados
    """
    logger.info("Inicializando dados de exemplo...")
    
    # Inicializar repositories
    categoria_repo = CategoriaRepository(db_path)
    fornecedor_repo = FornecedorRepository(db_path)
    produto_repo = ProdutoRepository(db_path)
    usuario_repo = UsuarioRepository(db_path)
    movimento_repo = MovimentoRepository(db_path)
    
    # Inicializar services
    fornecedor_service = FornecedorService(fornecedor_repo)
    produto_service = ProdutoService(produto_repo, categoria_repo, fornecedor_repo)
    movimento_service = MovimentoService(movimento_repo, produto_repo)
    
    try:
        # Criar usuário admin
        senha_hash = hashlib.sha256("admin123".encode()).hexdigest()
        usuario = Usuario(
            nome="Administrador",
            email="admin@estoque.com",
            senha_hash=senha_hash
        )
        usuario = usuario_repo.create(usuario)
        logger.info(f"Usuário criado: {usuario.email}")
        
        # Criar categorias
        categorias_data = [
            {"nome": "Eletrônicos", "descricao": "Produtos eletrônicos e tecnologia"},
            {"nome": "Alimentos", "descricao": "Produtos alimentícios"},
            {"nome": "Vestuário", "descricao": "Roupas e acessórios"},
            {"nome": "Limpeza", "descricao": "Produtos de limpeza"},
            {"nome": "Ferramentas", "descricao": "Ferramentas e equipamentos"}
        ]
        
        categorias = []
        for cat_data in categorias_data:
            categoria = Categoria(**cat_data)
            categoria = categoria_repo.create(categoria)
            categorias.append(categoria)
            logger.info(f"Categoria criada: {categoria.nome}")
        
        # Criar fornecedores
        fornecedores_data = [
            {
                "nome": "Tech Distribuidora LTDA",
                "cnpj": "12345678000190",
                "email": "contato@techdist.com",
                "telefone": "11987654321",
                "cidade": "São Paulo",
                "estado": "SP",
                "prazo_entrega_dias": 5
            },
            {
                "nome": "Alimentos Brasil S.A.",
                "cnpj": "98765432000180",
                "email": "vendas@alimentosbrasil.com",
                "telefone": "11912345678",
                "cidade": "Campinas",
                "estado": "SP",
                "prazo_entrega_dias": 3
            },
            {
                "nome": "Moda e Estilo Atacado",
                "cnpj": "11122233000145",
                "email": "comercial@modaestilo.com",
                "telefone": "11923456789",
                "cidade": "Rio de Janeiro",
                "estado": "RJ",
                "prazo_entrega_dias": 7
            }
        ]
        
        fornecedores = []
        for forn_data in fornecedores_data:
            fornecedor = fornecedor_service.criar_fornecedor(**forn_data)
            fornecedores.append(fornecedor)
            logger.info(f"Fornecedor criado: {fornecedor.nome}")
        
        # Criar produtos
        produtos_data = [
            {
                "nome": "Notebook Dell Inspiron",
                "codigo": "NB-001",
                "descricao": "Notebook i5, 8GB RAM, 256GB SSD",
                "preco": 3500.00,
                "preco_custo": 2800.00,
                "quantidade": 15,
                "categoria_id": categorias[0].id,
                "fornecedor_id": fornecedores[0].id,
                "estoque_minimo": 5,
                "estoque_maximo": 50,
                "localizacao": "A1-P1"
            },
            {
                "nome": "Mouse Logitech MX Master",
                "codigo": "MS-001",
                "preco": 350.00,
                "preco_custo": 250.00,
                "quantidade": 30,
                "categoria_id": categorias[0].id,
                "fornecedor_id": fornecedores[0].id,
                "estoque_minimo": 10,
                "localizacao": "A1-P2"
            },
            {
                "nome": "Arroz Tipo 1 - 5kg",
                "codigo": "AL-001",
                "preco": 25.00,
                "preco_custo": 18.00,
                "quantidade": 100,
                "categoria_id": categorias[1].id,
                "fornecedor_id": fornecedores[1].id,
                "estoque_minimo": 30,
                "data_validade": date(2025, 12, 31)
            },
            {
                "nome": "Feijão Preto - 1kg",
                "codigo": "AL-002",
                "preco": 8.50,
                "preco_custo": 6.00,
                "quantidade": 150,
                "categoria_id": categorias[1].id,
                "fornecedor_id": fornecedores[1].id,
                "estoque_minimo": 50,
                "data_validade": date(2025, 11, 30)
            },
            {
                "nome": "Camiseta Básica Algodão",
                "codigo": "VS-001",
                "preco": 45.00,
                "preco_custo": 25.00,
                "quantidade": 8,
                "categoria_id": categorias[2].id,
                "fornecedor_id": fornecedores[2].id,
                "estoque_minimo": 20,
                "localizacao": "B2-P1"
            },
            {
                "nome": "Detergente Líquido 500ml",
                "codigo": "LP-001",
                "preco": 3.50,
                "preco_custo": 2.00,
                "quantidade": 200,
                "categoria_id": categorias[3].id,
                "fornecedor_id": fornecedores[1].id,
                "estoque_minimo": 100
            },
            {
                "nome": "Desinfetante 1L",
                "codigo": "LP-002",
                "preco": 6.00,
                "preco_custo": 3.50,
                "quantidade": 120,
                "categoria_id": categorias[3].id,
                "fornecedor_id": fornecedores[1].id,
                "estoque_minimo": 80
            },
            {
                "nome": "Furadeira Elétrica 500W",
                "codigo": "FR-001",
                "preco": 250.00,
                "preco_custo": 180.00,
                "quantidade": 12,
                "categoria_id": categorias[4].id,
                "fornecedor_id": fornecedores[0].id,
                "estoque_minimo": 5,
                "localizacao": "C1-P3"
            }
        ]
        
        produtos = []
        for prod_data in produtos_data:
            produto = produto_service.criar_produto(**prod_data)
            produtos.append(produto)
            logger.info(f"Produto criado: {produto.nome}")
        
        # Registrar alguns movimentos
        movimento_service.registrar_entrada(
            produto_id=produtos[0].id,
            quantidade=5,
            usuario_id=usuario.id,
            observacao="Compra inicial"
        )
        
        movimento_service.registrar_saida(
            produto_id=produtos[1].id,
            quantidade=10,
            usuario_id=usuario.id,
            observacao="Venda para cliente"
        )
        
        logger.info("Dados de exemplo inicializados com sucesso!")
        print("\n" + "="*60)
        print("DADOS DE EXEMPLO CRIADOS COM SUCESSO!")
        print("="*60)
        print(f"Categorias: {len(categorias)}")
        print(f"Fornecedores: {len(fornecedores)}")
        print(f"Produtos: {len(produtos)}")
        print(f"Usuário admin: {usuario.email} / senha: admin123")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar dados: {e}", exc_info=True)
        print(f"\nErro ao inicializar dados: {e}\n")


def menu_principal():
    """Menu interativo CLI."""
    print("\n" + "="*60)
    print("SISTEMA DE GERENCIAMENTO DE ESTOQUE")
    print("="*60)
    print("1. Iniciar API REST")
    print("2. Inicializar dados de exemplo")
    print("3. Gerar relatório de estoque")
    print("4. Verificar produtos críticos")
    print("5. Sair")
    print("="*60)
    
    return input("\nEscolha uma opção: ").strip()


def main():
    """Função principal."""
    db_path = settings.get('database.name', 'estoque.db')
    
    while True:
        opcao = menu_principal()
        
        if opcao == '1':
            # Iniciar API
            print("\nIniciando API REST...")
            api_host = settings.get('api.host', '0.0.0.0')
            api_port = settings.get('api.port', 5000)
            api_debug = settings.get('api.debug', False)
            
            app = criar_app(db_path)
            
            print(f"\nAPI rodando em http://{api_host}:{api_port}")
            print("Documentação: http://localhost:5000/api")
            print("Health check: http://localhost:5000/api/health")
            print("\nPressione Ctrl+C para parar o servidor\n")
            
            try:
                app.run(host=api_host, port=api_port, debug=api_debug)
            except KeyboardInterrupt:
                print("\n\nServidor encerrado.")
            
        elif opcao == '2':
            # Inicializar dados
            resposta = input("\nDeseja inicializar dados de exemplo? (s/n): ").lower()
            if resposta == 's':
                inicializar_dados_exemplo(db_path)
            
        elif opcao == '3':
            # Gerar relatório
            print("\nGerando relatório de estoque atual...")
            produto_repo = ProdutoRepository(db_path)
            categoria_repo = CategoriaRepository(db_path)
            fornecedor_repo = FornecedorRepository(db_path)
            movimento_repo = MovimentoRepository(db_path)
            
            relatorio_service = RelatorioService(
                produto_repo, movimento_repo, categoria_repo, fornecedor_repo
            )
            
            relatorio = relatorio_service.gerar_relatorio_estoque_atual()
            
            print("\n" + "="*60)
            print("RELATÓRIO DE ESTOQUE ATUAL")
            print("="*60)
            print(f"Data: {relatorio['data_geracao']}")
            print(f"Total de produtos: {relatorio['total_produtos']}")
            print(f"Total de itens em estoque: {relatorio['total_itens_estoque']}")
            print(f"Valor total do estoque: R$ {relatorio['valor_total_estoque']:.2f}")
            print(f"Valor de custo total: R$ {relatorio['valor_custo_total']:.2f}")
            print(f"Margem de lucro média: {relatorio['margem_lucro_media']:.2f}%")
            print(f"Produtos em estoque crítico: {relatorio['produtos_criticos']}")
            print("="*60)
            
            # Exportar
            exportar = input("\nDeseja exportar relatório? (s/n): ").lower()
            if exportar == 's':
                formato = input("Formato (json/csv): ").lower()
                filepath = input("Caminho do arquivo: ").strip()
                
                if formato == 'json':
                    sucesso = relatorio_service.exportar_relatorio_json(relatorio, filepath)
                elif formato == 'csv':
                    sucesso = relatorio_service.exportar_relatorio_csv(relatorio, filepath)
                else:
                    print("Formato inválido!")
                    sucesso = False
                
                if sucesso:
                    print(f"Relatório exportado para: {filepath}")
                else:
                    print("Falha ao exportar relatório!")
            
        elif opcao == '4':
            # Verificar produtos críticos
            print("\nVerificando produtos críticos...")
            produto_repo = ProdutoRepository(db_path)
            categoria_repo = CategoriaRepository(db_path)
            fornecedor_repo = FornecedorRepository(db_path)
            
            produto_service = ProdutoService(produto_repo, categoria_repo, fornecedor_repo)
            alertas = produto_service.verificar_produtos_criticos()
            
            print("\n" + "="*60)
            print("PRODUTOS EM SITUAÇÃO CRÍTICA")
            print("="*60)
            print(f"Total de alertas: {len(alertas)}\n")
            
            if alertas:
                for i, alerta in enumerate(alertas, 1):
                    print(f"{i}. {alerta['nome']}")
                    print(f"   Tipo: {alerta['tipo_alerta']}")
                    print(f"   Recomendação: {alerta['recomendacao']}")
                    print()
            else:
                print("Nenhum produto em situação crítica!")
            
            print("="*60)
            
        elif opcao == '5':
            # Sair
            print("\nEncerrando sistema...")
            sys.exit(0)
            
        else:
            print("\nOpção inválida! Tente novamente.")
        
        input("\nPressione Enter para continuar...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSistema encerrado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro crítico: {e}", exc_info=True)
        print(f"\nErro crítico: {e}")
        sys.exit(1)