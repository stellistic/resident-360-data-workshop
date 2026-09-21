# ─────────────────────────────────────────────────────────────────────────────
# Lab 2 audit hook — paste this as the LAST cell of Lab 1's medallion notebook.
#
# It writes ONE audit row per layer into the metadata framework's `metadatadb`
# by calling mtd.capture_audit_event_sp. After this runs, your `gold.resident_360`
# load shows up in the Lakehouse Ingestion Dashboard (Lab 2) — that's the
# observability + traceability outcome, over the medallion YOU just built.
#
# It is wrapped in try/except so it cannot change your Lab 1 tables — if the
# metadatadb isn't reachable, it prints a warning and moves on. Per-table status
# is based on actual row-count checks; missing tables are reported as Failed,
# never as Success.
#
# Your facilitator gives you the two connection values below during Lab 2.
# Live tenant and workspace coordinates are intentionally not published in
# this public repo.
# ─────────────────────────────────────────────────────────────────────────────
import uuid, datetime

# ── "HPB Metadata Framework" metadatadb connection ────
SQL_SERVER = "<SQL_SERVER>"   # e.g. xxxx.database.fabric.microsoft.com
SQL_DB     = "<SQL_DB>"       # e.g. metadatadb-<guid>

def _emit_audit():
    import struct, pyodbc
    from notebookutils import credentials

    # Entra token for the Fabric SQL DB (Fabric SQL is Entra-auth only).
    token = credentials.getToken("https://database.windows.net/").encode("utf-16-le")
    tokenstruct = struct.pack(f"<I{len(token)}s", len(token), token)
    SQL_COPT_SS_ACCESS_TOKEN = 1256

    conn = pyodbc.connect(
        f"Driver={{ODBC Driver 18 for SQL Server}};Server={SQL_SERVER},1433;"
        f"Database={SQL_DB};Encrypt=yes;TrustServerCertificate=no",
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: tokenstruct},
    )
    cur = conn.cursor()

    # One row per important table this notebook produced. rows_* are counted live.
    # data_read/data_written are byte estimates (row_count * 100) so dashboard sizes
    # remain illustrative rather than pretending to be measured file sizes.
    layers = [
        ("bronze.h365_residents_reference", "bronze.h365_residents_reference", "Full"),
        ("bronze.h365_meal_logs",           "bronze.h365_meal_logs",           "Full"),
        ("bronze.h365_event_bookings",      "bronze.h365_event_bookings",      "Full"),
        ("bronze.h365_programme_enrolments","bronze.h365_programme_enrolments","Full"),
        ("bronze.h365_rewards",             "bronze.h365_rewards",             "Full"),
        ("bronze.h365_evoucher_redemptions","bronze.h365_evoucher_redemptions","Full"),
        ("bronze.h365_challenges",          "bronze.h365_challenges",          "Full"),
        ("bronze.env_air_quality",          "bronze.env_air_quality",          "Full"),
        ("silver.fact_meal_log",            "silver.fact_meal_log",            "Incr"),
        ("silver.fact_event_attendance",    "silver.fact_event_attendance",    "Incr"),
        ("silver.dim_event_occurrence",     "silver.dim_event_occurrence",     "Incr"),
        ("silver.map_resident_event_attendance", "silver.map_resident_event_attendance", "Incr"),
        ("silver.fact_programme_enrolment", "silver.fact_programme_enrolment", "Incr"),
        ("silver.fact_rewards",             "silver.fact_rewards",             "Incr"),
        ("silver.fact_evoucher_redemption", "silver.fact_evoucher_redemption", "Incr"),
        ("silver.fact_challenge",           "silver.fact_challenge",           "Incr"),
        ("gold.resident_360",               "gold.resident_360",               "Full"),
    ]
    run_id = str(uuid.uuid4())
    statuses = []
    for item_name, table, load_type in layers:
        start = datetime.datetime.utcnow()
        try:
            n = spark.table(f"lh_resident360.{table}").count()
            status = "Success"
            verification = "Verified by table count"
        except Exception as e:
            n = 0
            status = "Failed"
            verification = f"Not verified: count failed ({str(e)[:120]})"
        end = datetime.datetime.utcnow()
        approx_bytes = n * 100
        duration = max(0, int((end - start).total_seconds()))
        cur.execute(
            "EXEC mtd.capture_audit_event_sp "
            "@source_type=?, @event_run_id=?, @item_name=?, @data_read=?, @data_written=?, "
            "@rows_read=?, @rows_written=?, @data_consistency_verification=?, @copy_duration=?, "
            "@event_start_time=?, @event_end_time=?, @load_type=?, @status=?, "
            "@event_triggered_by=?, @pipeline_url=?",
            "FABRIC_LAKEHOUSE", run_id, item_name, approx_bytes, approx_bytes,
            n, n, verification, duration, start, end, load_type, status,
            "Lab1 Notebook", "https://app.fabric.microsoft.com",
        )
        statuses.append((item_name, status, n))
    conn.commit()
    cur.close(); conn.close()

    ok = sum(1 for _, status, _ in statuses if status == "Success")
    failed = [name for name, status, _ in statuses if status != "Success"]
    print(f"✅ Audit hook completed (run {run_id[:8]}): {ok}/{len(statuses)} tables counted successfully.")
    for name, status, n in statuses:
        print(f"  {status:7s} {name:42s} rows={n}")
    if failed:
        print("⚠️ Some audit rows were recorded as Failed because the table count could not be verified:", failed)
    else:
        print("Open the Lakehouse Ingestion Dashboard in Lab 2 to see your load.")

try:
    _emit_audit()
except Exception as e:
    print(f"⚠️ Audit hook skipped (metadatadb not reachable from this notebook): {e}")
    print("   This does NOT affect your Lab 1 tables — no audit status was written.")
