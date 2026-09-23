[← Workshop home](../README.md)

# Lab 2 · Govern & Trace

## Metadata-driven lakehouse — observability & traceability

**⏱ 60 min**  ·  **🎯 Focus:** #6 Data quality & traceability

### The story

In Lab 1 you built the Resident 360 medallion by hand. In production, HPB runs **hundreds** of such
loads across **many workspaces** — and needs to answer, at a glance: *did every load succeed? how many rows moved?
how long did it take? is the data consistent?* That's what a **metadata-driven lakehouse** gives you, arranged as a
**hub-and-spoke**: a central **hub** workspace (`HPB Metadata Framework`) holds the **control + audit database**
(`metadatadb`) and a **dashboard**; every **spoke** workspace (yours, and every other participant's) reports each load
into the hub. The hub **observes, monitors and audits** all the spokes from one place.

You won't build the framework from scratch (that's a facilitator preflight — see
`assets/PROVISIONING-RUNBOOK.md`). Instead you'll **connect your Lab 1 medallion (a spoke) to the hub** and watch your
own transform runs surface in the central governance dashboard alongside everyone else's.

### You'll do

- Read the hub's **control** table from your Lab 1 notebook to see how loads are config-driven.
- Add **one audit-hook cell** to your Lab 1 notebook so each run reports its metrics into the hub's `metadatadb`.
- Read the **audit** trail to see your own load on the record.
- Open the **Lakehouse Ingestion Dashboard** in the hub and read the observability + traceability story — your load
  appears next to the other spokes.

> **Why from the notebook?** The hub workspace is shared with you **read-only**, so its `metadatadb`
> query editor is disabled for participants. Instead you'll read `metadatadb` straight from **your own**
> Lab 1 notebook using a tiny helper — it runs with **your** identity, which has read access to the tables.
> This is also closer to how a real pipeline (a spoke) talks to the central control store.

### Where this fits — hub-and-spoke

```mermaid
flowchart TB
  subgraph HUB["Hub · HPB Metadata Framework workspace"]
    MDB["metadatadb<br/>mtd.ingest_control · mtd.ingest_audit"]
    DASH["Lakehouse Ingestion Dashboard<br/>observe · monitor · audit every spoke"]
    MDB --> DASH
  end
  subgraph S1["Spoke · your workspace · lh_resident360"]
    M1["bronze → silver → gold"] --> H1["audit-hook cell"]
  end
  subgraph S2["Spoke · another participant"]
    M2["bronze → silver → gold"] --> H2["audit-hook cell"]
  end
  H1 -->|run metrics| MDB
  H2 -->|run metrics| MDB
  classDef item fill:#cce5ff,stroke:#0066cc,stroke-width:2px,color:#003366;
  class MDB,DASH item;
  classDef done fill:#eeeeee,stroke:#999999,color:#333333;
  class M1,M2,H1,H2 done;
```

**Builds on:** the medallion from Lab 1. Your workspace is one **spoke**; the central **hub** sees them all (you see
your own rows filtered to your load).

### Files

These live **in the workshop kit you downloaded in Lab 0**, next to this README — the full path from the
folder the ZIP unzipped to (or that `git clone` created) is
`resident-360-data-workshop/lab2-metadata-lakehouse/assets/`. Open them in any text editor; on GitHub the
links below open them directly.

- [`assets/metadatadb-read-cell.py`](assets/metadatadb-read-cell.py) — a small helper cell that lets you read
  `metadatadb` from your notebook (defines `q("SELECT ...")`). You paste this in **Task 1**.
- [`assets/audit-hook-cell.py`](assets/audit-hook-cell.py) — the cell you paste at the end of your Lab 1
  notebook to report your load into `metadatadb`. You paste this in **Task 2**.
- `assets/PROVISIONING-RUNBOOK.md` — public placeholder explaining that private facilitator deployment
  instructions and artifacts are intentionally excluded from this participant repository.

> **New to Fabric?** Each step is small and self-contained — follow them in order.

---

### Task 1 — See the framework's brain: the control table

The framework is driven by a config table — no hard-coded pipelines. You'll read it from **your own**
Lab 1 notebook.

1. Go to **your** workspace and open your **Lab 1 medallion notebook** (`resident360_medallion`).
2. **Add a new cell** (anywhere after the first setup cell). Open
   [`lab2-metadata-lakehouse/assets/metadatadb-read-cell.py`](assets/metadatadb-read-cell.py) **from the kit
   folder you downloaded in Lab 0**, copy its full contents, and paste them in.
3. Check the two values at the top — `SQL_SERVER` and `SQL_DB` — match the facilitator's `metadatadb`.
   The public kit keeps placeholders; the facilitator gives you the two live values during the workshop.
4. **Run that cell.** You should see `✅ metadatadb reader ready`.
5. **Add another new cell** and run this read:

   ```python
   q("""
   SELECT source_schema_name, source_table_name, load_type, target_object, enable_flag
   FROM mtd.ingest_control
   ORDER BY source_schema_name, source_table_name
   """)
   ```

6. Notice the rows describe **your** medallion tables — `bronze.h365_*`, `silver.fact_*`, `gold.resident_360` —
   each with its **load type** (Full / Incr) and **target**. This config *is* the framework: add a row, and
   a new table is governed. No code change.

![Reading the mtd.ingest_control table from the notebook — control rows mapping bronze, silver and gold tables to gold.resident_360.](../docs/images/lab2/lab2-02-read-control.png)

> **Done when you see:** control rows naming your bronze / silver / gold tables. The exact number of rows depends on
> the facilitator's current hub configuration.

---

### Task 2 — Connect your Lab 1 notebook to the audit store

Now make your transform **report** each run into the framework.

1. Go back to **your** workspace and open your **Lab 1 medallion notebook** (`resident360_medallion`).
2. **Add a new cell at the very end.**
3. Open [`lab2-metadata-lakehouse/assets/audit-hook-cell.py`](assets/audit-hook-cell.py) from the same kit
   folder, copy its full contents, and paste them into that cell.
4. Confirm the `SQL_SERVER` and `SQL_DB` values at the top match the facilitator's `metadatadb`
   — these are the **same two values** you used for the reader cell in Task 1.
5. **Run only that cell.**

   ![The audit-hook cell at the end of the notebook, printing the actual per-table audit status after counting each table.](../docs/images/lab2/lab2-05-audit-hook.png)

> **Done when you see:** `✅ Audit hook completed ...` with all listed tables counted. The hook writes one
> audit row per table it tries to count. A single `Failed` row for a table that genuinely does not exist yet
> means the hook is working correctly — it reports what it cannot count instead of crashing. Do not edit the
> hook to "fix" that row; finish Lab 1 and rerun. If every table fails, or you see a ⚠️ skip message, tell
> the facilitator — your Lab 1 tables are not changed by the hook.

---

### Task 3 — Read the audit trail

1. Back in your notebook, **add a new cell** and run this read (uses the same `q()` helper from Task 1):

   ```python
   q("""
   SELECT TOP 20 item_name, load_type, rows_written, status,
          copy_duration AS seconds, event_end_time
   FROM mtd.ingest_audit
   ORDER BY event_end_time DESC
   """)
   ```

2. Each row is one **traceable** load event: which table, how many rows, success/failure, how long, and when.
3. Find the row for **`gold.resident_360`** — that's your unified view's load, now on the record.

   > **Why `TOP 20`?** `mtd.ingest_audit` is the *hub's* table — it collects load events from every
   > spoke in the room, so it holds hundreds of rows. Newest-first ordering plus `TOP 20` puts the rows
   > your audit hook just wrote right at the top. To narrow it to your own load alone, take the short run
   > id your hook printed (`✅ Audit hook completed (run abc12345)`) and add
   > `WHERE event_run_id LIKE 'abc12345%'`.

![Reading the mtd.ingest_audit table from the notebook — your latest run tops the list with gold.resident_360 at 1500 rows and the status reported by the audit hook.](../docs/images/lab2/lab2-03-read-audit.png)

> **Done when you see:** an audit row for `gold.resident_360` with your row count and the actual status reported by
> the hook.

---

### Task 4 — Open the hub's observability dashboard

1. In the central **`HPB Metadata Framework`** hub workspace, open the **Lakehouse Ingestion Dashboard**.
2. Read the tiles: **rows / data ingested by layer**, **success vs. failure**, **load duration**, **runs over time** — the hub aggregates every spoke's loads here.
3. Filter to **`gold.resident_360`** (or your run) — the dashboard now tells the operational story of the
   medallion **you** built (your spoke): what moved, whether it was consistent, and how long it took.

![Lakehouse Ingestion Dashboard — datasets ingested, success rate, rows written, and a per-layer audit grid showing your bronze/silver/gold loads](../docs/images/lab2/lab2-01-dashboard.png)

> **Done when you see:** your `gold.resident_360` load reflected in the dashboard tiles.

> **Tiles blank or showing an error?** The dashboard reads `metadatadb` through its semantic model, which needs its
> **data-source credentials bound once** by the facilitator (Fabric SQL is Entra-auth only). If every visual shows
> *"can't connect to the data source"* / *"capacity or license issue,"* tell the facilitator — they re-bind the
> model credential. Your audit rows are still safely in `metadatadb` (you just read them in Task 3), so the
> tiles fill in as soon as the connection is fixed.

---

### Task 5 — Trace it end-to-end

1. In **your own** workspace (`HPB Resident 360 (<your username>)`), switch to **Lineage view** (top-right toggle, next to
   the search box).
2. Follow **your spoke's** chain end-to-end: **`hpb_databricks_mirror` ← the Azure Databricks source**, and
   **`lh_resident360` → its SQL endpoint → `sm_resident360` → `rpt_resident360`** — with the `resident360_medallion`
   notebook feeding the Lakehouse. *(The central hub has its own governance lineage — dashboard → semantic model →
   `metadatadb` — if you want to peek there too.)*
3. This is **traceability**: from the report back to the raw Databricks source, and — via the audit table —
   *when* each hop last ran and whether it succeeded.

![Lineage view of your own workspace — the mirrored Databricks catalog, lh_resident360 Lakehouse and SQL endpoint, sm_resident360 semantic model, rpt_resident360 report, and the medallion notebook.](../docs/images/lab2/lab2-04-lineage.png)

> **Done when you see:** the lineage graph linking the dashboard to `metadatadb`, and your medallion back to the mirror.

---

### ✅ Checkpoint

- [ ] Found your tables in `mtd.ingest_control`
- [ ] Added the audit-hook cell and got `✅ Audit hook completed ...` with actual per-table statuses
- [ ] Read your load in `mtd.ingest_audit`
- [ ] Saw your `gold.resident_360` load in the Ingestion Dashboard
- [ ] Traced lineage from the dashboard back to your medallion

---

### Next up

**[Lab 3 · Nudges That Land →](../lab3-datascience-ml/README.md)**
