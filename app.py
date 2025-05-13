import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import plotly.express as px
from datetime import datetime

# Inicializa o aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Análise de Dados SISDPU"

# Layout do aplicativo
app.layout = dbc.Container(
    [
        # Cabeçalho
        dbc.Row(
            [
                dbc.Col(html.H1("Análise de Dados SISDPU"), width=9),
                dbc.Col(html.Div(id="last-update-time", children=f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"), width=3, style={"textAlign": "right", "paddingTop": "20px"})
            ],
            align="center",
            className="mb-4"
        ),
        # Linha para o logo e controles de fonte de dados
        dbc.Row(
            [
                dbc.Col(html.Img(src=app.get_asset_url("logo-dpu.png"), height="60px"), width=2),
                dbc.Col(
                    [
                        dcc.RadioItems(
                            id='data-source-selector',
                            options=[
                                {'label': 'Planilha Local (GitHub)', 'value': 'local_excel'},
                                {'label': 'API (PostgreSQL)', 'value': 'api'},
                                {'label': 'Upload de Planilha', 'value': 'upload'}
                            ],
                            value='local_excel', # Valor padrão
                            labelStyle={'display': 'inline-block', 'margin-right': '20px'}
                        ),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Arraste e solte ou ', 
                                html.A('selecione uma planilha Excel')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0'
                            },
                            # Permite apenas um arquivo por vez
                            multiple=False,
                            # Aceita apenas arquivos .xlsx
                            accept=".xlsx"
                        )
                    ], width=10
                )
            ], className="mb-4", align="center"
        ),
        
        # Filtros
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Filtros de Data"),
                        dcc.DatePickerRange(
                            id='date-picker-range',
                            display_format='DD/MM/YYYY',
                            min_date_allowed=datetime(2000, 1, 1),
                            max_date_allowed=datetime.now(),
                            initial_visible_month=datetime.now(),
                            # start_date=df_tratado['Data de Abertura do PAJ'].min() if not df_tratado.empty else None, # Definir após carregar dados
                            # end_date=df_tratado['Data de Abertura do PAJ'].max() if not df_tratado.empty else None, # Definir após carregar dados
                            className="mb-2"
                        ),
                    ], md=6
                ),
                dbc.Col(
                    [
                        html.H5("Filtros Categóricos"),
                        dcc.Dropdown(id='oficio-filter', multi=True, placeholder="Selecionar Ofício(s)", className="mb-2"),
                        dcc.Dropdown(id='pretensao-filter', multi=True, placeholder="Selecionar Tipo(s) de Pretensão", className="mb-2"),
                        dcc.Dropdown(id='materia-filter', multi=True, placeholder="Selecionar Matéria(s)", className="mb-2"),
                        dcc.Dropdown(id='usuario-filter', multi=True, placeholder="Selecionar Usuário(s)", className="mb-2"),
                    ], md=6
                )
            ], className="mb-4"
        ),

        # Gráficos
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='time-series-graph'), md=12, className="mb-4"),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='oficio-dist-graph'), md=6, className="mb-4"),
                dbc.Col(dcc.Graph(id='pretensao-dist-graph'), md=6, className="mb-4"),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='materia-dist-graph'), md=6, className="mb-4"),
                dbc.Col(dcc.Graph(id='usuario-dist-graph'), md=6, className="mb-4"),
            ]
        ),
        # Armazenamento de dados intermediários
        dcc.Store(id='intermediate-data-store')
    ],
    fluid=True
)

# Callbacks serão adicionados aqui

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')



import io
import base64
from dash.dependencies import Input, Output, State

# --- Cores DPU (extraídas anteriormente) ---
DPU_COLORS = {
    "primary_green": "#4d9529",
    "primary_teal": "#00898f",
    "dark_gray": "#373737",
    "light_gray": "#f0f0f0", # Adicionando uma cor clara para fundos ou elementos secundários
    "white": "#ffffff"
}

# --- Funções Auxiliares ---
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'xlsx' in filename:
            # Assume que o usuário fez upload de um arquivo Excel
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return html.Div(['Tipo de arquivo não suportado. Por favor, use .xlsx'])
    except Exception as e:
        print(e)
        return html.Div(['Ocorreu um erro ao processar este arquivo.'])
    return df

def load_local_excel_data():
    try:
        df = pd.read_excel("data/tratado_filtrado.xlsx")
        # Assegurar que a coluna de data está no formato correto e é datetime
        if 'Data de Abertura do PAJ' in df.columns:
            df['Data de Abertura do PAJ'] = pd.to_datetime(df['Data de Abertura do PAJ'], errors='coerce', dayfirst=True)
        return df
    except Exception as e:
        print(f"Erro ao carregar planilha local: {e}")
        return pd.DataFrame() # Retorna DataFrame vazio em caso de erro

# --- Callbacks ---

# Callback para carregar dados com base na seleção da fonte ou upload
@app.callback(
    Output('intermediate-data-store', 'data'),
    Output('last-update-time', 'children'),
    Input('data-source-selector', 'value'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_data_store(selected_source, uploaded_contents, uploaded_filename):
    df = pd.DataFrame()
    trigger_id = dash.callback_context.triggered_id
    now_time_str = f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    if trigger_id == 'upload-data' and uploaded_contents is not None:
        df = parse_contents(uploaded_contents, uploaded_filename)
        if isinstance(df, html.Div): # Erro no parse
            print("Erro no parse do upload")
            # Mantém os dados anteriores ou carrega o local como fallback?
            # Por enquanto, vamos carregar o local se o upload falhar e a fonte selecionada for upload
            if selected_source == 'upload':
                 df = load_local_excel_data()
            # Se não, respeita a seleção atual
            elif selected_source == 'local_excel':
                 df = load_local_excel_data()
            # API ainda não implementada
            # else: df = pd.DataFrame()
        else:
             if 'Data de Abertura do PAJ' in df.columns:
                df['Data de Abertura do PAJ'] = pd.to_datetime(df['Data de Abertura do PAJ'], errors='coerce') # Tenta formato padrão primeiro
                # Se falhar, tenta com dayfirst=True (comum no Brasil)
                if df['Data de Abertura do PAJ'].isnull().all():
                    df['Data de Abertura do PAJ'] = pd.to_datetime(parse_contents(uploaded_contents, uploaded_filename)['Data de Abertura do PAJ'], errors='coerce', dayfirst=True)

    elif selected_source == 'local_excel':
        df = load_local_excel_data()
    elif selected_source == 'api':
        # Lógica para buscar dados da API (será implementada depois)
        # Por enquanto, retorna DataFrame vazio ou dados locais como placeholder
        print("Fonte API selecionada, mas ainda não implementada. Carregando dados locais.")
        df = load_local_excel_data() # Placeholder
    else: # Caso inicial ou upload sem arquivo ainda
        df = load_local_excel_data()

    return df.to_json(date_format='iso', orient='split'), now_time_str

# Callback para atualizar os filtros com base nos dados carregados
@app.callback(
    Output('date-picker-range', 'min_date_allowed'),
    Output('date-picker-range', 'max_date_allowed'),
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Output('date-picker-range', 'initial_visible_month'),
    Output('oficio-filter', 'options'),
    Output('pretensao-filter', 'options'),
    Output('materia-filter', 'options'),
    Output('usuario-filter', 'options'),
    Input('intermediate-data-store', 'data')
)
def update_filters(jsonified_cleaned_data):
    if not jsonified_cleaned_data:
        # Valores padrão se não houver dados
        default_date = datetime.now().date()
        min_date = datetime(2000, 1, 1).date()
        empty_options = []
        return min_date, default_date, min_date, default_date, default_date, empty_options, empty_options, empty_options, empty_options

    df = pd.read_json(jsonified_cleaned_data, orient='split')
    if df.empty or 'Data de Abertura do PAJ' not in df.columns:
        default_date = datetime.now().date()
        min_date = datetime(2000, 1, 1).date()
        empty_options = []
        return min_date, default_date, min_date, default_date, default_date, empty_options, empty_options, empty_options, empty_options

    # Converte a coluna de data para datetime se ainda não for
    df['Data de Abertura do PAJ'] = pd.to_datetime(df['Data de Abertura do PAJ'], errors='coerce')
    df = df.dropna(subset=['Data de Abertura do PAJ']) # Remove linhas onde a data não pôde ser convertida

    if df.empty:
        default_date = datetime.now().date()
        min_date = datetime(2000, 1, 1).date()
        empty_options = []
        return min_date, default_date, min_date, default_date, default_date, empty_options, empty_options, empty_options, empty_options

    min_date_allowed = df['Data de Abertura do PAJ'].min().date()
    max_date_allowed = df['Data de Abertura do PAJ'].max().date()
    start_date = min_date_allowed
    end_date = max_date_allowed
    initial_visible_month = start_date

    oficio_options = [{'label': i, 'value': i} for i in sorted(df['Oficio'].astype(str).unique())]
    pretensao_options = [{'label': i, 'value': i} for i in sorted(df['Tipo de Pretensão'].astype(str).unique())]
    materia_options = [{'label': i, 'value': i} for i in sorted(df['Materia'].astype(str).unique())]
    usuario_options = [{'label': i, 'value': i} for i in sorted(df['Usuário'].astype(str).unique())]

    return min_date_allowed, max_date_allowed, start_date, end_date, initial_visible_month, oficio_options, pretensao_options, materia_options, usuario_options

# Callback para atualizar os gráficos
@app.callback(
    Output('time-series-graph', 'figure'),
    Output('oficio-dist-graph', 'figure'),
    Output('pretensao-dist-graph', 'figure'),
    Output('materia-dist-graph', 'figure'),
    Output('usuario-dist-graph', 'figure'),
    Input('intermediate-data-store', 'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('oficio-filter', 'value'),
    Input('pretensao-filter', 'value'),
    Input('materia-filter', 'value'),
    Input('usuario-filter', 'value')
)
def update_graphs(jsonified_cleaned_data, start_date, end_date, oficio_selected, pretensao_selected, materia_selected, usuario_selected):
    if not jsonified_cleaned_data:
        # Retorna figuras vazias se não houver dados
        empty_fig = {'data': [], 'layout': {'title': 'Sem dados para exibir'}}
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    dff = pd.read_json(jsonified_cleaned_data, orient='split')
    if dff.empty:
        empty_fig = {'data': [], 'layout': {'title': 'Sem dados para exibir'}}
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # Assegurar que a coluna de data é datetime
    dff['Data de Abertura do PAJ'] = pd.to_datetime(dff['Data de Abertura do PAJ'], errors='coerce')
    dff = dff.dropna(subset=['Data de Abertura do PAJ'])

    # Filtrar por data
    if start_date and end_date:
        dff = dff[(dff['Data de Abertura do PAJ'] >= pd.to_datetime(start_date)) & (dff['Data de Abertura do PAJ'] <= pd.to_datetime(end_date))]

    # Filtrar por campos categóricos
    if oficio_selected:
        dff = dff[dff['Oficio'].isin(oficio_selected)]
    if pretensao_selected:
        dff = dff[dff['Tipo de Pretensão'].isin(pretensao_selected)]
    if materia_selected:
        dff = dff[dff['Materia'].isin(materia_selected)]
    if usuario_selected:
        dff = dff[dff['Usuário'].isin(usuario_selected)]

    if dff.empty:
        empty_fig = {'data': [], 'layout': {'title': 'Nenhum dado corresponde aos filtros selecionados'}}
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # Gráfico de Séries Temporais (Volume de PAJs por data)
    paj_counts_by_date = dff.groupby(dff['Data de Abertura do PAJ'].dt.date).size().reset_index(name='count')
    time_series_fig = px.line(paj_counts_by_date, x='Data de Abertura do PAJ', y='count', title='Volume de PAJs por Data de Abertura',
                              color_discrete_sequence=[DPU_COLORS["primary_teal"]])
    time_series_fig.update_layout(xaxis_title="Data de Abertura", yaxis_title="Número de PAJs")

    # Gráficos de Distribuição (Barras ou Roscas)
    # Ofício
    oficio_counts = dff['Oficio'].value_counts().reset_index()
    oficio_counts.columns = ['Oficio', 'count']
    oficio_counts['percentage'] = (oficio_counts['count'] / oficio_counts['count'].sum()) * 100
    oficio_fig = px.bar(oficio_counts, x='Oficio', y='count', text_auto=True, title='Distribuição por Ofício',
                        labels={'count': 'Quantidade'}, color_discrete_sequence=[DPU_COLORS["primary_green"]])
    oficio_fig.update_traces(texttemplate='%{y} (%{customdata[0]:.1f}%)', customdata=oficio_counts[['percentage']])
    oficio_fig.update_layout(xaxis_title="Ofício", yaxis_title="Quantidade")

    # Tipo de Pretensão
    pretensao_counts = dff['Tipo de Pretensão'].value_counts().reset_index()
    pretensao_counts.columns = ['Tipo de Pretensão', 'count']
    pretensao_counts['percentage'] = (pretensao_counts['count'] / pretensao_counts['count'].sum()) * 100
    pretensao_fig = px.bar(pretensao_counts, x='Tipo de Pretensão', y='count', text_auto=True, title='Distribuição por Tipo de Pretensão',
                           labels={'count': 'Quantidade'}, color_discrete_sequence=[DPU_COLORS["primary_teal"]])
    pretensao_fig.update_traces(texttemplate='%{y} (%{customdata[0]:.1f}%)', customdata=pretensao_counts[['percentage']])
    pretensao_fig.update_layout(xaxis_title="Tipo de Pretensão", yaxis_title="Quantidade", xaxis_tickangle=-45)

    # Matéria
    materia_counts = dff['Materia'].value_counts().reset_index()
    materia_counts.columns = ['Materia', 'count']
    materia_counts['percentage'] = (materia_counts['count'] / materia_counts['count'].sum()) * 100
    materia_fig = px.bar(materia_counts, x='Materia', y='count', text_auto=True, title='Distribuição por Matéria',
                         labels={'count': 'Quantidade'}, color_discrete_sequence=[DPU_COLORS["primary_green"]])
    materia_fig.update_traces(texttemplate='%{y} (%{customdata[0]:.1f}%)', customdata=materia_counts[['percentage']])
    materia_fig.update_layout(xaxis_title="Matéria", yaxis_title="Quantidade", xaxis_tickangle=-45)

    # Usuário
    usuario_counts = dff['Usuário'].value_counts().reset_index()
    usuario_counts.columns = ['Usuário', 'count']
    usuario_counts['percentage'] = (usuario_counts['count'] / usuario_counts['count'].sum()) * 100
    # Limitar a N usuários para melhor visualização, por exemplo, top 15
    top_n_usuarios = 15
    usuario_counts_top = usuario_counts.head(top_n_usuarios)
    usuario_fig = px.bar(usuario_counts_top, x='Usuário', y='count', text_auto=True, title=f'Distribuição por Usuário (Top {top_n_usuarios})',
                         labels={'count': 'Quantidade'}, color_discrete_sequence=[DPU_COLORS["primary_teal"]])
    usuario_fig.update_traces(texttemplate='%{y} (%{customdata[0]:.1f}%)', customdata=usuario_counts_top[['percentage']])
    usuario_fig.update_layout(xaxis_title="Usuário", yaxis_title="Quantidade", xaxis_tickangle=-45)

    return time_series_fig, oficio_fig, pretensao_fig, materia_fig, usuario_fig


