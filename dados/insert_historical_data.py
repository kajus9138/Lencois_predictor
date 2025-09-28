import pandas as pd
import sqlite3
from pathlib import Path

df_jus = pd.read_csv('dados\Telemetria_Construserv_2025-09-17_jusante.csv', encoding='ISO-8859-1',
                 sep=';',skiprows=1, skipfooter=1, engine='python', decimal=',',
                na_values = '-')
df_jus.rename(columns={'Unnamed: 0': 'timestamp',
                       'Precipitação (mm)**': 'precipitacao_mm',
                       'Nível (cm)': 'nivel_cm',
                       'Vazão (m3/s)': 'vazao_m3_s'}, inplace=True)
df_jus['timestamp'] = pd.to_datetime(df_jus['timestamp'], dayfirst=True)

df_mon = pd.read_csv('dados\Telemetria_Construserv_2025-09-17_montante.csv', encoding='ISO-8859-1',
                 sep=';',skiprows=1, skipfooter=1, engine='python', decimal=',',
                na_values = '-')
df_mon.rename(columns={'Unnamed: 0': 'timestamp',
                       'Precipitação (mm)**': 'precipitacao_mm',
                       'Nível (cm)': 'nivel_cm',
                       'Vazão (m3/s)': 'vazao_m3_s'}, inplace=True)
df_mon['timestamp'] = pd.to_datetime(df_mon['timestamp'], dayfirst=True)

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

cols = ["estacao_id", "timestamp", "nivel_cm", "vazao_m3_s", "precipitacao_mm"]

df_jus[cols].to_sql('medicoes', conn, if_exists="append", index=False)
df_mon[cols].to_sql("medicoes", conn, if_exists="append", index=False)

conn.close()