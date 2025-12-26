import sqlite3
import os

# Path to your database
db_path = 'database.db'

# Path to schema.sql
schema_path = os.path.join(r'D:\Sanguine\Downloads\multi-disease-prediction2\multi-disease-prediction-main', 'schema.sql')

# Connect to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Read and execute schema
with open(schema_path, 'r') as f:
    sql_script = f.read()

cursor.executescript(sql_script)
conn.commit()
conn.close()

print("Database initialized successfully!")
