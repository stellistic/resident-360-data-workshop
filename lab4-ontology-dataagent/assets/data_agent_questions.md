# Lab 4 · Data agent — instructions & question bank

## Agent instructions (paste into the data agent → Setup → Agent instructions)
```
You are the HPB Resident 360 assistant. Use HPB terminology:
- "MVPA" = moderate-to-vigorous physical activity minutes.
- "Healthpoints" = the Healthy 365 rewards currency; eVouchers are redeemed with them.
- A resident is "disengaged" when is_disengaged = 1 (low steps AND no events attended AND a dropped programme).
- "hazy" / poor-air region = region_is_hazy = 1 (regional 24-hour PSI >= 55). PSI is a regional haze-context proxy, not individual exposure.
- Event questions use occurrence grain (`event_occurrence_id`). The ontology `attended` edge maps only actual attended rows from `silver.map_resident_event_attendance`; `event_id` alone is not unique by date/region.
Prefer the ontology for resident-level and relationship questions; use the semantic models for aggregated metrics.
When comparing groups, return a chart. Never expose individual resident_ids — report by region, age band,
programme, event or challenge.
```

## Question bank

### Multi-hop relationship questions (Resident · Programme · EventOccurrence · Region)
These span several domains. **Both** agents attempt them over the same governed medallion data — the point
is to compare *how* each does it (star joins vs. named-relationship traversal). Validate the figures shown by the
agents in your run; the ontology agent is preview and may not reproduce the semantic-model breakdown exactly.
1. **Among residents who dropped a programme, how many attended at least one event, broken down by the region where those events were held? Return a chart by region.**  *(the headline comparison — spans enrolledIn + attended + heldIn)*
2. How many residents attended events in each region? Return a chart by region.
3. On average, how many events does a resident attend, broken down by their home region?

> ⚠️ **"region" is ambiguous, and the data makes it bite** — it appears as a resident's *home* region (`livesIn`)
> and an event's *held-in* region (`heldIn`). **About 18% of attended events are held outside the resident's home
> region** (501 of 2,721), so the two readings return genuinely different numbers. Phrase the question so the
> intended hop is explicit. The ontology's named edges disambiguate it structurally; the flat model relies on the
> agent picking the right `region` column, and there are two of them (`resident_360[region]` and
> `fact_event_attendance[region]`).
>
> This is the single best reason to run the comparison. Ask Q1 of both agents and check *which* region each one
> used — that difference, not a difference in arithmetic, is the point of Lab 4.

### Engagement & risk
4. Which regions have the highest share of disengaged residents?
5. How many residents are disengaged by age band?
6. Compare average daily steps for residents who attended ≥1 event vs those who attended none.

### Diet, rewards & screening
7. What is the % Healthier Choice for residents at High screening risk vs Low?
8. Average calories logged per meal type.
9. Healthpoints earned by programme, and eVoucher value redeemed by region.

### Programmes & challenges
10. Which programmes do disengaged residents in the East most often drop?
11. Which regions have the most residents enrolled in "Eat Drink Shop Healthy" but with low challenge progress?
12. Which challenges have the highest completion, and in which regions?

## Compare the two agents (the point of Task 5)
Ask **Q1** to **both** the **`Resident360 SM Agent`** (on `sm_resident360`) and the **`Resident360 Ontology Agent`**
(on `resident_ontology`). Both read the same governed medallion data, so the comparison is about *how* each answers — not a promise
of identical numbers. Validate the semantic-model query/chart produced in your run, then compare the ontology agent
(preview), which demonstrates named-relationship traversal but may return different figures on this multi-hop aggregate.
The difference is *architectural*: the SM agent joins the star on `resident_id`; the ontology agent traverses named
relationships (`enrolledIn`, `attended`, `heldIn`) at event occurrence grain. Discuss when each fits:
- **Semantic model** — classic BI metrics, dashboards, well-understood star schemas.
- **Ontology** — named/typed relationships, deep or variable-length multi-hop traversal, and a governed layer reused
  across many agents and apps.
