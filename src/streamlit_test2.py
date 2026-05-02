import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import os
from pathlib import Path

# --- Configurações iniciais ---
st.set_page_config(page_title="Gráfico Real x Predito", layout="wide")
st.title("📈 Comparativo Real x Predito (Última Semana)")

# --- Caminho do banco ---
try:
    raiz = Path(__file__).parent  # diretório do script
except NameError:
    # fallback caso __file__ não esteja definido (ex: em alguns notebooks ou streamlit)
    raiz = Path(os.getcwd())

#db_path = raiz / "dados" / "rio.db"
db_path = r"C:\Users\ksilva\OneDrive - Technomar\Documentos\PI\Lencois_predictor\dados\rio.db"

#
# print("Caminho do banco:", db_path)
#print("Banco existe?", db_path.exists())
#raiz = os.path.dirname(os.path.dirname(__file__))
#db_path = os.path.join(raiz,'dados','rio.db')
#raiz = Path.cwd()  # diretório onde você rodou o streamlit
#db_path = raiz / "dados" / "rio.db"

# --- Conexão com o banco ---
conn = sqlite3.connect(db_path)

# --- Selecionar estação ---
estacoes = pd.read_sql("SELECT id, estacao FROM estacoes", conn)
if estacoes.empty:
    st.warning("Nenhuma estação cadastrada no banco.")
    st.stop()

estacao_nome = st.selectbox("Selecione a estação:", estacoes["estacao"])
estacao_id = int(estacoes.loc[estacoes["estacao"] == estacao_nome, "id"].iloc[0])

# --- Buscar medições ---
df_med = pd.read_sql(f"""
    SELECT timestamp, nivel_cm
    FROM medicoes
    WHERE estacao_id = {estacao_id}
    ORDER BY timestamp
""", conn)

if df_med.empty:
    st.warning("Nenhuma medição disponível para esta estação.")
    st.stop()

# --- Converter timestamp e filtrar última semana ---
df_med["timestamp"] = pd.to_datetime(df_med["timestamp"], dayfirst=True, errors="coerce")
ultima_data = df_med["timestamp"].max()
inicio_periodo = ultima_data - timedelta(days=7)
df_med_semana = df_med[df_med["timestamp"] >= inicio_periodo]

# --- Buscar forecasts correspondentes ---
df_fc = pd.read_sql(f"""
    SELECT timestamp_alvo, nivel_previsto_cm, nivel_inf, nivel_sup, timestamp_emissao
    FROM forecasts
    WHERE estacao_id = {estacao_id}
    ORDER BY timestamp_alvo
""", conn)
conn.close()

if df_fc.empty:
    st.warning("Nenhum forecast disponível para esta estação.")
    st.stop()

df_fc["timestamp_alvo"] = pd.to_datetime(df_fc["timestamp_alvo"], dayfirst=True, errors="coerce")

# Filtrar previsões dentro do intervalo das medições
df_fc_semana = df_fc[(df_fc["timestamp_alvo"] >= inicio_periodo) & (df_fc["timestamp_alvo"] <= ultima_data)]

# --- Gráfico ---
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(df_med_semana["timestamp"], df_med_semana["nivel_cm"], label="Nível Real (cm)", color="black", linewidth=2)
ax.plot(df_fc_semana["timestamp_alvo"], df_fc_semana["nivel_previsto_cm"], label="Nível Previsto (cm)", color="blue", linestyle="--", linewidth=2)

# Faixa de confiança
ax.fill_between(df_fc_semana["timestamp_alvo"], df_fc_semana["nivel_inf"], df_fc_semana["nivel_sup"],
                color="blue", alpha=0.2, label="Intervalo de Confiança (95%)")

ax.set_xlabel("Data")
ax.set_ylabel("Nível (cm)")
ax.set_title(f"Estação: {estacao_nome} — Última semana")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.6)
plt.xticks(rotation=30)

st.pyplot(fig)

# --- Mostrar dados ---
with st.expander("📋 Ver dados brutos"):
    st.dataframe(df_med_semana.merge(df_fc_semana, left_on="timestamp", right_on="timestamp_alvo", how="outer"))
