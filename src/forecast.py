import pickle
import os
from pathlib import Path
from datetime import datetime
import sqlite3

raiz = os.path.dirname(os.path.dirname(__file__))
arima_mon = os.path.join(raiz, 'dados', 'modelos', 'arima_mon.pkl')
arima_jus = os.path.join(raiz, 'dados', 'modelos', 'arima_jus.pkl')

def insere_forecasts(modelo, estacao_id):

    print("iniciando novos forecasts")
    
    

    with open(modelo, "rb") as f:
        resultado = pickle.load(f)

    ultimo_timestamp = resultado.data.row_labels[-1]
    print(f"ultimo timestamp: {ultimo_timestamp}")

    forecast = resultado.get_forecast(steps=7)
    preds = forecast.predicted_mean
    conf_int = forecast.conf_int(alpha=0.05)

    timestamp_emissao = datetime.now()
    modelo = "ARIMA"
    versao_modelo = "1.0"
    estacao_id = estacao_id
    
    raiz = os.path.dirname(os.path.dirname(__file__))
    db_path = Path(raiz) / "dados" / "rio.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Inserir previsões no banco
    for timestamp_alvo, nivel_previsto_cm in preds.items():
        # Obter limites inferior e superior
        intervalo = conf_int.loc[timestamp_alvo]
        nivel_inf = float(intervalo[0])
        nivel_sup = float(intervalo[1])

        print(timestamp_alvo)

        cursor.execute("""
            INSERT INTO forecasts (
                estacao_id, timestamp_emissao, timestamp_alvo,
                nivel_previsto_cm, nivel_inf, nivel_sup, modelo, versao_modelo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            estacao_id,
            timestamp_emissao.strftime("%d/%m/%Y %H:%M"),
            timestamp_alvo.strftime("%d/%m/%Y %H:%M"),
            float(nivel_previsto_cm),
            nivel_inf,
            nivel_sup,
            modelo,
            versao_modelo
        ))

    conn.commit()
    conn.close()

insere_forecasts(arima_mon, estacao_id=1)
insere_forecasts(arima_jus, estacao_id=2)
