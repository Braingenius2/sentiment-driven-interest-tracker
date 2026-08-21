# Demo Video Script — DS-20 Sentiment-Driven Interest Tracker

**Target length:** 2:30–2:50 · **Format:** screen recording + voiceover · **Participant:** Fortune Uzodinma

---

## Before you hit record

- [ ] Open these in tabs, in this order: `day4_modeling.ipynb` (scrolled to comparison table) → `reports/figures/weekly_article_volume.png` → `reports/figures/confusion_matrix_logistic_regression.png` → `README.md`
- [ ] Turn on Do Not Disturb; close Slack/mail/notification badges; hide bookmarks bar
- [ ] Browser zoom ~125% so text reads on video
- [ ] One practice run with a timer — aim to finish under 2:50
- [ ] Recorder: Xbox Game Bar (`Win+G`) or OBS Studio; mic close, quiet room
- [ ] Speak slightly slower than feels natural; pause at each section break

---

## The script

### Section 1 — Problem (0:00–0:20)

**On screen:** README top / framing cell

**Say:**

> Hi, I'm Fortune Uzodinma, and this is my DS-20 capstone: a sentiment-driven interest tracker for Nigerian food prices and the cost of living. Nigerians feel this pressure every day — but it's hard to see how news coverage reflects it, and how that attention shifts over time. One thing upfront: this project tracks *news attention* — not public opinion, and not actual prices.

### Section 2 — Data (0:20–0:45)

**On screen:** `collection_metadata.json` or Day 1 notebook gate output

**Say:**

> I planned to use GDELT as my primary source, but it was persistently rate-limited and timed out. So I moved to my documented contingency: Google News RSS feeds. I queried one service with seven closely related phrases — food prices, food inflation, cost of living, rice prices and more — then cleaned, deduplicated, and filtered the results down to **111 frozen headlines** from **51 distinct sources**, covering mid-May to mid-August 2026.

### Section 3 — Manual labels (0:45–1:15)

**On screen:** `articles_labeled.csv` showing rows 1–3 side by side

**Say:**

> Every headline was labelled by hand, using a written rubric: *positive* for falling prices or relief, *negative* for rising prices, scarcity or hardship, *neutral* for factual reporting. Here's why human judgment matters. "Inflation **rises** to 15.69 percent" is clearly negative. But "food inflation **slows** to 16 percent" *sounds* like good news — while prices are still rising. I labelled that one neutral. Overall, seventy percent of coverage was negative.

### Section 4 — Models (1:15–1:45)

**On screen:** model comparison table in `day4_modeling.ipynb`

**Say:**

> Using those labels as ground truth, I compared two approaches. VADER — a rule-based baseline — managed only thirty-five percent accuracy. It's tuned for social media language, not Nigerian news headlines. My core model — TF-IDF features with logistic regression — reached **seventy-four percent accuracy** and zero point four eight macro F1. Both models scored zero on the positive class: only nine positive headlines existed. I report that honestly rather than tuning around it.

### Section 5 — Findings (1:45–2:10)

**On screen:** `weekly_article_volume.png`, then the weekly sentiment summary

**Say:**

> Applying the trained model to the full collection, weekly sentiment stayed negative-dominated — between fifty and one hundred percent, every single week. The most negative stretches were early June and late July, and across three months, **no week had a positive-majority tone**. That's the tracker doing exactly what DS-20 asked: making shifting attention visible.

### Section 6 — Errors and honesty (2:10–2:40)

**On screen:** `model_error_analysis.csv` (rows for row_id 3, 52, 107)

**Say:**

> The error analysis is where it gets interesting. A headline saying inflation "**slows**" was predicted negative — a bag-of-words model can't understand deceleration. Two price-*transparency* startup stories were predicted negative, because price vocabulary dominates the negative class. None of this is hidden — the errors are exported with explanations. Key limitations: a small labelled sample, severe class imbalance, dynamic ranked feeds, and coverage being only a proxy for real-world interest.

### Section 7 — Close (2:40–2:50)

**On screen:** repository root / README reproduction section

**Say:**

> Everything reproduces from four notebooks run in order, with one requirements file, and the README documents data, method, evaluation and ethics. Thanks for watching — this was my DS-20 sentiment-driven interest tracker.

---

## After recording

- [ ] Watch it back once: audio audible, text readable, under 3 minutes
- [ ] Export MP4, name it `DS20_Fortune_Uzodinma_Demo.mp4`
- [ ] Upload where the portal asks (or YouTube unlisted)
- [ ] Description line: `DS-20 Sentiment-Driven Interest Tracker — Fortune Uzodinma (FE/24/4175253063)` — Fellow ID lives here and in the portal, never in the public README
- [ ] Submit on the portal before the deadline

## If you're short on time

Minimum viable version: skip Sections 6–7 details — say one sentence on errors ("the error analysis and limitations are documented in the README") and close. You still cover problem, data, labels, model, findings — which is the full rubric.
