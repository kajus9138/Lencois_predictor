import os
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import matplotlib.dates as mdates
import logging

logging.basicConfig(
    level=logging.INFO,  # nível mínimo de log a ser mostrado
    format='%(asctime)s - %(levelname)s - %(message)s',  # formato das mensagens
    filename='last_week.log',  # arquivo onde os logs serão salvos
    filemode='a'  # 'a' = append (adiciona ao arquivo); 'w' = overwrite (sobrescreve)
)


def exibir():



    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'rio.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM medicoes;")
    qtd_registros = cursor.fetchone()[0]

    if qtd_registros == 0:
        print("A tabela 'medicoes' está vazia.")
        return

    logging.info("Iniciando exibição de gráficos de comparação. . .")

    fim = pd.read_sql(
        """
        SELECT MAX(
        CASE
            WHEN instr(timestamp, '/') > 0 THEN
            -- caso formato seja DD/MM/YYYY HH:MM:SS
            substr(timestamp, 7, 4) || '-' ||  -- ano
            substr(timestamp, 4, 2) || '-' ||  -- mês
            substr(timestamp, 1, 2) || ' ' ||  -- dia
            substr(timestamp, 12, 8)           -- HH:MM:SS (8 caracteres)
            ELSE
            -- já está em YYYY-MM-DD HH:MM:SS (padrão ISO)
            substr(timestamp, 1, 19)           -- pega YYYY-MM-DD HH:MM:SS
        END
        ) AS ultimo_timestamp
        FROM medicoes;
        """,
        conn
    )

    fim = fim['ultimo_timestamp'].iloc[0]
    # Parse seguro: agora fim está em 'YYYY-MM-DD HH:MM:SS'
    fim = pd.to_datetime(fim, dayfirst=False)

    inicio = fim - pd.Timedelta(days=7)
    inicio_med = inicio + pd.Timedelta(days=1)

    # Se quiser strings para logs
    fim_s = str(fim)
    inicio_s = str(inicio)
    inicio_med_s = str(inicio_med)

    logging.info(f"Periodo de forecasts: {inicio_s} a {fim_s}")
    logging.info(f"Periodo de medicoes: {inicio_med_s} a {fim_s}")

    #Buscando dados medidos 
    df_med_mon = pd.read_sql(f"""
    SELECT m.timestamp, m.nivel_cm
    FROM medicoes m
    JOIN (
        SELECT timestamp, MAX(id) AS max_id
        FROM medicoes
        WHERE estacao_id = {1}
          AND timestamp BETWEEN '{inicio_med}' AND '{fim}'
        GROUP BY timestamp
    ) x
    ON m.id = x.max_id
    ORDER BY m.timestamp;
    """, conn)
    
    #print(df_med_mon['timestamp'])
    df_med_mon['timestamp'] = pd.to_datetime(df_med_mon['timestamp']).dt.date
    logging.info("Últimos dados medidos a montante, df_med_mon: {df_med_mon}")


    df_med_jus = pd.read_sql(f"""
    SELECT m.timestamp, m.nivel_cm
    FROM medicoes m
    JOIN (
        SELECT timestamp, MAX(id) AS max_id
        FROM medicoes
        WHERE estacao_id = {2}
          AND timestamp BETWEEN '{inicio_med}' AND '{fim}'
        GROUP BY timestamp
    ) x
    ON m.id = x.max_id
    ORDER BY m.timestamp;
    """, conn)

    df_med_jus['timestamp'] = pd.to_datetime(df_med_jus['timestamp']).dt.date
    logging.info("Últimos dados medidos a jusante, df_med_jus: {df_med_jus}")

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
    AND strftime('%Y-%m-%d %H:%M', substr(timestamp_alvo, 7, 4) || '-' || substr(timestamp_alvo, 4, 2) || '-' || substr(timestamp_alvo, 1, 2) || ' ' || substr(timestamp_alvo, 12, 5))
        BETWEEN '{inicio}' AND '{fim}'
    ORDER BY timestamp_alvo;
    """, conn)
    
    #df_fc_mon = df_fc_mon.drop_duplicates(subset=['timestamp_alvo', 'nivel_previsto_cm', 'nivel_inf', 'nivel_sup'])
    df_fc_mon = df_fc_mon.reset_index(drop=True)
    df_fc_mon['timestamp_alvo'] = pd.to_datetime(df_fc_mon['timestamp_alvo'], dayfirst=True, errors='coerce')
    df_fc_mon = df_fc_mon[df_fc_mon['timestamp_alvo'].dt.date.isin(df_med_mon['timestamp'])]
    df_fc_mon = df_fc_mon.drop_duplicates(subset=['timestamp_alvo']).reset_index(drop=True)

    logging.info("Previsões a montante, df_fc_mon: {df_fc_mon}")
    
    df_fc_jus = pd.read_sql(f"""
        SELECT DISTINCT 
            timestamp_alvo, 
            nivel_previsto_cm, 
            nivel_inf, 
            nivel_sup, 
            timestamp_emissao
    FROM forecasts
    WHERE estacao_id = {2}
    AND strftime('%Y-%m-%d %H:%M', substr(timestamp_alvo, 7, 4) || '-' || substr(timestamp_alvo, 4, 2) || '-' || substr(timestamp_alvo, 1, 2) || ' ' || substr(timestamp_alvo, 12, 5))
        BETWEEN '{inicio}' AND '{fim}'
    ORDER BY timestamp_alvo;
    """, conn)
    
    
    #df_fc_jus = df_fc_jus.drop_duplicates(subset=['timestamp_alvo', 'nivel_previsto_cm', 'nivel_inf', 'nivel_sup'])
    df_fc_jus = df_fc_jus.reset_index(drop=True)
    df_fc_jus['timestamp_alvo'] = pd.to_datetime(df_fc_jus['timestamp_alvo'], dayfirst=True, errors='coerce')
    df_fc_jus = df_fc_jus[df_fc_jus['timestamp_alvo'].dt.date.isin(df_med_jus['timestamp'])]
    df_fc_jus = df_fc_jus.drop_duplicates(subset=['timestamp_alvo']).reset_index(drop=True)

    logging.info("Previsões a jusante, df_fc_jus: {df_fc_jus}")


    df_fc_mon = df_fc_mon.sort_values(by='timestamp_alvo').reset_index(drop=True)
    df_fc_jus = df_fc_jus.sort_values(by='timestamp_alvo').reset_index(drop=True)


    print(f"df_med_mon: {df_med_mon}")
    print(f"df_med_jus: {df_med_jus}")

    print(f"df_fc_mon: {df_fc_mon}")
    print(f"df_fc_jus: {df_fc_jus}")

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
    axs[1].plot(df_med_jus['timestamp'], df_med_jus['nivel_cm'], color='blue', linewidth=3, label='Real')
    axs[1].plot(df_fc_jus['timestamp_alvo'], df_fc_jus['nivel_previsto_cm'], color='orange', linewidth=3, label='Previsto')
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
    axs[1].legend(loc='upper right')

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

    figuras_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)


    nome_arquivo = f'comparacao_{str(inicio)[:10]}_a_{str(fim)[:10]}.png'
    caminho_arquivo = os.path.join(figuras_dir, nome_arquivo)
    fig.savefig(caminho_arquivo, dpi=300, bbox_inches='tight')

    st.pyplot(fig)


