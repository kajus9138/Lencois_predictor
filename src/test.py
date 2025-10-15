import sqlite3
import pandas as pd


conn = sqlite3.connect("rio.db")
print(pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn))
conn.close()
