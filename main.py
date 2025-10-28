
# Leitura do dicionário de configuração

# Verifica se há arquivo com novos dados
    #SIM:
        # VERIFICA COMPATIBILIDADE
        # ETL
        # ATUALIZA ARIMA
        # GET FORECAST
        # PLOT LAST WEEK (QUERY MASCARA)
        # PLOT NEXT WEEK

    #NÃO:
        #GET FORECAST
        #PLOT NEXT WEEK


import configparser
import sqlite3
from pathlib import Path
import os
from src import view_next_week, view_last_week, layout, update, forecast
import streamlit as st
import logging

logging.basicConfig(
    level=logging.INFO,  # nível mínimo de log a ser mostrado
    format='%(asctime)s - %(levelname)s - %(message)s',  # formato das mensagens
    filename='app.log',  # arquivo onde os logs serão salvos
    filemode='a'  # 'a' = append (adiciona ao arquivo); 'w' = overwrite (sobrescreve)
)


# Leitura do arquivo de configuração
config = configparser.ConfigParser()
config.read('config.ini')
#modo = config['modo']['teste']
#print(type(modo))


# Conexão ao banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'dados', 'rio.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Último timestamp
cursor.execute("SELECT timestamp FROM medicoes ORDER BY timestamp DESC LIMIT 1;")
ultimo_timestamp = cursor.fetchone()

if ultimo_timestamp is not None:
    ultimo_timestamp = ultimo_timestamp[0]
else:
    ultimo_timestamp = None

# Leitura do arquivo de novos dados
arquivo = os.path.join( os.path.dirname(__file__), 'input', config['new_data']['arquivo'])
logging.info(f"Lendo novos dados em: {arquivo}")

# Execução da aplicação

if os.path.isfile(arquivo):
    layout.exibir_cabecalho()
    update.etl_medicoes(ultimo_timestamp, arquivo)
    update.atualiza_arima()
    arima_mon = os.path.join('dados', 'modelos', 'arima_mon.pkl')
    arima_jus = os.path.join('dados', 'modelos', 'arima_jus.pkl')
    forecast.insere_forecasts(arima_mon, estacao_id=1)
    forecast.insere_forecasts(arima_jus, estacao_id=2)

    view_last_week.exibir()
    view_next_week.exibir()



else:
    layout.exibir_cabecalho()
    arima_mon = os.path.join('dados', 'modelos', 'arima_mon.pkl')
    arima_jus = os.path.join('dados', 'modelos', 'arima_jus.pkl')
    forecast.insere_forecasts(arima_mon, estacao_id=1)
    forecast.insere_forecasts(arima_jus, estacao_id=2)

    ## roda o view_next_week com os dados da última semana de previsões disponível
    view_next_week.exibir()









