# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Idioma de Desenvolvimento

**IMPORTANTE**: Sempre utilize português do Brasil para conversação e comentários no código. Todas as interações, documentação e comentários devem ser em português brasileiro.

## Visão Geral do Projeto

Este é um aplicativo dashboard de poker baseado em Streamlit chamado "BPD - Sistema de Gestão" que gerencia dados de jogos de poker, autenticação de usuários e métricas financeiras. O aplicativo fornece diferentes visualizações para administradores e jogadores, com capacidades abrangentes de filtragem e relatórios.

## Comandos de Desenvolvimento

### Iniciar a Aplicação
```bash
# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Executar a aplicação Streamlit
streamlit run app.py
# Ou especificamente: venv\Scripts\streamlit.exe run app.py
```

### Configuração do Banco de Dados
```bash
# Configurar tabelas do banco de dados
python setup_database.py

# Verificar conexão com o banco
python test_db_connection.py

# Atualizar tabela de usuários
python update_users_table.py
```

### Testes
```bash
# Executar testes de lógica de data
python test_date_logic.py

# Executar testes de conexão com banco
python test_db_connection.py
```

## Arquitetura

### Estrutura Principal da Aplicação

- **app.py**: Ponto de entrada principal com interface Streamlit, fluxo de autenticação e orquestração do dashboard
- **database.py**: Gerenciamento de conexão com banco de dados e funções de carregamento de dados usando conector MySQL
- **auth.py**: Lógica de autenticação e autorização de usuários
- **utils.py**: Funções utilitárias incluindo integração com Google Analytics

### Arquitetura de Componentes

A aplicação segue uma arquitetura modular baseada em componentes:

- **table_component.py**: Exibe tabelas de dados com capacidades de filtragem e ordenação
- **filter_component.py**: Controles de filtragem avançada para análise de dados
- **metric_cards_component.py**: Exibição de métricas financeiras com suporte a moedas
- **config_page.py**: Gerenciamento de configurações e ajustes do usuário

### Schema do Banco de Dados

A aplicação usa um banco de dados MySQL com as seguintes tabelas principais:
- `bpd`: Tabela principal de dados de poker com estatísticas de jogadores, ganhos, taxas e métricas de jogo
- `users`: Tabela de autenticação de usuários com username, senha e informações de função

### Sistema de Autenticação

- **Acesso baseado em função**: Funções Admin e Player com diferentes permissões
- **Geração de senha**: Geração automática de senha para jogadores usando algoritmo baseado em nome
- **Gerenciamento de sessão**: Estado de sessão Streamlit para autenticação e preferências do usuário

### Fluxo de Dados

1. Autenticação de usuário através de `auth.py`
2. Carregamento de dados do MySQL via `database.py` com filtragem específica do usuário
3. Renderização de componentes através de módulos especializados
4. Gerenciamento de estado via estado de sessão Streamlit

## Recursos Principais

### Gerenciamento de Usuários
- Usuários admin podem ver todos os dados e gerenciar usuários
- Usuários jogadores veem apenas seus próprios dados
- Geração automática de senha para novos jogadores

### Filtragem de Dados
- Filtragem por intervalo de datas (hoje, semana atual, última semana, últimos 30 dias, tudo)
- Filtragem avançada através de componentes de filtro
- Seleção de moeda (Real e Dólar)

### Exibição de Métricas
- Cálculo em tempo real de métricas de poker (mãos, ganhos, taxas, rakeback)
- Suporte a múltiplas moedas
- Cartões de métricas responsivos com estilo moderno

## Configuração

### Configuração do Banco de Dados
Credenciais do banco são armazenadas em `secrets.toml` (não no repositório):
```toml
[mysql]
host = "seu-host"
user = "seu-usuario"
password = "sua-senha"
database = "seu-banco"
port = 3306
```

### Dependências
Principais dependências do `requirements.txt`:
- streamlit: Framework de aplicação web
- mysql-connector-python: Conectividade com banco de dados
- pandas: Manipulação de dados
- streamlit-shadcn-ui: Componentes de UI modernos
- streamlit-option-menu: Componentes de navegação

## Diretrizes de Desenvolvimento

### Consultas ao Banco de Dados
- Use consultas parametrizadas para prevenir injeção SQL
- Implemente tratamento adequado de erros para conexões com banco
- Faça cache de dados apropriadamente mas esteja atento aos requisitos de tempo real

### Componentes de UI
- Siga padrões de componentes existentes no código
- Use estilização consistente com o framework CSS existente
- Implemente estados de carregamento e tratamento de erros adequados

### Autenticação
- Nunca armazene senhas em texto plano
- Implemente gerenciamento adequado de sessão
- Valide permissões de usuário antes do acesso aos dados

### Testes
- Teste conexões com banco antes do deploy
- Valide lógica de datas com arquivos de teste existentes
- Teste fluxos de autenticação de usuário