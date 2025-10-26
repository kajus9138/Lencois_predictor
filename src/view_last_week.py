import os
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import matplotlib.dates as mdates


def exibir():

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'rio.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Buscando dados medidos 
    df_med_mon = pd.read_sql(f"""
        SELECT DISTINCT timestamp, nivel_cm
        FROM medicoes
        WHERE estacao_id = {1}
        LIMIT 7;
    """, conn)
    
    #print(df_med_mon['timestamp'])
    df_med_mon['timestamp'] = pd.to_datetime(df_med_mon['timestamp']).dt.date

    print(f"df_med_mon: {df_med_mon}")

    df_med_jus = pd.read_sql(f"""
        SELECT DISTINCT timestamp, nivel_cm
        FROM medicoes
        WHERE estacao_id = {2}
        LIMIT 7;
    """, conn)

    df_med_jus['timestamp'] = pd.to_datetime(df_med_jus['timestamp']).dt.date

    #print(df_med_jus)

    #Buscando dados de forecast
    
    df_fc_mon = pd.read_sql(f"""
        SELECT DISTINCT 
            timestamp_alvo, 
            nivel_previsto_cm, 
            nivel_inf, 
            nivel_sup, 
            timestamp_emissao
        FROM forecasts
        WHERE estacao_id = {1}
        LIMIT 7;
    """, conn)
    
    #df_fc_mon = df_fc_mon.drop_duplicates(subset=['timestamp_alvo', 'nivel_previsto_cm', 'nivel_inf', 'nivel_sup'])
    df_fc_mon = df_fc_mon.reset_index(drop=True)
    df_fc_mon['timestamp_alvo'] = pd.to_datetime(df_fc_mon['timestamp_alvo'], dayfirst=True, errors='coerce')
    
    print(f"df_fc_mon before: {df_fc_mon}")
    
    df_fc_mon = df_fc_mon[df_fc_mon['timestamp_alvo'].dt.date.isin(df_med_mon['timestamp'])]
    df_fc_mon = df_fc_mon.drop_duplicates(subset=['timestamp_alvo']).reset_index(drop=True)

    print(f"df_fc_mon {df_fc_mon}")
    
    df_fc_jus = pd.read_sql(f"""
        SELECT DISTINCT 
            timestamp_alvo, 
            nivel_previsto_cm, 
            nivel_inf, 
            nivel_sup, 
            timestamp_emissao
        FROM forecasts
        WHERE estacao_id = {2}
        LIMIT 7;
    """, conn)
    
    
    #df_fc_jus = df_fc_jus.drop_duplicates(subset=['timestamp_alvo', 'nivel_previsto_cm', 'nivel_inf', 'nivel_sup'])
    df_fc_jus = df_fc_jus.reset_index(drop=True)
    df_fc_jus['timestamp_alvo'] = pd.to_datetime(df_fc_jus['timestamp_alvo'], dayfirst=True, errors='coerce')
    df_fc_jus = df_fc_jus[df_fc_jus['timestamp_alvo'].dt.date.isin(df_med_jus['timestamp'])]
    df_fc_jus = df_fc_jus.drop_duplicates(subset=['timestamp_alvo']).reset_index(drop=True)


    mae_mon = mean_absolute_error(df_med_mon['nivel_cm'], df_fc_mon['nivel_previsto_cm'])
    rmse_mon = np.sqrt(mean_squared_error(df_med_mon['nivel_cm'], df_fc_mon['nivel_previsto_cm']))
    erro_max_mon = np.max(np.abs(df_med_mon['nivel_cm'] - df_fc_mon['nivel_previsto_cm']))

    mae_jus = mean_absolute_error(df_med_jus['nivel_cm'], df_fc_jus['nivel_previsto_cm'])
    rmse_jus = np.sqrt(mean_squared_error(df_med_jus['nivel_cm'], df_fc_jus['nivel_previsto_cm']))
    erro_max_jus = np.max(np.abs(df_med_jus['nivel_cm'] - df_fc_jus['nivel_previsto_cm']))


    df_med_mon['timestamp'] = pd.to_datetime(df_med_mon['timestamp'], errors='coerce')
    df_fc_mon['timestamp_alvo'] = pd.to_datetime(df_fc_mon['timestamp_alvo'], errors='coerce')
    df_med_jus['timestamp'] = pd.to_datetime(df_med_jus['timestamp'], errors='coerce')
    df_fc_jus['timestamp_alvo'] = pd.to_datetime(df_fc_jus['timestamp_alvo'], errors='coerce')


    # Plots
    fig, axs = plt.subplots(1, 2, figsize=(20, 8))

    # --- Montante ---
    axs[0].plot(df_med_mon['timestamp'], df_med_mon['nivel_cm'], color='blue', linewidth=3)
    axs[0].plot(df_fc_mon['timestamp_alvo'], df_fc_mon['nivel_previsto_cm'], color='orange', linewidth=3)
    axs[0].fill_between(df_fc_mon['timestamp_alvo'],
                        df_fc_mon['nivel_inf'],
                        df_fc_mon['nivel_sup'],
                        color='orange', alpha=0.5,
                        label="Intervalo de Confiança (95%)")

    axs[0].set_xlabel("Data")
    axs[0].set_ylabel("Nível (cm)")
    axs[0].set_title("Estação: Montante — Última semana")
    axs[0].grid(True, linestyle="--", alpha=0.6)

    axs[0].text(0.02, 0.95,
                f"MAE: {mae_mon:.2f} cm\nRMSE: {rmse_mon:.2f} cm\nErro Máx: {erro_max_mon:.2f} cm",
                transform=axs[0].transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

    # --- Jusante ---
    axs[1].plot(df_med_jus['timestamp'], df_med_jus['nivel_cm'], color='blue', linewidth=3)
    axs[1].plot(df_fc_jus['timestamp_alvo'], df_fc_jus['nivel_previsto_cm'], color='orange', linewidth=3)
    axs[1].fill_between(df_fc_jus['timestamp_alvo'],
                        df_fc_jus['nivel_inf'],
                        df_fc_jus['nivel_sup'],
                        color='orange', alpha=0.5,
                        label="Intervalo de Confiança (95%)")

    axs[1].set_xlabel("Data")
    axs[1].set_ylabel("Nível (cm)")
    axs[1].set_title("Estação: Jusante — Última semana")
    axs[1].grid(True, linestyle="--", alpha=0.6)

    axs[1].text(0.02, 0.95,
                f"MAE: {mae_jus:.2f} cm\nRMSE: {rmse_jus:.2f} cm\nErro Máx: {erro_max_jus:.2f} cm",
                transform=axs[1].transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

    # --- Formatação do eixo X ---
    for ax in axs:
        # Garantir que os dados do eixo X são datetime64
        if ax == axs[0]:
            ax.xaxis_date()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        else:
            ax.xaxis_date()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        
        ax.tick_params(axis='x', rotation=45)

    st.pyplot(fig)


