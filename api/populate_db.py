# api/populate_db.py
import os
import sys
import pandas as pd
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Adicionar o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from api.main import db, app, PajData # Importar db, app e o modelo PajData

# Caminho para a planilha de dados tratados
DATA_FILE_PATH = os.path.join(project_root, "data", "tratado_filtrado.xlsx")

def populate_database():
    """Popula o banco de dados com os dados da planilha Excel."""
    with app.app_context(): # Contexto da aplicação Flask é necessário para SQLAlchemy
        print(f"Lendo dados de {DATA_FILE_PATH}...")
        try:
            df = pd.read_excel(DATA_FILE_PATH)
        except FileNotFoundError:
            print(f"Erro: Arquivo {DATA_FILE_PATH} não encontrado.")
            return
        except Exception as e:
            print(f"Erro ao ler o arquivo Excel: {e}")
            return

        print(f"{len(df)} registros encontrados na planilha.")
        
        # Renomear colunas do DataFrame para corresponder aos nomes dos atributos do modelo PajData
        # Isso é crucial se os nomes das colunas no Excel não forem exatamente iguais aos nomes no modelo
        # ou se você usou o argumento `name` no db.Column.
        # O modelo PajData já usa o argumento `name` para mapear para os nomes das colunas do Excel.

        # Limpar a tabela antes de popular para evitar duplicatas se o script for rodado múltiplas vezes
        # Comente esta linha se você quiser adicionar dados sem limpar os existentes
        try:
            print(f"Limpando dados existentes da tabela {PajData.__tablename__}...")
            db.session.query(PajData).delete()
            db.session.commit()
            print("Dados existentes removidos.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao limpar a tabela: {e}")
            return

        print(f"Inserindo dados na tabela {PajData.__tablename__}...")
        count_inserted = 0
        count_skipped = 0
        for index, row in df.iterrows():
            try:
                # Converter a data para o formato correto, se necessário
                data_abertura_str = row.get("Data de Abertura do PAJ")
                data_abertura_obj = None
                if pd.notna(data_abertura_str):
                    if isinstance(data_abertura_str, datetime):
                        data_abertura_obj = data_abertura_str.date()
                    else:
                        try:
                            # Tenta converter de string DD/MM/YYYY
                            data_abertura_obj = datetime.strptime(str(data_abertura_str).split(' ')[0], '%d/%m/%Y').date()
                        except ValueError:
                            try:
                                # Tenta converter de string YYYY-MM-DD (formato ISO que o Pandas pode usar ao ler)
                                data_abertura_obj = datetime.strptime(str(data_abertura_str).split(' ')[0], '%Y-%m-%d').date()
                            except ValueError:
                                print(f"Formato de data inválido para '{data_abertura_str}' na linha {index + 2}. Pulando registro.")
                                count_skipped += 1
                                continue
                
                paj_entry = PajData(
                    paj_numero=row.get("PAJ"),
                    unidade=row.get("Unidade"),
                    assistido=row.get("Assistido"),
                    oficio=row.get("Oficio"),
                    pretensao=row.get("Pretensão"),
                    tipo_pretensao=row.get("Tipo de Pretensão"),
                    data_abertura_paj=data_abertura_obj,
                    materia=row.get("Materia"),
                    atribuicao=row.get("Atribuição"),
                    defensor=row.get("DEFENSOR"),
                    usuario_instaurou=row.get("Usuário que instaurou o paj"),
                    usuario=row.get("Usuário")
                )
                db.session.add(paj_entry)
                count_inserted += 1
            except IntegrityError as e:
                db.session.rollback()
                print(f"Erro de integridade ao inserir linha {index + 2} (PAJ: {row.get('PAJ')}): {e}. Pulando registro.")
                count_skipped += 1
            except Exception as e:
                db.session.rollback()
                print(f"Erro inesperado ao processar linha {index + 2} (PAJ: {row.get('PAJ')}): {e}. Pulando registro.")
                count_skipped += 1
            
            # Commit em lotes para melhor desempenho
            if (index + 1) % 100 == 0:
                try:
                    db.session.commit()
                    print(f"{count_inserted} registros inseridos até agora...")
                except Exception as e:
                    db.session.rollback()
                    print(f"Erro ao commitar lote: {e}")
        
        # Commit final para quaisquer registros restantes
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao commitar registros finais: {e}")

        print(f"População do banco de dados concluída.")
        print(f"Total de registros inseridos: {count_inserted}")
        print(f"Total de registros pulados devido a erros: {count_skipped}")

if __name__ == '__main__':
    populate_database()

