[← Lab 1](../README.md)

# Lab 1 · Semantic model catch-up prompts

Use these if you are behind on **Task 3**, or not sure how much of `sm_resident360` you have already built.
They take you through **3b (relationships)** and **3c (measures)** with **Copilot**, from wherever you are.

Each prompt tells Copilot to **check the model first**, then create only what is missing and fix only what is
different. That makes them safe to run at any stage — even if you have already done part of 3b or 3c by hand — and
safe to run again if a prompt only half-applies.

> 💡 **Why five prompts and not one?** Copilot works more reliably with one focused job per prompt than with a long
> list of mixed changes. Short prompts also let you check each step before the next one depends on it: the measures
> only return the right numbers once the relationships are right.

---

### Before you start

1. Open **`sm_resident360`** from your workspace list. It opens in **Model view**, in **Viewing** mode.
2. Switch to **Editing**: click **Viewing** on the ribbon (top-left) → **Editing**. *(The whole ribbon, Copilot
   included, is greyed out in Viewing mode.)*
3. Click **Copilot** on the ribbon. The first time, Copilot asks for permission to review and change the model —
   allow it. Copilot then saves a restore point in the model's **version history**, so you can undo everything this
   chat session changes.
4. Paste the prompts **one at a time, in order**. Let each one finish and do its **Check** before you paste the next.
   If Copilot asks you to confirm or apply its changes, confirm them.

---

### Prompt 1 — Take stock (no changes)

```text
Do not change anything yet. Describe the current state of this semantic model in three short lists:
1. Tables: the name of every table.
2. Relationships: for each one, the from table and column, the to table and column, the cardinality,
   the cross-filter direction, and whether it is active.
3. Measures: for each one, the table it is on, its name, its DAX expression and its format string.
```

**Check:** the tables list shows all six — `resident_360`, `fact_event_attendance`, `fact_meal_log`,
`fact_rewards`, `fact_programme_enrolment`, `fact_challenge`. These prompts do not add tables, so if one is
missing, go back to [3a](../README.md#3a--create-the-model) (or ask a facilitator) before carrying on. Whatever the
relationship and measure lists show is fine — the next prompts sort them out.

---

### Prompt 2 — Relationships (3b)

```text
Make the relationships in this semantic model match this spec exactly. Keep any relationship that already
matches, fix any that differ, and create any that are missing.

There must be exactly five relationships, each from a fact table to resident_360, joined on resident_id:
1. fact_event_attendance[resident_id] -> resident_360[resident_id]
2. fact_meal_log[resident_id] -> resident_360[resident_id]
3. fact_rewards[resident_id] -> resident_360[resident_id]
4. fact_programme_enrolment[resident_id] -> resident_360[resident_id]
5. fact_challenge[resident_id] -> resident_360[resident_id]

Every one must be many-to-one (*:1, with the fact table on the many side), cross-filter direction Single,
and active. Delete any other relationship, including duplicates and any relationship between two fact
tables. Do not change any tables, columns or measures.
```

**Check:** on the ribbon open **Manage relationships**. There are **exactly five** rows, each `*:1`, **Single**,
**Active** and joined on `resident_id`. The most common miss is a relationship in the wrong direction (`1:*`
instead of `*:1`). Run Prompt 2 again, or fix that row by hand in the dialog.

---

### Prompt 3 — Core measures (3c, part 1)

```text
Make sure these three measures exist on the resident_360 table, with exactly these names, DAX expressions
and format strings. If a measure with one of these names is on another table, move it to resident_360.
If one already exists with a different expression or format string, update it. Create any that are
missing. Do not change anything else.

Residents              = COUNTROWS('resident_360')                                                 format #,0
Disengaged Residents   = CALCULATE(COUNTROWS('resident_360'), 'resident_360'[is_disengaged] = 1)  format #,0
Disengagement Rate     = DIVIDE([Disengaged Residents], [Residents])                              format 0.0%
```

**Check:** in the **Data** pane, expand `resident_360`. `Residents`, `Disengaged Residents` and
`Disengagement Rate` are listed with the calculator icon.

---

### Prompt 4 — Remaining eight measures (3c, part 2)

```text
Make sure these eight measures exist on the resident_360 table, with exactly these names, DAX expressions
and format strings. If a measure with one of these names is on another table, move it to resident_360.
If one already exists with a different expression or format string, update it. Create any that are
missing. Do not change anything else.

Avg Daily Steps          = AVERAGE('resident_360'[avg_daily_steps])                                                 format #,0
Avg MVPA Minutes         = AVERAGE('resident_360'[avg_mvpa_min])                                                    format #,0.0
Events Attended          = SUM('resident_360'[events_attended])                                                     format #,0
Programmes Dropped       = SUM('resident_360'[programmes_dropped])                                                  format #,0
Healthpoints Earned      = SUM('resident_360'[healthpoints_earned])                                                 format #,0
Meals Logged             = COUNTROWS('fact_meal_log')                                                               format #,0
Avg Region PSI           = AVERAGE('resident_360'[region_psi])                                                      format #,0
Not Screened Residents   = CALCULATE(COUNTROWS('resident_360'), 'resident_360'[screening_risk] = "Not Screened")   format #,0
```

**Check:** `resident_360` now shows **all 11** measures from the [3c table](../README.md#3c--add-the-core-measures),
and none of those names appear on any other table.

---

### Prompt 5 — Sanity check (no changes)

```text
Do not change anything. Run these two DAX queries against this semantic model and show me the results:
1. One row with the values of Residents, Disengaged Residents, Disengagement Rate and Not Screened Residents.
2. Meals Logged for each value of resident_360[region], plus the grand total.
```

**Check:** compare Copilot's results with this table.

| Measure | Expected |
|---|---|
| `Residents` | **1,500** |
| `Disengaged Residents` | about **182** |
| `Disengagement Rate` | about **12.1%** |
| `Not Screened Residents` | **419** |
| `Meals Logged` — grand total | **20,481** |
| `Meals Logged` — by region | a **different** number for each region, adding up to 20,481 |

- **Every region shows 20,481?** A region filter on `resident_360` is not reaching `fact_meal_log`, so the
  `fact_meal_log` relationship is missing or points the wrong way. Go back to Prompt 2.
- **`Residents` is not 1,500?** The gold table is short. Re-check the Task 2 notebook run, not the model.
- **Another value is off?** Open that measure and compare its DAX and format with the
  [3c table](../README.md#3c--add-the-core-measures), or run Prompt 3 or 4 again.

If Copilot can't run the queries, switch the model to **DAX query** view, paste this, and run it:

```dax
EVALUATE
ROW(
    "Residents", [Residents],
    "Disengaged Residents", [Disengaged Residents],
    "Disengagement Rate", [Disengagement Rate],
    "Not Screened Residents", [Not Screened Residents],
    "Meals Logged", [Meals Logged]
)

EVALUATE
SUMMARIZECOLUMNS('resident_360'[region], "Meals Logged", [Meals Logged])
```

---

### If something goes wrong

- **A prompt only half-applied, or Copilot stopped part-way.** Paste the same prompt again. Each one checks first, so
  re-running it only fills the gaps.
- **Copilot changed something it shouldn't have.** Restore the checkpoint Copilot saved at the start of the chat
  session from the model's **version history**, then start again from Prompt 1.
- **Copilot is not available, or keeps failing.** Build the rest by hand using the steps in
  [3b](../README.md#3b--add-the-star-relationships) and [3c](../README.md#3c--add-the-core-measures). The first three
  measures are enough to carry on to Task 4.

When Prompt 5 checks out, carry on to [Task 4 — Let Copilot build the report](../README.md#task-4--let-copilot-build-the-report).
