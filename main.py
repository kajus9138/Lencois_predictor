

import configparser
import sqlite3
from pathlib import Path
import os
from src import view_next_week, view_last_week, update, forecast, layout
import streamlit as st
import logging
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

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


uploaded_file = st.file_uploader("Envie arquivo de dados de medição atualizados", type=["xlsx"])
if uploaded_file is not None:
    destino = os.path.join(os.path.dirname(__file__), 'input', 'novo_dado.xlsx')
    with open(destino, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Arquivo enviado com sucesso. Reprocessando dados...")
    arquivo = destino
else:
    # Leitura do arquivo de novos dados
    arquivo = os.path.join( os.path.dirname(__file__), 'input', config['new_data']['arquivo'])
    logging.info(f"Lendo novos dados em: {arquivo}")

print(f"arquivo: {arquivo}")

# Conexão ao banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'dados', 'rio.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Último timestamp
cursor.execute("SELECT timestamp FROM medicoes ORDER BY timestamp DESC LIMIT 1;")
ultimo_timestamp = cursor.fetchone()

if ultimo_timestamp is not None:
    ultimo_timestamp = ultimo_timestamp[0]
else:  # primeiro forecast
    ultimo_timestamp = None
 


#print(f"ultimo_timestamp type: {type(ultimo_timestamp)}\n")
#print(f"first_new_timestamp type: {type(first_new_timestamp)}\n")

# Execução da aplicação

if os.path.isfile(arquivo) and ultimo_timestamp is not None:
    layout.exibir_cabecalho()
    df_med_mon, df_med_jus = update.process_data(arquivo)
    first_new_timestamp = df_med_mon.index[0]
    last_timestamp = datetime.strptime(ultimo_timestamp, "%Y-%m-%d %H:%M:%S")

    forecast_day_init = df_med_mon.index[-1] + pd.Timedelta(days=1)



    if df_med_jus['nivel_cm'].max() >= 200:
        st.error("Alerta: nível medido para jusante da semana ultrapassou 2 metros !")
    if df_med_mon['nivel_cm'].max() >= 200:
        st.error("Alerta: nível medido para montante da semana ultrapassou 2 metros !")


    if first_new_timestamp.date() == last_timestamp.date() + timedelta(days=1):
        if df_med_jus['nivel_cm'].max() >= 200:
            st.error("Alerta: nível medido para jusante da semana ultrapassou 2 metros !")
        if df_med_mon['nivel_cm'].max() >= 200:
            st.error("Alerta: nível medido para montante da semana ultrapassou 2 metros !")

        
        


        update.etl_medicoes(ultimo_timestamp, df_med_mon, df_med_jus)
        update.atualiza_arima()
        arima_mon = os.path.join('dados', 'modelos', 'arima_mon.pkl')
        arima_jus = os.path.join('dados', 'modelos', 'arima_jus.pkl')
        forecast.insere_forecasts(arima_mon, estacao_id=1, day_1=forecast_day_init)
        forecast.insere_forecasts(arima_jus, estacao_id=2, day_1=forecast_day_init)


        

    view_last_week.exibir()
    view_next_week.exibir()

elif os.path.isfile(arquivo) and ultimo_timestamp is None:
    df_med_mon, df_med_jus = update.process_data(arquivo)
    forecast_day_init = df_med_mon.index[-1] + pd.Timedelta(days=1)
    update.etl_medicoes(ultimo_timestamp, df_med_mon, df_med_jus)
    update.atualiza_arima()
    arima_mon = os.path.join('dados', 'modelos', 'arima_mon.pkl')
    arima_jus = os.path.join('dados', 'modelos', 'arima_jus.pkl')
    forecast.insere_forecasts(arima_mon, estacao_id=1, day_1=forecast_day_init)
    forecast.insere_forecasts(arima_jus, estacao_id=2, day_1=forecast_day_init)
        
    

    view_last_week.exibir()
    view_next_week.exibir()



else:
    layout.exibir_cabecalho()
    #arima_mon = os.path.join('dados', 'modelos', 'arima_mon.pkl')
    #arima_jus = os.path.join('dados', 'modelos', 'arima_jus.pkl')
    #forecast.insere_forecasts(arima_mon, estacao_id=1, day_1 = '2025-09-11 00:00:00')
    #forecast.insere_forecasts(arima_jus, estacao_id=2, day_1 = '2025-09-11 00:00:00')
        
    

    ## roda o view_next_week com os dados da última semana de previsões disponível
    view_last_week.exibir()
    view_next_week.exibir()











