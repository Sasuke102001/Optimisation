"""
Run all M3-related DDL against M2 RDS, then create m3_app_user.
Run once, as polynovea_admin.
"""
import psycopg2
import os

M2 = dict(
    host="polynovea-module2.cxeo8066g8t2.ap-south-1.rds.amazonaws.com",
    port=5432,
    dbname="polynovea_module2",
    user="polynovea_admin",
    password="07586277012Luna",
    sslmode="require",
)

M3_APP_USER_PASSWORD = "M3app_PNv2026!"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
M3_FEEDBACK_SQL  = os.path.join(SCRIPT_DIR, "..",  "..",
    "..", "Acquistion System", "App", "backend", "db", "m3_feedback_tables.sql")
M3_FEED_SQL = os.path.join(SCRIPT_DIR, "m3_m2_feed_tables.sql")


def run_ddl(cur, filepath, label):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    # Strip commented-out blocks (lines starting with --)
    # but keep CREATE / INDEX statements
    lines = [l for l in raw.splitlines() if not l.strip().startswith("--")]
    sql = "\n".join(lines)
    cur.execute(sql)
    print(f"  {label} applied.")


def create_m3_app_user(cur, password):
    # Check if role already exists
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'm3_app_user'")
    if cur.fetchone():
        print("  m3_app_user already exists — skipping CREATE ROLE")
    else:
        cur.execute(f"CREATE ROLE m3_app_user WITH LOGIN PASSWORD %s", (password,))
        print(f"  Created role: m3_app_user")


def grant_permissions(cur):
    stmts = [
        "GRANT CONNECT ON DATABASE polynovea_module2 TO m3_app_user",
        "GRANT USAGE ON SCHEMA public TO m3_app_user",
        "GRANT SELECT ON ALL TABLES IN SCHEMA public TO m3_app_user",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO m3_app_user",
        # Write access — feedback tables
        "GRANT INSERT, UPDATE ON m3_segment_validation_feedback TO m3_app_user",
        "GRANT INSERT, UPDATE ON m3_venue_behavioral_outcomes    TO m3_app_user",
        "GRANT USAGE ON SEQUENCE m3_segment_validation_feedback_id_seq TO m3_app_user",
        "GRANT USAGE ON SEQUENCE m3_venue_behavioral_outcomes_id_seq    TO m3_app_user",
        # Write access — feed tables
        "GRANT INSERT, UPDATE ON m3_kpi_observations    TO m3_app_user",
        "GRANT INSERT, UPDATE ON m3_dwell_observations  TO m3_app_user",
        "GRANT INSERT, UPDATE ON m3_segment_table_log   TO m3_app_user",
        "GRANT USAGE ON SEQUENCE m3_kpi_observations_id_seq   TO m3_app_user",
        "GRANT USAGE ON SEQUENCE m3_dwell_observations_id_seq TO m3_app_user",
        "GRANT USAGE ON SEQUENCE m3_segment_table_log_id_seq  TO m3_app_user",
    ]
    for s in stmts:
        cur.execute(s)
    print("  All grants applied.")


def list_m3_tables(cur):
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE 'm3_%'
        ORDER BY table_name
    """)
    return [r[0] for r in cur.fetchall()]


def main():
    print("Connecting to M2 RDS...")
    conn = psycopg2.connect(**M2)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("\n[1/4] Running m3_feedback_tables.sql...")
        run_ddl(cur, M3_FEEDBACK_SQL, "m3_feedback_tables.sql")

        print("\n[2/4] Running m3_m2_feed_tables.sql...")
        run_ddl(cur, M3_FEED_SQL, "m3_m2_feed_tables.sql")

        conn.commit()
        print("\n  Tables committed.")

        print("\n[3/4] Creating m3_app_user role...")
        conn.autocommit = True   # role creation needs autocommit
        create_m3_app_user(cur, M3_APP_USER_PASSWORD)

        print("\n[4/4] Granting permissions...")
        grant_permissions(cur)

        conn.autocommit = False
        print("\nAll done. M3 tables on M2 RDS:")
        tables = list_m3_tables(cur)
        for t in tables:
            print(f"  {t}")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
