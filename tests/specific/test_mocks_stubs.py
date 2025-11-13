# ===========================
# tests/specific/test_mocks_stubs.py
# ===========================
"""
Testes com mocks e stubs (requisito: pelo menos 2 tipos).
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime


class TestMocksAndStubs:
    """Testes usando mocks e stubs para isolar dependências."""
    
    def test_mock_api_externa(self):
        """Simula chamada a API externa com mock."""
        with patch('requests.get') as mock_get:
            # Configurar resposta mock
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'ok'}
            mock_get.return_value = mock_response
            
            # Usar mock (simularia integração com API externa)
            import requests
            response = requests.get('https://api.example.com/status')
            
            assert response.status_code == 200
            assert response.json() == {'status': 'ok'}
            mock_get.assert_called_once_with('https://api.example.com/status')
    
    def test_spy_verifica_chamadas_metodo(self):
        """Usa spy para verificar chamadas de método."""
        from src.services.movimento_service import MovimentoService
        
        movimento_repo_mock = Mock()
        produto_repo_mock = Mock()
        
        # Configurar mocks
        produto_mock = Mock()
        produto_mock.quantidade = 10
        produto_mock.estoque_maximo = 100
        produto_repo_mock.read.return_value = produto_mock
        produto_repo_mock.atualizar_quantidade.return_value = True
        
        movimento_mock = Mock()
        movimento_mock.id = 1
        movimento_repo_mock.create.return_value = movimento_mock
        
        service = MovimentoService(movimento_repo_mock, produto_repo_mock)
        
        # Executar operação
        service.registrar_entrada(1, 5, 1)
        
        # Verificar sequência de chamadas
        assert produto_repo_mock.read.called
        assert produto_repo_mock.atualizar_quantidade.called
        assert movimento_repo_mock.create.called
        
        # Verificar ordem de chamadas
        expected_calls = [
            call.read(1),
            call.atualizar_quantidade(1, 15)
        ]
        produto_repo_mock.assert_has_calls(expected_calls)
    
    def test_mock_file_handler_isolamento(self):
        """Testa isolamento de operações de arquivo com mock."""
        from src.services.relatorio_service import RelatorioService
        
        with patch('src.utils.file_handler.FileHandler.exportar_json') as mock_export:
            mock_export.return_value = True
            
            # Criar mocks de repositories
            produto_repo_mock = Mock()
            movimento_repo_mock = Mock()
            categoria_repo_mock = Mock()
            fornecedor_repo_mock = Mock()
            
            produto_repo_mock.list_all.return_value = []
            
            service = RelatorioService(
                produto_repo_mock,
                movimento_repo_mock,
                categoria_repo_mock,
                fornecedor_repo_mock
            )
            
            relatorio = service.gerar_relatorio_estoque_atual()
            resultado = service.exportar_relatorio_json(relatorio, 'test.json')
            
            assert resultado is True
            mock_export.assert_called_once()