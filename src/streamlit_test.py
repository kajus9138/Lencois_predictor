import streamlit as st
import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt



base_dir = os.path.dirname(__file__)
db_path = os.path.join(base_dir, "../dados/rio.db")
print(db_path)

DB_PATH = db_path
TABELA = "medicoes"
COL_TEMPO = "timestamp"
COL_VALOR = "nivel_cm"

# Janela de tempo da série
DATA_INICIO = "2025-09-10 00:00:00"
DATA_FIM = "2025-09-16 00:00:00"

## Conectar e consultar banco
conn = sqlite3.connect(DB_PATH)
query = f"""

    SELECT {COL_TEMPO}, {COL_VALOR}
    FROM "{TABELA}"
    WHERE {COL_TEMPO} BETWEEN '{DATA_INICIO}' AND '{DATA_FIM}'
    ORDER BY {COL_TEMPO}

"""

df = pd.read_sql_query(query, conn, parse_dates=[COL_TEMPO])
conn.close()

df.set_index(COL_TEMPO, inplace=True)
df_diario = df.resample('D').max()

fig, ax = plt.subplots(figsize=(10,5))

ax.plot(df_diario.index, df_diario[COL_VALOR], marker='o')
ax.set_title("Máxima diária do nível do rio")
ax.set_xlabel("Data")
ax.set_ylabel("Nível (cm)")

ax.set_xlim(pd.Timestamp(DATA_INICIO), pd.Timestamp(DATA_FIM))
ax.set_ylim(df_diario[COL_VALOR].min() - 10 , df_diario[COL_VALOR].max() + 10)
ax.grid(True)

st.title("Monitoramento Rio Lençóis")

st.write("Série semanal")

st.pyplot(fig)

st.write("Série futura")
st.pyplot(fig)

