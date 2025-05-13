# api/create_tables.py
import os
import sys
from sqlalchemy import create_engine, text

# Adicionar o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from api.main import db, app # Importar db e app de api.main

def create_db_tables():
    """Cria as tabelas no banco de dados se não existirem."""
    with app.app_context(): # Precisamos do contexto da aplicação Flask para SQLAlchemy
        print("Conectando ao banco de dados...")
        try:
            # Verificar se a tabela já existe
            inspector = db.inspect(db.engine)
            if not inspector.has_table(PajData.__tablename__):
                print(f"Criando tabela {PajData.__tablename__}...")
                db.create_all() # Cria todas as tabelas definidas nos modelos SQLAlchemy
                print(f"Tabela {PajData.__tablename__} criada com sucesso.")
            else:
                print(f"Tabela {PajData.__tablename__} já existe.")
        except Exception as e:
            print(f"Erro ao conectar ou criar tabelas: {e}")
            print("Verifique as configurações do banco de dados (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) e se o PostgreSQL está rodando.")

if __name__ == '__main__':
    # Importar o modelo aqui para garantir que seja registrado antes de create_all
    from api.main import PajData
    create_db_tables()

