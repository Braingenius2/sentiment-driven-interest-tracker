# Sources

## Selected source

- **Google News RSS search feeds** (selected 14 Aug 2026). One service queried with seven closely related phrases:
  - Nigeria food prices
  - Nigeria food inflation
  - Nigeria cost of living
  - Nigeria rice prices
  - Nigeria food affordability
  - Nigeria staple food prices
  - Nigeria purchasing power food

  Example feed URL: `https://news.google.com/rss/search?q=Nigeria%20food%20prices&hl=en-NG&gl=NG&ceid=NG%3Aen`
  Full list recorded in `data/raw/collection_metadata.json`.

## Tested and rejected for the core dataset

- **GDELT DOC 2.0 API** — <https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/>
  Tested first as primary source. Persistently unavailable from this environment: repeated HTTP 429 rate-limit responses followed by read timeouts; when a response did return, the strict query produced too few records to support a trend. Documented in `references/day1_feasibility_notes.md`.

## Reference datasets (not used in the core analysis)

- **NaijaSenti** — <https://github.com/hausanlp/NaijaSenti> — Nigerian-language sentiment corpus; consulted for rubric design context.
- **Stanford SNAP Amazon Fine Food Reviews** — <https://snap.stanford.edu/data/web-FineFoods.html> — documented fallback if neither live source had provided enough records. Not required.

## Assignment materials

- `Data Science.pdf` — 3MTT Data Science curriculum
- `Capstone Project Assignment.xlsx` — fellow assignment roster and DS brief bank (DS-20)
- `3MTT NextGen Project Brief Bank.xlsx` — multi-track brief bank and data-sources guide
