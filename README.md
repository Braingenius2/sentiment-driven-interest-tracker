# Sentiment-Driven Interest Tracker: Nigerian Food Prices and Cost of Living

**Brief:** DS-20 — Sentiment-Driven Interest Tracker (3MTT Data Science capstone)
**Participant:** Fortune Uzodinma
**Demo video (2–3 min):** [Watch on Loom](https://www.loom.com/share/43d676bdc2364beb9bd2df42762e74dd)

## What this project does

Tracks how Nigerian online news attention to **food prices and the cost of living** changed over a three-month window (15 May – 11 August 2026), and how the sentiment of that coverage shifted week by week.

**Research question:** How has Nigerian online news attention to food prices and cost of living changed over the most recent available period, and how has the tone of that coverage (positive, neutral, negative) shifted over the same time?

**What this project does *not* measure:** actual food prices, household purchasing behaviour, public opinion, or search interest. It tracks online news coverage only — and volume figures are a Google News feed sample, not a complete record of all coverage. No causal claims are made.

## Data

- **Source:** Google News RSS search feeds (one service, seven closely related queries: Nigeria food prices / food inflation / cost of living / rice prices / food affordability / staple food prices / purchasing power food).
- **Why this source:** GDELT DOC 2.0 was tested first and was persistently unavailable (HTTP 429 rate limits and read timeouts). The contingency source was selected and documented; see `references/day1_feasibility_notes.md`.
- **Collection:** 14 August 2026 (UTC timestamp recorded in `data/raw/collection_metadata.json`).
- **Volume:** 676 raw feed items → 517 after deduplication → 185 within the three-month window → **111 frozen records** across 51 distinct source labels.
- **Filter rule:** a headline is kept if it contains a food term **and** a price term, or an approved topic phrase (`cost of living`, `purchasing power`, `food inflation`, `food prices`, `food crisis`, `food affordability`). This is a screening rule, not a human relevance label.
- Raw RSS captures are excluded from this repository pending a reuse/attribution review; re-running the collection notebook regenerates them.

## Method

1. **Text preparation** — headline normalisation, date parsing (UTC), deduplication by URL and by headline–source–datetime combination.
2. **Manual labels (ground truth)** — all 111 headlines labelled by the author as positive/neutral/negative using a written rubric (`references/labeling_aid.md`), with a short reason and confidence per row.
3. **Baseline** — VADER rule-based sentiment, compared against the manual labels.
4. **Core model** — TF-IDF (1–2 grams) + Logistic Regression (`class_weight='balanced'`), trained on a stratified 80/20 split; text features fitted on training data only.
5. **Evaluation** — accuracy, macro F1, per-class precision/recall, confusion matrices, and manual error analysis. Accuracy alone is not used because classes are imbalanced.
6. **Trend analysis** — weekly article counts, distinct-source counts, and model-predicted sentiment proportions applied to the full frozen collection.

## Results

_Manual labels (111 rows):_ negative 70% · neutral 22% · positive 8%. Evaluation on a stratified held-out test set of 23 rows.

| Model | Accuracy | Macro F1 |
|---|---|---|
| VADER (rule-based baseline) | 0.35 | 0.26 |
| TF-IDF + Logistic Regression | **0.74** | **0.48** |

Per-class (Logistic Regression): negative F1 0.86 · neutral F1 0.57 · positive F1 0.00 — only 2 test positives existed and both were missed.

**Key observations**

- The trained classifier clearly outperforms the lexicon baseline; VADER misread most Nigerian news headlines, which rarely use the social-media phrasing it was tuned for.
- Both models scored zero on the positive class — 9 positives overall (2 in test) is too few to learn from; reported honestly rather than tuned around.
- Representative errors: a *deceleration* headline ("food inflation slows…") was predicted negative although labelled neutral — rate-of-increase language reads as bad to a bag-of-words model; two price-*transparency* startup headlines were predicted negative because price vocabulary dominates the negative class; one prospective-relief story ("farmers predict lower food prices…", labelled neutral) was predicted positive — arguably the model's read was reasonable.
- Weekly predicted-sentiment share stayed negative-dominated throughout (50–100% negative per week), with the most negative weeks in early June and late July 2026. No week had a positive-majority tone.

Artifacts: `data/clean/model_comparison.csv`, `reports/figures/confusion_matrix_vader.png`, `reports/figures/confusion_matrix_logistic_regression.png`, `data/clean/model_error_analysis.csv`, `data/clean/weekly_sentiment_summary.csv`.

## Limitations

- News coverage is a proxy for attention, not public opinion or prices.
- Feed results are dynamic and ranked; the collection timestamp is part of the dataset definition.
- Source distribution is uneven (a few outlets dominate) — described as source coverage, not a representative media sample.
- First and last weeks are partial because the window boundary falls mid-week.
- English-language headlines only; broadcast-style and social-media discourse are out of scope.
- Small labelled sample (111); metrics carry wide uncertainty and are reported with class counts.
- Severe class imbalance (9 positive rows) makes per-class metrics for the positive label unreliable; both models scored zero on it.

## Ethics

No personal data or user profiles were collected; no publisher article bodies were scraped; only headlines and metadata needed for analysis were retained. Source reuse/attribution requirements were reviewed before publishing derived outputs.

## Reproduction

```bash
pip install -r requirements.txt
```

Run the notebooks in order:

1. `notebooks/day1_feasibility_check.ipynb` — source feasibility and decision
2. `notebooks/day2_day3_collection_eda.ipynb` — collection, cleaning, freeze, EDA
3. `notebooks/day4_labeling.ipynb` — label validation → `data/clean/articles_labeled.csv`
4. `notebooks/day4_modeling.ipynb` — baselines, model, evaluation, trends

## Repository structure

```text
├── README.md
├── implementation_file.md
├── requirements.txt
├── notebooks/
├── data/
│   ├── raw/          # collection metadata (+ local raw captures, not redistributed)
│   └── clean/        # frozen dataset, labels, model outputs
├── references/       # feasibility notes, EDA notes, labeling aid, sources
└── reports/figures/  # charts
```

Optional extensions (Streamlit dashboard, HuggingFace comparison, forecasting) are documented in `implementation_file.md` and are not part of the core DS-20 submission.

## Teaching app (post-submission extension)

`app/` contains **Sentiment Tracker Tutor**, an interactive Streamlit app that teaches this project's workflow to 3MTT peers and beginners using the real artifacts in `data/`. It was added after the capstone submission and does not change any graded content. See `app/README.md` for how to run or deploy it.
