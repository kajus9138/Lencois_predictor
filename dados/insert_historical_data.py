import pandas as pd
import sqlite3
from pathlib import Path

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


df_jus = pd.read_csv('dados\Telemetria_Construserv_2025-09-10_jusante.csv', encoding='ISO-8859-1',
                 sep=';',skiprows=1, skipfooter=1, engine='python', decimal=',',
                na_values = '-')
df_jus.rename(columns={'Unnamed: 0': 'timestamp',
                       'Precipitação (mm)**': 'precipitacao_mm',
                       'Nível (cm)': 'nivel_cm',
                       'Vazão (m3/s)': 'vazao_m3_s'}, inplace=True)

df_jus['timestamp'] = pd.to_datetime(df_jus['timestamp'], dayfirst=True)
df_jus.set_index('timestamp', inplace=True)
df_jus.index.name='timestamp'
df_jus.index = pd.to_datetime(df_jus.index, format="%d/%m/%Y %H:%M", dayfirst=True, errors='coerce')



df_mon = pd.read_csv('dados\Telemetria_Construserv_2025-09-10_montante.csv', encoding='ISO-8859-1',
                 sep=';',skiprows=1, skipfooter=1, engine='python', decimal=',',
                na_values = '-')
df_mon.rename(columns={'Unnamed: 0': 'timestamp',
                       'Precipitação (mm)**': 'precipitacao_mm',
                       'Nível (cm)': 'nivel_cm',
                       'Vazão (m3/s)': 'vazao_m3_s'}, inplace=True)
df_mon['timestamp'] = pd.to_datetime(df_mon['timestamp'], dayfirst=True)
df_mon.set_index('timestamp', inplace=True)
df_mon.index.name='timestamp'
df_mon.index = pd.to_datetime(df_mon.index, format="%d/%m/%Y %H:%M", dayfirst=True, errors='coerce')

df_jus = df_jus.resample('D').max()
df_mon = df_mon.resample('D').max()

df_mon = tratar_outliers_iqr(df_mon, 'nivel_cm', q1=0.15, q3=0.85)
df_jus = tratar_outliers_iqr(df_jus, 'nivel_cm', q1=0.15, q3=0.85)
df_mon = preencher_nans(df_mon, 'nivel_cm')
df_jus = preencher_nans(df_jus, 'nivel_cm')



db_path = Path("dados") / "rio.db"
db_path.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

estacoes = [('Montante', 'Rio Lencois'), ('Jusante', 'Rio Lencois')]
for estacao, rio in estacoes:
    cursor.execute("""
        INSERT OR IGNORE INTO estacoes (estacao, rio) VALUES (?, ?)
""", (estacao, rio))

conn.commit()

cursor.execute("SELECT id, estacao FROM estacoes")
estacao_ids = {row[1]:row[0] for row in cursor.fetchall()}

df_jus['estacao_id'] = estacao_ids['Jusante']
df_mon['estacao_id'] = estacao_ids['Montante']

df_jus.reset_index(inplace=True)
df_mon.reset_index(inplace=True)

cols = ["estacao_id", "timestamp", "nivel_cm", "vazao_m3_s", "precipitacao_mm"]

df_jus[cols].to_sql('medicoes', conn, if_exists="append", index=False)
df_mon[cols].to_sql("medicoes", conn, if_exists="append", index=False)

conn.close()