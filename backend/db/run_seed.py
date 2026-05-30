import psycopg2
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
seed_file = os.path.join(script_dir, "seed_kpi_families.sql")

conn = psycopg2.connect(
    host="polynovea-m3.postgres.database.azure.com",
    port=5432,
    user="subrojitroy",
    password="07586277012Luna",
    dbname="polynovea_m3",
    sslmode="require"
)
conn.autocommit = False

with open(seed_file, "r", encoding="utf-8") as f:
    sql = f.read()

try:
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("seed_kpi_families.sql applied successfully.")
    
    cur.execute("SELECT slug, label FROM m3_kpi_families ORDER BY id")
    families = cur.fetchall()
    print(f"Families in m3_kpi_families ({len(families)}):")
    for slug, label in families:
        print(f"  {slug} -> {label}")
        
    cur.execute("SELECT family_id, slug, label FROM m3_kpi_signals ORDER BY family_id, id")
    signals = cur.fetchall()
    print(f"Signals in m3_kpi_signals ({len(signals)}):")
    for fam_id, slug, label in signals:
        print(f"  [Fam {fam_id}] {slug} -> {label}")
        
    cur.close()
except Exception as e:
    conn.rollback()
    print(f"ERROR: {e}")
    raise
finally:
    conn.close()
