import os
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import numpy as np
import matplotlib.patches as patches
from .funcoes_estilizar import aplicar_estilo 



def exibir():
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'rio.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Buscando dados de forecast
    df_fc_mon = pd.read_sql(f"""
        SELECT DISTINCT timestamp_alvo, nivel_previsto_cm, nivel_inf, nivel_sup
        FROM forecasts
        WHERE estacao_id = {1}
        ORDER BY date(substr(timestamp_alvo, 7, 4) || '-' || substr(timestamp_alvo, 4, 2) || '-' || substr(timestamp_alvo, 1, 2)) DESC
        LIMIT 7;
    """, conn)
    
    df_fc_mon = df_fc_mon.drop_duplicates(subset=['timestamp_alvo', 'nivel_previsto_cm', 'nivel_inf', 'nivel_sup'])
    df_fc_mon = df_fc_mon.reset_index(drop=True)
    df_fc_mon['timestamp_alvo'] = pd.to_datetime(df_fc_mon['timestamp_alvo'], format='%d/%m/%Y %H:%M', errors='coerce')

    #print(f"olha o df aí {df_fc_mon}")

    df_fc_jus = pd.read_sql(f"""
        SELECT DISTINCT timestamp_alvo, nivel_previsto_cm, nivel_inf, nivel_sup
        FROM forecasts
        WHERE estacao_id = {2}
        ORDER BY date(substr(timestamp_alvo, 7, 4) || '-' || substr(timestamp_alvo, 4, 2) || '-' || substr(timestamp_alvo, 1, 2)) DESC
        LIMIT 7;
    """, conn)
    
    df_fc_jus = df_fc_jus.drop_duplicates(subset=['timestamp_alvo', 'nivel_previsto_cm', 'nivel_inf', 'nivel_sup'])
    df_fc_jus = df_fc_jus.reset_index(drop=True)
    df_fc_jus['timestamp_alvo'] = pd.to_datetime(df_fc_jus['timestamp_alvo'], format='%d/%m/%Y %H:%M', errors='coerce')

    fig, axs = plt.subplots(1, 2, figsize=(20, 8)) 

    axs[0].plot(df_fc_mon['timestamp_alvo'],df_fc_mon['nivel_previsto_cm'], color='blue', linewidth=4)
    axs[0].fill_between(df_fc_mon['timestamp_alvo'],
                        df_fc_mon['nivel_inf'],
                        df_fc_mon['nivel_sup'],
                        color='#5894bf',
                        alpha=0.5,
                        label="Intervalo de Confiança (95%)")
    aplicar_estilo(axs[0], "Estação Montante – Última semana")

    axs[0].set_xlabel("Data")
    axs[0].set_ylabel("Nível (cm)")
    axs[0].set_title(f"Estação: Montante — Última semana")
    axs[0].legend()
    axs[0].grid(True, linestyle="--", alpha=0.6)

    axs[1].plot(df_fc_jus['timestamp_alvo'],df_fc_jus['nivel_previsto_cm'], color='blue', linewidth=4, label='Previsto')
    axs[1].fill_between(df_fc_jus['timestamp_alvo'],
                        df_fc_jus['nivel_inf'],
                        df_fc_jus['nivel_sup'],
                        color='#5894bf', alpha=0.5,
                        label="Intervalo de Confiança (95%)")
    
    aplicar_estilo(axs[1], "Estação Jusante – Última semana")
    
    axs[1].set_xlabel("Data")
    axs[1].set_ylabel("Nível (cm)")
    axs[1].set_title(f"Estação: Jusante — Última semana")
    axs[1].legend()
    axs[1].grid(True, linestyle="--", alpha=0.6)
    axs[1].legend(loc='upper right')
    
    for ax in axs:
        ax.tick_params(axis='x', rotation=45)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.set_xlim(df_fc_mon['timestamp_alvo'].min(), df_fc_mon['timestamp_alvo'].max())


    st.pyplot(fig)


