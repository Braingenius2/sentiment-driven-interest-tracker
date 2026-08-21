# Labeling Aid (Day 4)

This is a working aid for the manual labeling session. It contains the rubric, decision rules, and worked examples from the actual data. It does not contain suggested labels — every judgment in `data/clean/articles_to_label.csv` must be yours.

## Rubric (from implementation_file.md)

- **positive** — falling prices, improved affordability, successful relief, increased supply, or another clearly favourable development for households.
- **negative** — rising prices, unaffordability, scarcity, worsening hardship, or another clearly unfavourable development for households.
- **neutral** — factual reporting without a clear positive or negative tone.

Fill all three columns for every row:

- `sentiment_label`: `positive` / `neutral` / `negative` (lowercase)
- `label_reason`: one short sentence (5–10 words)
- `confidence`: `high` / `medium` / `low`

## Decision rules (use these to move fast)

| Pattern | Rule |
|---|---|
| Prices rising / scarcity / hardship / borrowing to eat | negative |
| Prices falling / relief / intervention succeeding / supply improving | positive |
| Factual statistic reported without valence words | neutral |
| Policy meetings, calls on government to act, warnings issued | neutral unless hardship language dominates |
| "**Slows** / moderates / eases" (rate decelerating, prices still rising) | neutral — deceleration is not falling prices |
| Intervention announced (distribution, subsidies) | neutral if prospective; positive only if framed as delivered relief |
| Peripheral cost-of-living (housing, wages, fuel, electricity) | judge by tone toward household welfare |
| Same event, multiple outlets | label each headline independently on its own words |

## Worked examples from this dataset

- Row 1 — "inflation **rises** to 15.69% … food prices remain **elevated**" → negative (headline CPI metric).
- Row 2 — "food inflation rate **continues on a steady rise** to 16.06%" → negative (food sub-index metric; different indicator, same release — both correct).
- Row 3 — "food inflation **slows** to 16.06%" → the deceleration case: still rising, slower rate → neutral (or negative with low confidence if hardship-framed). Record your reasoning either way; this becomes a star example in the Day-5 error analysis.

## Workflow

1. Work in batches of 25–30 rows. Do not reorder rows or touch columns A–E; the validator joins on `row_id`.
2. Expect imbalance — price-rise coverage dominates, so `negative` will likely lead. Do not force balance; the imbalance is documented on Day 5.
3. When genuinely torn, pick the least-wrong label, set `confidence` to `low`, and say why in `label_reason`. Ambiguous-but-recorded beats forced-and-fake.
4. Save as CSV (never .xlsx). In Excel use Data → From Text/CSV with UTF-8 encoding; in Google Sheets use File → Import, then Download → CSV.
5. Run `notebooks/day4_labeling.ipynb` — it validates all 111 rows and writes `data/clean/articles_labeled.csv`.
