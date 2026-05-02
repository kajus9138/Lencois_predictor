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
    # 1. Leitura mantendo o cabeçalho duplo
    df = pd.read_excel(arquivo, header=[0, 1])
    
    # Mapeamento do timestamp
    df.columns = df.columns.map(lambda x: 'timestamp' if 'Data' in str(x[0]) else x)
    col_data = ['timestamp']

    # 2. Separação Jusante/Montante
    col_jusante = [col for col in df.columns if 'Jusante' in str(col[0])]
    df_med_jus = df[col_data + col_jusante].copy()

    col_montante = [col for col in df.columns if 'Montante' in str(col[0])]
    df_med_mon = df[col_data + col_montante].copy()

    # 3. Renomeação consistente
    df_med_jus.columns = ['timestamp', 'precipitacao_mm', 'nivel_cm', 'vazao_m3_s']
    df_med_mon.columns = ['timestamp', 'precipitacao_mm', 'nivel_cm', 'vazao_m3_s']

    # --- INÍCIO DA MELHORIA DE BLINDAGEM ---
    
    for df_ in [df_med_jus, df_med_mon]:
        # A. Tratamento robusto de Datas (Converte e remove o que for inválido/NaT)
        df_['timestamp'] = pd.to_datetime(df_['timestamp'], dayfirst=True, errors='coerce')

        # C. Limpeza numérica aprimorada (Trata o erro 2.696.40 e vírgulas)
        for col in df_.columns[1:]:
            df_[col] = (df_[col]
                        .astype(str)
                        .str.replace('.', '', regex=False)  # Remove ponto de milhar
                        .str.replace(',', '.', regex=False)  # Garante ponto decimal
                        .replace('-', np.nan)
                        .replace('nan', np.nan)             # Caso a conversão para str gere 'nan'
                        .replace('', np.nan))
            
            # B. Remove linhas onde o timestamp falhou (isso evita o erro NaTType no resample)
            df_.dropna(subset=['timestamp'], inplace=True)
            
            # Converte para float de forma segura (erros viram NaN)
            df_[col] = pd.to_numeric(df_[col], errors='coerce')

    # --- FIM DA MELHORIA ---

    # 4. Configuração de Índice e Resample
    # Agora garantimos que não há NaT no índice antes de resamplear
    df_med_mon.set_index('timestamp', inplace=True)
    df_med_mon = df_med_mon.resample('D').max()

    df_med_jus.set_index('timestamp', inplace=True)
    df_med_jus = df_med_jus.resample('D').max()

    # 5. Tratamentos Estatísticos (Mantendo suas funcionalidades)
    df_med_mon = tratar_outliers_iqr(df_med_mon, 'nivel_cm', q1=0.15, q3=0.85)
    df_med_jus = tratar_outliers_iqr(df_med_jus, 'nivel_cm', q1=0.15, q3=0.85)
    
    df_med_mon = preencher_nans(df_med_mon, 'nivel_cm')
    df_med_jus = preencher_nans(df_med_jus, 'nivel_cm')
            
    return df_med_mon, df_med_jus

def etl_medicoes(ultimo_timestamp, df_med_mon, df_med_jus):
    
    first_new_timestamp = df_med_mon.index[0]

    if pd.isna(ultimo_timestamp):
        print("Sem dados passados")
        corte = None
    else:
        corte = pd.to_datetime(ultimo_timestamp)

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

    if corte is not None:
        df_med_mon = df_med_mon[df_med_mon['timestamp'] > corte]
        df_med_jus = df_med_jus[df_med_jus['timestamp'] > corte]

    cols = ["estacao_id", "timestamp", "nivel_cm", "vazao_m3_s", "precipitacao_mm"]

    df_med_jus[cols].to_sql('medicoes', conn, if_exists="append", index=False)
    df_med_mon[cols].to_sql("medicoes", conn, if_exists="append", index=False)

    conn.close()
    
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

    dir_arima_mon = os.path.join(raiz, 'dados', 'modelos', 'arimax_mon.pkl')
    dir_arima_jus = os.path.join(raiz, 'dados', 'modelos', 'arimax_jus.pkl')

    with open(dir_arima_mon, "rb") as f:
        arima_mon = pickle.load(f)

    with open(dir_arima_jus, "rb") as f:
        arima_jus = pickle.load(f)

    
    level_mon = df_med_mon['nivel_cm'].values
    novas_chuvas_mon = df_med_mon['precipitacao_mm'].values #add devido novo modelo sarimax
    level_jus = df_med_jus['nivel_cm'].values
    novas_chuvas_jus = df_med_jus['precipitacao_mm'].values #add devido novo modelo sarimax

    #arima_mon = arima_mon.append(level_mon, refit=False)   modificado para 
    arima_mon = arima_mon.append(endog=level_mon, exog=novas_chuvas_mon, refit=False)
    #arima_jus = arima_jus.append(level_jus, refit=False)
    arima_mon = arima_mon.append(endog=level_jus, exog=novas_chuvas_jus, refit=False)

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
    