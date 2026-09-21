# ─────────────────────────────────────────────────────────────────────────────
# Lab 2 metadatadb reader — paste this as a NEW cell in your Lab 1 medallion
# notebook (it runs with YOUR identity, so it works even though the framework
# workspace is shared with you read-only).
#
# It defines one helper, q("SELECT ..."), that runs a read-only query against the
# framework's metadatadb and shows the result as a table. You'll use it in Task 1
# and Task 3 to read the control and audit tables — no portal query editor needed.
#
# Your facilitator gives you the two connection values below during Lab 2
# (the same two values as the audit-hook cell). Live tenant and workspace
# coordinates are intentionally not published in this public repo.
# ─────────────────────────────────────────────────────────────────────────────
import struct, pandas as pd

# ── "HPB Metadata Framework" metadatadb connection ────
SQL_SERVER = "<SQL_SERVER>"   # e.g. xxxx.database.fabric.microsoft.com
SQL_DB     = "<SQL_DB>"       # e.g. metadatadb-<guid>

def q(sql: str):
    """Run a read-only query against the framework's metadatadb and return a DataFrame."""
    import pyodbc, warnings
    from notebookutils import credentials

    # Entra token for the Fabric SQL DB (Fabric SQL is Entra-auth only)
    token = credentials.getToken("https://database.windows.net/").encode("utf-16-le")
    tokenstruct = struct.pack(f"<I{len(token)}s", len(token), token)
    SQL_COPT_SS_ACCESS_TOKEN = 1256

    conn = pyodbc.connect(
        f"Driver={{ODBC Driver 18 for SQL Server}};Server={SQL_SERVER},1433;"
        f"Database={SQL_DB};Encrypt=yes;TrustServerCertificate=no",
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: tokenstruct},
    )
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # hide pandas' benign "SQLAlchemy only" notice
            df = pd.read_sql(sql, conn)
    finally:
        conn.close()
    return df

print("✅ metadatadb reader ready — call q(\"SELECT ...\") in the next cells.")
