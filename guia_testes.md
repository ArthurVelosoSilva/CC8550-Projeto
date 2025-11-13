# Guia Completo de Testes - Sistema de Estoque

## Índice

1. [Estrutura dos Testes](#estrutura-dos-testes)
2. [Instalação](#instalação)
3. [Executar Todos os Testes](#executar-todos-os-testes)
4. [Executar por Categoria](#executar-por-categoria)
5. [Análise de Cobertura](#análise-de-cobertura)

---

## Estrutura dos Testes

```
tests/
├── conftest.py                          # Fixtures globais
├── unit/                                # Testes Unitários
│   ├── test_models.py
│   ├── test_validators.py
│   ├── test_repositories.py
│   └── test_services.py
├── integration/                         # Testes de Integração
│   ├── test_produto_integration.py
│   └── test_api_integration.py
├── functional/                          # Testes Funcionais
│   └── test_functional.py
├── structural/                          # Testes Estruturais
│   └── test_coverage.py
├── specific/                            # Testes Específicos
│   ├── test_api_endpoints.py
│   ├── test_exceptions.py
│   ├── test_mocks_stubs.py
│   └── test_performance.py
```

---

## Instalação

### 1. Instalar Dependências

```bash
# Certifique-se de estar no diretório do projeto
cd estoque_system

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências de teste
pip install pytest pytest-cov pytest-mock pytest-benchmark mutmut
```

### 2. Verificar Instalação

```bash
# Verificar pytest
pytest --version

# Verificar mutmut
mutmut --version

# Listar testes disponíveis
pytest --collect-only
```

---

## Executar Todos os Testes

```bash
# Executar todos os testes com cobertura
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
```

---

## Executar por Categoria

### 1. Testes Unitários

```bash
# Executar todos unitários
pytest tests/unit/ -v

# Por arquivo
pytest tests/unit/test_models.py -v
pytest tests/unit/test_validators.py -v
pytest tests/unit/test_repositories.py -v
pytest tests/unit/test_services.py -v

# Teste específico
pytest tests/unit/test_models.py::TestProdutoModel::test_criar_produto_basico -v
```

**Saída Esperada:**
```
tests/unit/test_models.py::TestProdutoModel::test_criar_produto_basico PASSED
tests/unit/test_models.py::TestProdutoModel::test_calcular_margem_lucro PASSED
...
============== 40 passed in 2.34s ==============
```

### 2. Testes de Integração

```bash
# Executar todos integração
pytest tests/integration/ -v

# Por arquivo
pytest tests/integration/test_produto_integration.py -v
pytest tests/integration/test_api_integration.py -v
```

**Saída Esperada:**
```
tests/integration/test_produto_integration.py::test_fluxo_completo_criar_atualizar_deletar_produto PASSED
tests/integration/test_api_integration.py::test_health_check PASSED
...
============== 15 passed in 5.67s ==============
```

### 3. Testes Funcionais

```bash
# Executar testes funcionais
pytest tests/functional/ -v

# Com descrição detalhada
pytest tests/functional/test_functional.py -v --tb=short
```

**Saída Esperada:**
```
CENÁRIO 1: Cadastrar produto com sucesso PASSED
CENÁRIO 2: Tentar cadastrar produto com preço inválido PASSED
...
============== 21 passed in 8.23s ==============
```

### 4. Testes Estruturais com Cobertura

```bash
# Executar com relatório de cobertura
pytest tests/structural/ --cov=src --cov-report=html --cov-report=term-missing

# Ver cobertura de branches
pytest tests/structural/ --cov=src --cov-branch

# Falhar se cobertura < 80%
pytest tests/structural/ --cov=src --cov-fail-under=80
```

**Saída Esperada:**
```
---------- coverage: platform linux, python 3.11.0 -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/models/produto.py                     45      2    96%
src/services/produto_service.py          120      8    93%
src/utils/validators.py                   85      5    94%
...
-----------------------------------------------------------
TOTAL                                   1250     95    92%
```

### 5. Testes Específicos (4 tipos)

```bash
# Testes de API
pytest tests/specific/test_api_endpoints.py -v

# Testes de Exceções
pytest tests/specific/test_exceptions.py -v

# Testes com Mocks
pytest tests/specific/test_mocks_stubs.py -v

# Testes de Performance
pytest tests/specific/test_performance.py -v

# Com benchmark
pytest tests/specific/test_performance.py --benchmark-only
```

---

## Análise de Cobertura

### Gerar Relatório HTML

```bash
# Gerar relatório completo
pytest tests/ --cov=src --cov-report=html

# Abrir relatório
open htmlcov/index.html     # Mac
xdg-open htmlcov/index.html # Linux
start htmlcov/index.html    # Windows
```

### Análise por Módulo

```bash
# Ver cobertura por arquivo
pytest tests/ --cov=src --cov-report=term-missing

# Ver apenas módulos específicos
pytest tests/ --cov=src/services --cov-report=term
```

### Cobertura de Branches

```bash
# Incluir cobertura de branches (if/else)
pytest tests/ --cov=src --cov-branch --cov-report=html
```

---