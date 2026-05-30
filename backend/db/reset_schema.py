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

DROP_SQL = """
DROP TABLE IF EXISTS
    m3_segment_validation_log,
    m3_customer_survey_responses,
    m3_se_feedback,
    m3_se_triggers,
    m3_se_suggestions,
    m3_show_plans,
    m3_session_states,
    m3_intervention_log,
    m3_kpi_signal_readings,
    m3_kpi_assessments,
    m3_interventions,
    m3_kpi_signals,
    m3_kpi_families,
    m3_behavioral_states,
    m3_sessions,
    m3_venues
CASCADE;
"""

try:
    cur = conn.cursor()

    print("Dropping all m3_ tables...")
    cur.execute(DROP_SQL)
    conn.commit()
    print("  Done.")

    print("Applying m3_schema.sql...")
    with open(schema_file, "r", encoding="utf-8") as f:
        sql = f.read()
    cur.execute(sql)
    conn.commit()
    print("  Done.")

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    print(f"\nTables in polynovea_m3 ({len(tables)}):")
    for t in tables:
        print(f"  {t}")

    cur.close()
except Exception as e:
    conn.rollback()
    print(f"ERROR: {e}")
    raise
finally:
    conn.close()
