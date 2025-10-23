
# Leitura do dicionário de configuração

#Caso principal:

    # Conecta ao banco de dados
    # Retorna último timestamp
    #Cria visualização da última semana real x previsto
    # Verifica se há arquivo no dir input
        #Sim: Verifica se o primeiro timestamp é compatível com o último do banco
            #Processa os dados e carrega no banco
            #Executa forecast
            # Cria visualização da próxima semana
        #Não: # printa mensagem: "Sem dados de entrada"
            # encerra o programa


import configparser
import sqlite3
from pathlib import Path
import os
from src import view_last_mon, layout
import streamlit as st

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
ultimo_timestamp = ultimo_timestamp[0]


layout.exibir_cabecalho()

#Cria visualização da última semana real x previsto
view_last_mon.exibir()




