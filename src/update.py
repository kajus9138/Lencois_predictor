# Lê dados novos
# Atualiza tabela de medicoes
# Atualiza modelos ARIMA
# Gera novas previsões 
# Atualiza tabela de previsões

import pandas as pd
import numpy as np
import os
import sqlite3
import pickle
import datetime

def tratar_outliers_iqr(df, coluna, fator=1.5, q1=0.05, q3=0.95):

    df_copy = df.copy()
    
    Q1 = df_copy[coluna].quantile(q1)
    Q3 = df_copy[coluna].quantile(q3)
    IQR = Q3 - Q1
    
    limite_inferior = Q1 - fator * IQR
    limite_superior = Q3 + fator * IQR

    # média apenas dos valores válidos (não outliers, >=0 e <=800)
    media_valida = df_copy[coluna][(df_copy[coluna] >= 0) & 
                                   (df_copy[coluna] >= limite_inferior) & 
                                   (df_copy[coluna] <= limite_superior) & 
                                   (df_copy[coluna] <= 800)].mean()
    
    # substitui valores inválidos pela média válida
    df_copy[coluna] = df_copy[coluna].mask((df_copy[coluna] < 0) | 
                                           (df_copy[coluna] < limite_inferior) | 
                                           (df_copy[coluna] > limite_superior) |
                                           (df_copy[coluna] > 800),
                                           media_valida)
    
    return df_copy

def preencher_nans(df, coluna):

    df_copy = df.copy()
    media = df_copy[coluna].mean()
    df_copy[coluna] = df_copy[coluna].fillna(media)
    return df_copy


def process_data(arquivo):
    
    df = pd.read_excel(arquivo, header=[0, 1])
    df.columns = df.columns.map(lambda x: 'timestamp' if 'Data' in str(x[0]) else x)
    col_data = ['timestamp']

    col_jusante = [col for col in df.columns if 'Jusante' in str(col[0])]
    df_med_jus = df[col_data + col_jusante].copy()

    col_montante = [col for col in df.columns if 'Montante' in str(col[0])]
    df_med_mon = df[col_data + col_montante].copy()

    df_med_jus.columns = ['timestamp', 'precipitacao_mm', 'nivel_cm', 'vazao_m3_s']
    df_med_mon.columns = ['timestamp', 'precipitacao_mm', 'nivel_cm', 'vazao_m3_s']

    df_med_jus['timestamp'] = pd.to_datetime(df_med_jus['timestamp'], format="%d/%m/%Y %H:%M", dayfirst=True, errors='coerce')
    df_med_mon['timestamp'] = pd.to_datetime(df_med_mon['timestamp'], format="%d/%m/%Y %H:%M", dayfirst=True, errors='coerce')

  


    # Substituir vírgula por ponto nas colunas numéricas e converter para float
    for df_ in [df_med_jus, df_med_mon]:
        for col in df_.columns[1:]:
            df_[col] = (df_[col]
                        .astype(str)
                        .str.replace(',', '.', regex=False)
                        .replace('-', np.nan)        # substitui traço por NaN
                        .replace('', np.nan)         # substitui strings vazias
                        .astype(float))
    
    df_med_mon.set_index('timestamp', inplace=True)
    df_med_mon = df_med_mon.resample('D').max()

    df_med_jus.set_index('timestamp', inplace=True)
    df_med_jus = df_med_jus.resample('D').max()

    df_med_mon = tratar_outliers_iqr(df_med_mon, 'nivel_cm', q1=0.15, q3=0.85)
    df_med_jus = tratar_outliers_iqr(df_med_jus, 'nivel_cm', q1=0.15, q3=0.85)
    df_med_mon = preencher_nans(df_med_mon, 'nivel_cm')
    df_med_jus = preencher_nans(df_med_jus, 'nivel_cm')
            
    return df_med_mon, df_med_jus


def etl_medicoes(ultimo_timestamp, df_med_mon, df_med_jus):
    
    first_new_timestamp = df_med_mon.index[0]

    if pd.isna(ultimo_timestamp):
        print("Sem dados passados")
        diferenca = 0
    else:
        ultimo_timestamp = pd.to_datetime(ultimo_timestamp)
        diferenca = first_new_timestamp - ultimo_timestamp

    #if diferenca == pd.Timedelta(days=1) or diferenca == 0:
    if True:
        print("iniciando ETL")
        raiz = os.path.dirname(os.path.dirname(__file__))
        db_path = os.path.join(raiz, 'dados', 'rio.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()


        cursor.execute("SELECT id, estacao FROM estacoes")
        estacao_ids = {row[1]:row[0] for row in cursor.fetchall()}

        df_med_mon['estacao_id'] = 1
        df_med_jus['estacao_id'] = 2
        

        df_med_jus.reset_index(inplace=True)
        df_med_mon.reset_index(inplace=True)

        cols = ["estacao_id", "timestamp", "nivel_cm", "vazao_m3_s", "precipitacao_mm"]

        df_med_jus[cols].to_sql('medicoes', conn, if_exists="append", index=False)
        df_med_mon[cols].to_sql("medicoes", conn, if_exists="append", index=False)

        conn.close()



    else:
        print("Dados incompatíveis")
        return('ERRO NO ETL !!!')
    
def atualiza_arima():

    raiz = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(raiz, 'dados', 'rio.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Buscando dados medidos 
    df_med_mon = pd.read_sql(f"""
        SELECT timestamp, nivel_cm
        FROM (
            SELECT timestamp, nivel_cm
            FROM medicoes
            WHERE estacao_id = {1}
            ORDER BY timestamp DESC
            LIMIT 7
        )
        ORDER BY timestamp ASC;
    """, conn)
    
    #print(df_med_mon['timestamp'])
    df_med_mon['timestamp'] = pd.to_datetime(df_med_mon['timestamp']).dt.date

    df_med_jus = pd.read_sql(f"""
        SELECT timestamp, nivel_cm
        FROM (
            SELECT timestamp, nivel_cm
            FROM medicoes
            WHERE estacao_id = {2}
            ORDER BY timestamp DESC
            LIMIT 7
        )
        ORDER BY timestamp ASC;
    """, conn)

    df_med_jus['timestamp'] = pd.to_datetime(df_med_jus['timestamp']).dt.date

    dir_arima_mon = os.path.join(raiz, 'dados', 'modelos', 'arima_mon.pkl')
    dir_arima_jus = os.path.join(raiz, 'dados', 'modelos', 'arima_jus.pkl')

    with open(dir_arima_mon, "rb") as f:
        arima_mon = pickle.load(f)

    with open(dir_arima_jus, "rb") as f:
        arima_jus = pickle.load(f)

    
    level_mon = df_med_mon['nivel_cm'].values
    level_jus = df_med_jus['nivel_cm'].values

    arima_mon = arima_mon.append(level_mon, refit=False)    
    arima_jus = arima_jus.append(level_jus, refit=False)

    with open(dir_arima_mon, "wb") as f:
        pickle.dump(arima_mon, f)
    
    with open(dir_arima_jus, "wb") as f:
        pickle.dump(arima_jus, f)
    
    
    
    '''
    forecast_mon = arima_mon.get_forecast(steps=7)
    preds_mon = forecast_mon.predicted_mean
    conf_int_mon = forecast_mon.conf_int(alpha=0.05)
    inf_mon = conf_int_mon.iloc[:, 0]
    sup_mon = conf_int_mon.iloc[:, 1]

    forecast_jus = arima_jus.get_forecast(steps=7)
    preds_mon = forecast_jus.predicted_mean
    conf_int_jus = forecast_jus.conf_int(alpha=0.05)
    inf_jus = conf_int_jus.iloc[:, 0]
    sup_jus = conf_int_jus.iloc[:, 1]

    timestamp_emissao = datetime.now()
    '''








    







        #print(df_med_jus)
    






    

