import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(
    host="polynovea-m3.postgres.database.azure.com",
    port=5432,
    user="subrojitroy",
    password="07586277012Luna",
    dbname="postgres",
    sslmode="require"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname = 'polynovea_m3'")
exists = cur.fetchone()

if exists:
    print("Database polynovea_m3 already exists — skipping CREATE")
else:
    cur.execute("CREATE DATABASE polynovea_m3")
    print("Created database: polynovea_m3")

cur.close()
conn.close()
print("Done.")
