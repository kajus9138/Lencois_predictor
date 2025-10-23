import sqlite3
import pandas as pd
from pathlib import Path

raiz = Path.cwd()  # diretório onde você rodou o streamlit
db_path = raiz / "dados" / "rio.db"

conn = sqlite3.connect(db_path)
print(pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn))
conn.close()
