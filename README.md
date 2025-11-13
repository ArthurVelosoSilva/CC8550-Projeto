# Sistema de Gerenciamento de Estoque

Sistema completo de gerenciamento de estoque desenvolvido em Python com arquitetura modular.

## Funcionalidades

### CRUD Completo (5 entidades)
- Produtos
- Categorias
- Fornecedores
- Movimentos de Estoque
- Usuários

### Regras de Negócio Complexas (3)
1. **Validação Complexa de Produto**: Valida todos os campos, verifica relacionamentos, valida preços e datas
2. **Aplicação de Desconto com Limites**: Aplica desconto respeitando limites e não permitindo preço abaixo do custo
3. **Análise de Produtos Críticos**: Identifica produtos com estoque baixo, próximos do vencimento ou margem baixa

### Consultas/Buscas com Filtros (2)
1. **Busca de Produtos**: Filtros por categoria, fornecedor, faixa de preço, com ordenação customizável
2. **Movimentos por Período**: Consulta movimentos de estoque em período específico

## Arquitetura

```
estoque_system/
├── config/              # Configurações
├── src/
│   ├── models/         # Modelos de dados (dataclasses)
│   ├── repositories/   # Camada de acesso a dados (Repository Pattern)
│   ├── services/       # Lógica de negócio
│   ├── api/            # API REST (Flask)
│   ├── utils/          # Utilitários (logger, validators, file_handler)
│   └── exceptions/     # Exceções personalizadas
├── tests/              # Testes
├── logs/               # Arquivos de log
├── main.py             # Ponto de entrada
└── requirements.txt    # Dependências
```

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\\Scripts\\activate

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

1. Copie `.env.example` para `.env`
2. Ajuste as configurações conforme necessário
3. Ou crie um arquivo `config.yaml` com suas configurações

## Uso

### CLI Interativo

```bash
python main.py
```

### API REST

```bash
# Iniciar via menu CLI ou diretamente:
python -c "from src.api.routes import criar_app; app = criar_app(); app.run()"
```

### Endpoints da API

**Produtos**
- `GET /api/produtos` - Listar produtos
- `GET /api/produtos/<id>` - Buscar produto
- `POST /api/produtos` - Criar produto
- `PUT /api/produtos/<id>` - Atualizar produto
- `DELETE /api/produtos/<id>` - Deletar produto
- `POST /api/produtos/<id>/desconto` - Aplicar desconto
- `GET /api/produtos/criticos` - Produtos críticos

**Categorias**
- `GET /api/categorias` - Listar categorias
- `POST /api/categorias` - Criar categoria
- `PUT /api/categorias/<id>` - Atualizar categoria
- `DELETE /api/categorias/<id>` - Deletar categoria

**Fornecedores**
- `GET /api/fornecedores` - Listar fornecedores
- `POST /api/fornecedores` - Criar fornecedor
- `PUT /api/fornecedores/<id>` - Atualizar fornecedor
- `DELETE /api/fornecedores/<id>` - Deletar fornecedor

**Movimentos**
- `GET /api/movimentos` - Listar movimentos
- `POST /api/movimentos/entrada` - Registrar entrada
- `POST /api/movimentos/saida` - Registrar saída
- `POST /api/movimentos/ajuste` - Registrar ajuste

**Relatórios**
- `GET /api/relatorios/estoque-atual` - Relatório de estoque
- `GET /api/relatorios/movimentacao` - Relatório de movimentação
- `GET /api/relatorios/categorias` - Relatório por categorias
- `GET /api/relatorios/fornecedores` - Relatório por fornecedores
- `POST /api/relatorios/exportar` - Exportar relatório

## Testes

Os testes devem ser implementados conforme requisitos do projeto:
- Testes unitários (30+ casos)
- Testes de integração (10+ casos)
- Testes funcionais (8+ cenários)
- Testes estruturais (80%+ cobertura)
