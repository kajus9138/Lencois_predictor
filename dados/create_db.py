import sqlite3
from pathlib import Path

db_path = Path("dados") / "rio.db"
db_path.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS estacoes(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               estacao TEXT NOT NULL,
               rio TEXT NOT NULL)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS medicoes(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               estacao_id INTEGER NOT NULL,
               timestamp DATETIME NOT NULL,
               nivel_cm REAL,
               vazao_m3_s REAL,
               precipitacao_mm REAL,
               FOREIGN KEY (estacao_id) REFERENCES estacoes(id))
""")

conn.commit()
conn.close()
