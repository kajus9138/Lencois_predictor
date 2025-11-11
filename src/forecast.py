import pickle
import os
from pathlib import Path
from datetime import datetime
import sqlite3
import logging
import numpy as np
import streamlit as st
import pandas as pd

logging.basicConfig(
    level=logging.INFO,  # nível mínimo de log a ser mostrado
    format='%(asctime)s - %(levelname)s - %(message)s',  # formato das mensagens
    filename='forecast.log',  # arquivo onde os logs serão salvos
    filemode='a'  # 'a' = append (adiciona ao arquivo); 'w' = overwrite (sobrescreve)
)

raiz = os.path.dirname(os.path.dirname(__file__))
arima_mon = os.path.join(raiz, 'dados', 'modelos', 'arima_mon.pkl')
arima_jus = os.path.join(raiz, 'dados', 'modelos', 'arima_jus.pkl')

def insere_forecasts(modelo, estacao_id, day_1): 
    logging.info("iniciando novos forecasts")

    with open(modelo, "rb") as f:
        resultado = pickle.load(f)

    ultimo_timestamp = resultado.data.row_labels[-1]
    print(f"ultimo timestamp: {ultimo_timestamp}")

    forecast = resultado.get_forecast(steps=7)
    preds = forecast.predicted_mean
    conf_int = forecast.conf_int(alpha=0.05)

    # gerar timestamps diários entre start_day e end_day
    day_7 = pd.to_datetime(day_1) + pd.Timedelta(days=6)
    timestamps_range = pd.date_range(start=day_1, end=day_7, freq="D")
    print(f"\n\n timestamps_range:{timestamps_range}\n\n")

    if len(timestamps_range) != len(preds):
        raise ValueError(
            f"Quantidade de timestamps ({len(timestamps_range)}) "
            f"não coincide com quantidade de previsões ({len(preds)})."
        )

    timestamp_emissao = datetime.now()
    modelo = "ARIMA"
    versao_modelo = "1.0"
    estacao_id = estacao_id
    
    raiz = os.path.dirname(os.path.dirname(__file__))
    db_path = Path(raiz) / "dados" / "rio.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    niveis_sup = []
    predicted_means = []

    # percorrer os timestamps novos junto com os valores previstos
    for ts_alvo, (orig_ts, nivel_previsto_cm) in zip(timestamps_range, preds.items()):

        intervalo = conf_int.loc[orig_ts]
        nivel_inf = float(intervalo[0])
        nivel_sup = float(intervalo[1])

        niveis_sup.append(nivel_sup)
        predicted_means.append(float(nivel_previsto_cm))

        print(ts_alvo)

        cursor.execute("""
            INSERT INTO forecasts (
                estacao_id, timestamp_emissao, timestamp_alvo,
                nivel_previsto_cm, nivel_inf, nivel_sup, modelo, versao_modelo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            estacao_id,
            timestamp_emissao.strftime("%d/%m/%Y %H:%M"),
            ts_alvo.strftime("%d/%m/%Y %H:%M"),   # <<< usa timestamp do range
            float(nivel_previsto_cm),
            nivel_inf,
            nivel_sup,
            modelo,
            versao_modelo
        ))

    conn.commit()
    conn.close()

    if np.array(predicted_means).max() >= 200 and estacao_id == 1:
        st.error("Alerta: Previsão média para montante acima de 1 metro !!")
    if np.array(niveis_sup).max() >= 200 and estacao_id == 1:
        st.warning("Alerta: Nível superior para montante acima de 1 metro !!")
    
    if np.array(predicted_means).max() >= 200 and estacao_id == 2:
        st.error("Alerta: Previsão média para jusante acima de 1 metro !!")
    if np.array(niveis_sup).max() >= 200 and estacao_id == 2:
        st.warning("Alerta: Nível superior para jusante acima de 1 metro !!")

    return

