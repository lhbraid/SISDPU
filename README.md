# Análise de Dados SISDPU - Dashboard Interativo

Este projeto consiste em um dashboard web interativo para análise de dados do SISDPU, desenvolvido com Dash/Plotly e Flask. Ele oferece múltiplas formas de carregar dados, filtros interativos e visualizações dinâmicas.

## Funcionalidades Principais

*   **Múltiplas Fontes de Dados Independentes:**
    *   **Planilha Local (GitHub):** Carrega dados de uma planilha Excel (`tratado_filtrado.xlsx`) incluída no repositório.
    *   **API (PostgreSQL):** Busca dados de um banco de dados PostgreSQL através de uma API RESTful.
    *   **Upload de Planilha:** Permite ao usuário fazer upload de uma nova planilha Excel, atualizando os gráficos e filtros dinamicamente.
*   **Cabeçalho Informativo:** Exibe o título "Análise de Dados SISDPU" e a data da última atualização dos dados.
*   **Filtros de Data Avançados:**
    *   Seleção de um único dia.
    *   Seleção de um intervalo de datas customizado.
    *   Incide sobre a coluna "Data de Abertura do PAJ".
*   **Filtros Categóricos com Múltipla Seleção:**
    *   Ofício
    *   Tipo de Pretensão
    *   Matéria
    *   Usuário
*   **Gráficos Interativos (Plotly):**
    *   Série temporal do volume de PAJs por data.
    *   Gráficos de barras para distribuições por Ofício, Tipo de Pretensão, Matéria e Usuário (com percentuais e quantidades).
*   **Identidade Visual:** Utiliza as cores do logo da DPU.
*   **API RESTful (Flask):** Fornece endpoints para acesso aos dados armazenados no PostgreSQL.
*   **Scripts Auxiliares:** Para criação de tabelas e população do banco de dados.
*   **Deploy Automático:** Configurado para deploy no Render via `render.yaml` e GitHub Actions (push na `main` branch).

## Estrutura do Projeto

```
/home/ubuntu/sisdpu_dashboard/
├── .github/
│   └── workflows/
│       └── main.yml         # Workflow do GitHub Actions para Render
├── api/
│   ├── main.py            # Código da API Flask (endpoints, modelo DB)
│   ├── create_tables.py   # Script para criar tabelas no DB
│   └── populate_db.py     # Script para popular o DB com dados da planilha
├── assets/
│   └── logo-dpu.png       # Logo da DPU usado no dashboard
├── data/
│   └── tratado_filtrado.xlsx # Planilha Excel com dados tratados (default)
├── src/
│   └── app.py             # Código principal do dashboard Dash/Plotly
├── Procfile                 # Comandos para iniciar os serviços no Render
├── README.md                # Este arquivo
├── render.yaml              # Configuração de Blueprint do Render
├── requirements.txt         # Dependências Python do projeto
└── todo.md                  # Checklist de desenvolvimento (interno)
```

## Tecnologias Utilizadas

*   **Python 3.11**
*   **Dash e Plotly:** Para a criação do dashboard interativo.
*   **Dash Bootstrap Components:** Para estilização e layout responsivo.
*   **Pandas:** Para manipulação e análise de dados.
*   **Flask:** Para a criação da API RESTful.
*   **Flask-SQLAlchemy e psycopg2-binary:** Para interação com o banco de dados PostgreSQL.
*   **Flask-CORS:** Para habilitar Cross-Origin Resource Sharing na API.
*   **Gunicorn:** Como servidor WSGI para produção.
*   **PostgreSQL:** Banco de dados relacional.
*   **GitHub Actions:** Para integração contínua e acionamento de deploy.
*   **Render:** Plataforma PaaS para deploy da aplicação e do banco de dados.

## Configuração e Instalação (Local)

Siga os passos abaixo para configurar e rodar o projeto localmente.

### Pré-requisitos

*   Python 3.11 ou superior instalado.
*   pip (gerenciador de pacotes Python).
*   PostgreSQL instalado e rodando.
*   Git (opcional, para clonar o repositório).

### 1. Clonar o Repositório (Opcional)

Se você recebeu o projeto como um arquivo zip, descompacte-o. Se for clonar:
```bash
git clone <URL_DO_REPOSITORIO>
cd sisdpu_dashboard
```

### 2. Criar e Ativar um Ambiente Virtual

É altamente recomendado usar um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate    # No Windows
```

### 3. Instalar Dependências

Com o ambiente virtual ativado, instale as dependências listadas no `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configurar o Banco de Dados PostgreSQL (Local)

*   **Crie um banco de dados:** Use o `psql` ou uma ferramenta gráfica (como pgAdmin) para criar um novo banco de dados. Por exemplo, `sisdpu_db`.
    ```sql
    CREATE DATABASE sisdpu_db;
    ```
*   **Crie um usuário (opcional, mas recomendado):** Crie um usuário com permissões para este banco.
    ```sql
    CREATE USER sisdpu_user WITH PASSWORD 'sua_senha_segura';
    GRANT ALL PRIVILEGES ON DATABASE sisdpu_db TO sisdpu_user;
    ```
*   **Configure as Variáveis de Ambiente para a API:**
    A API (`api/main.py`) usa variáveis de ambiente para se conectar ao banco. Defina-as no seu terminal antes de rodar os scripts da API ou a própria API. Para desenvolvimento local, se você não definir, os valores padrão no código serão usados (`postgres`, `password`, `localhost`, `5432`, `sisdpu_db`).

    Exemplo no Linux/macOS:
    ```bash
    export DB_USERNAME="sisdpu_user"
    export DB_PASSWORD="sua_senha_segura"
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export DB_NAME="sisdpu_db"
    ```
    No Windows (PowerShell):
    ```powershell
    $env:DB_USERNAME = "sisdpu_user"
    $env:DB_PASSWORD = "sua_senha_segura"
    # ... e assim por diante
    ```

### 5. Criar Tabelas no Banco de Dados

Execute o script `create_tables.py` para criar a tabela `paj_data` no seu banco de dados PostgreSQL. Certifique-se de que as variáveis de ambiente do banco estão configuradas ou que os padrões no script correspondem à sua configuração local.
```bash
python api/create_tables.py
```

### 6. Popular o Banco de Dados

Execute o script `populate_db.py` para carregar os dados da planilha `data/tratado_filtrado.xlsx` para a tabela `paj_data`.
```bash
python api/populate_db.py
```

## Rodando Localmente

### 1. Rodar a API Flask

Navegue até a pasta raiz do projeto e execute:
```bash
python api/main.py
```
A API estará rodando em `http://0.0.0.0:5001` por padrão.

### 2. Rodar o Dashboard Dash

Em um novo terminal, navegue até a pasta raiz do projeto e execute:
```bash
python src/app.py
```
O dashboard estará acessível em `http://127.0.0.1:8050/` (ou `http://0.0.0.0:8050/`).

Agora você pode abrir o dashboard no seu navegador e interagir com ele, selecionando a fonte de dados "API (PostgreSQL)" para testar a conexão com o banco local.

## Variáveis de Ambiente

As seguintes variáveis de ambiente são usadas pela aplicação, especialmente para o deploy no Render:

*   **Para a API (`api/main.py`):**
    *   `DB_USERNAME`: Usuário do PostgreSQL.
    *   `DB_PASSWORD`: Senha do usuário do PostgreSQL.
    *   `DB_HOST`: Host do servidor PostgreSQL.
    *   `DB_PORT`: Porta do servidor PostgreSQL.
    *   `DB_NAME`: Nome do banco de dados PostgreSQL.
    *   `FLASK_APP` (geralmente `api.main:app` para produção).
    *   `FLASK_ENV` (geralmente `production` para produção).
    *   `PORT_API` (usado pelo Render para injetar a porta da API, configurado no `render.yaml` e `Procfile`).

*   **Para o Dashboard (`src/app.py`):**
    *   `PORT` (usado pelo Render para injetar a porta do serviço web principal).

No Render, a maioria das variáveis de banco de dados (`DB_*`) são injetadas automaticamente quando você vincula o serviço da API ao serviço de banco de dados do Render, conforme definido no `render.yaml`.

## Deploy no Render

Este projeto está configurado para deploy fácil no Render usando o arquivo `render.yaml` (Blueprint).

### 1. Pré-requisitos para Deploy no Render

*   Conta no GitHub com o projeto versionado.
*   Conta no Render.

### 2. Configuração no Render

*   **Crie um novo Blueprint no Render:** Vá para o seu dashboard do Render, clique em "Blueprints" e depois em "New Blueprint".
*   **Conecte seu repositório GitHub:** Autorize o Render a acessar seu repositório.
*   **Selecione o repositório e a branch `main`.**
*   **Render irá detectar o `render.yaml`:** Ele usará este arquivo para configurar os serviços (dashboard web, API web e banco de dados PostgreSQL).
*   **Variáveis de Ambiente (Secrets do GitHub - Opcional para Trigger Manual):**
    *   Se você quisesse usar o trigger manual de deploy via API do Render no `main.yml` (atualmente comentado), você precisaria configurar os seguintes secrets no seu repositório GitHub (`Settings > Secrets and variables > Actions`):
        *   `RENDER_API_KEY`: Sua chave de API do Render (encontrada nas configurações da sua conta no Render).
        *   `RENDER_DASHBOARD_SERVICE_ID`: O ID do serviço do dashboard no Render.
        *   `RENDER_API_SERVICE_ID`: O ID do serviço da API no Render.
    *   **Nota:** Com o `render.yaml`, o deploy é geralmente automático no push para a branch conectada, então o trigger manual via GitHub Actions pode não ser necessário.

### 3. Processo de Deploy

*   **Primeiro Deploy:** Após criar o Blueprint, o Render iniciará o processo de build e deploy. Isso inclui:
    1.  Provisionar o banco de dados PostgreSQL.
    2.  Construir o serviço da API: instalar dependências, rodar `api/create_tables.py` e `api/populate_db.py` (conforme `buildCommand` no `render.yaml`).
    3.  Iniciar o serviço da API usando Gunicorn.
    4.  Construir o serviço do Dashboard: instalar dependências.
    5.  Iniciar o serviço do Dashboard usando Gunicorn.
*   **Atualizações:** Qualquer `git push` para a branch `main` (ou a branch configurada no Render) irá automaticamente acionar um novo build e deploy dos serviços afetados.

### 4. Acessando a Aplicação

Após o deploy bem-sucedido, o Render fornecerá URLs públicas para o seu dashboard e API.

## GitHub Actions

O arquivo `.github/workflows/main.yml` está configurado para rodar em pushes para a branch `main`. Atualmente, ele serve mais como um placeholder, pois o `render.yaml` e a integração direta do Render com o GitHub cuidam do deploy automático.

Se você precisar de etapas de CI mais complexas (testes, linting) antes do deploy, você pode adicioná-las a este workflow. O deploy manual via API do Render (comentado no `main.yml`) pode ser usado se você precisar de controle programático sobre quando o deploy é acionado após as etapas de CI.

## Scripts Auxiliares

*   **`api/create_tables.py`:**
    *   Uso: `python api/create_tables.py`
    *   Função: Cria a tabela `paj_data` no banco de dados PostgreSQL configurado, se ela ainda não existir. Requer que as variáveis de ambiente do banco estejam setadas ou que os padrões no script sejam válidos para sua configuração.
*   **`api/populate_db.py`:**
    *   Uso: `python api/populate_db.py`
    *   Função: Lê os dados da planilha `data/tratado_filtrado.xlsx` e os insere na tabela `paj_data` do banco. Por padrão, ele limpa a tabela antes de inserir novos dados para evitar duplicatas. Requer as mesmas configurações de banco que o `create_tables.py`.

## Possíveis Problemas e Soluções (Troubleshooting)

*   **Erro de conexão com o banco de dados local:**
    *   Verifique se o serviço PostgreSQL está rodando.
    *   Confirme se as variáveis de ambiente `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` estão corretas e exportadas na sessão do terminal onde você está rodando os scripts da API ou a própria API.
    *   Verifique as configurações de autenticação do PostgreSQL (ex: `pg_hba.conf`).
*   **Dashboard não carrega dados da API:**
    *   Verifique se a API Flask está rodando e acessível na porta correta (padrão 5001).
    *   Verifique o console do navegador e o terminal da API para mensagens de erro.
    *   Certifique-se de que o CORS está habilitado na API (já está por padrão com `Flask-CORS`).
*   **Problemas de data no dashboard ou API:**
    *   O código tenta lidar com formatos de data comuns (DD/MM/YYYY e ISO YYYY-MM-DD). Se sua planilha tiver um formato diferente, pode ser necessário ajustar o parsing de data nos scripts (`populate_db.py`) e no callback do dashboard (`src/app.py`).
*   **Deploy no Render falha:**
    *   Verifique os logs de build e deploy no dashboard do Render para identificar o erro.
    *   Confirme se o `requirements.txt` está completo e todas as dependências são compatíveis com o ambiente Linux do Render.
    *   Verifique se o `Procfile` e o `render.yaml` estão configurados corretamente para os comandos de build e start.
    *   Certifique-se de que as variáveis de ambiente no Render estão configuradas corretamente, especialmente se você não estiver usando o `fromDatabase` para as credenciais do banco.

Para qualquer dúvida ou problema, consulte os logs da aplicação e do servidor.

