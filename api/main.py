# api/main.py
import os
import sys
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd

# Adicionar o diretório raiz do projeto ao sys.path para importações corretas
# Isso é importante para quando o app Flask for executado de dentro do diretório api/
# ou quando for importado por outros módulos.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

app = Flask(__name__)
CORS(app) # Habilitar CORS para todas as rotas

# Configuração do Banco de Dados PostgreSQL
# Use variáveis de ambiente para segurança e flexibilidade
DB_USERNAME = os.getenv("DB_USERNAME", "postgres") # Default para desenvolvimento local
DB_PASSWORD = os.getenv("DB_PASSWORD", "password") # Default para desenvolvimento local
DB_HOST = os.getenv("DB_HOST", "localhost")       # Default para desenvolvimento local
DB_PORT = os.getenv("DB_PORT", "5432")          # Default para desenvolvimento local
DB_NAME = os.getenv("DB_NAME", "sisdpu_db")      # Default para desenvolvimento local

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo da Tabela de Dados (equivalente a tratado_filtrado.xlsx)
class PajData(db.Model):
    __tablename__ = 'paj_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paj_numero = db.Column(db.String(255), name='PAJ') # Nome da coluna no Excel
    unidade = db.Column(db.String(255), name='Unidade')
    assistido = db.Column(db.Text, name='Assistido')
    oficio = db.Column(db.String(255), name='Oficio')
    pretensao = db.Column(db.Text, name='Pretensão')
    tipo_pretensao = db.Column(db.String(255), name='Tipo de Pretensão')
    data_abertura_paj = db.Column(db.Date, name='Data de Abertura do PAJ')
    materia = db.Column(db.String(255), name='Materia')
    atribuicao = db.Column(db.String(255), name='Atribuição')
    defensor = db.Column(db.String(255), name='DEFENSOR')
    usuario_instaurou = db.Column(db.String(255), name='Usuário que instaurou o paj')
    usuario = db.Column(db.String(255), name='Usuário')

    def to_dict(self):
        return {
            'PAJ': self.paj_numero,
            'Unidade': self.unidade,
            'Assistido': self.assistido,
            'Oficio': self.oficio,
            'Pretensão': self.pretensao,
            'Tipo de Pretensão': self.tipo_pretensao,
            'Data de Abertura do PAJ': self.data_abertura_paj.isoformat() if self.data_abertura_paj else None,
            'Materia': self.materia,
            'Atribuição': self.atribuicao,
            'DEFENSOR': self.defensor,
            'Usuário que instaurou o paj': self.usuario_instaurou,
            'Usuário': self.usuario
        }

@app.route('/api/data', methods=['GET'])
def get_all_data():
    try:
        data = PajData.query.all()
        return jsonify([d.to_dict() for d in data])
    except Exception as e:
        # Log do erro no servidor
        app.logger.error(f"Erro ao buscar dados da API: {e}")
        # Retornar uma resposta de erro mais genérica para o cliente
        return jsonify({"error": "Erro ao processar a solicitação de dados"}), 500

# Rota de health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    # Cria as tabelas se não existirem (para desenvolvimento local)
    # Em produção, as migrações ou scripts de setup devem cuidar disso.
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001) # Rodar em porta diferente do Dash app

