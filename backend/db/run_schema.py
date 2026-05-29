import psycopg2
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
schema_file = os.path.join(script_dir, "m3_schema.sql")

conn = psycopg2.connect(
    host="polynovea-m3.postgres.database.azure.com",
    port=5432,
    user="subrojitroy",
    password="07586277012Luna",
    dbname="polynovea_m3",
    sslmode="require"
)
conn.autocommit = False

with open(schema_file, "r", encoding="utf-8") as f:
    sql = f.read()

try:
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("m3_schema.sql applied successfully.")
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables in polynovea_m3 ({len(tables)}):")
    for t in tables:
        print(f"  {t}")
    cur.close()
except Exception as e:
    conn.rollback()
    print(f"ERROR: {e}")
    raise
finally:
    conn.close()
