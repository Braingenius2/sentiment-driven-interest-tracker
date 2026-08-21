# Implementation Plan

## Project Identity

- **Participant:** Fortune Uzodinma
- **Assigned brief:** DS-20
- **Project title:** Sentiment-Driven Interest Tracker
- **Working project title:** Sentiment-Driven Interest Tracker: Nigerian Food Prices and Cost of Living
- **Official deadline:** The 21st
- **Personal build sprint:** Seven days
- **Available study time:** 3-4 hours per day
- **Primary environment:** Google Colab with Google Drive backups

## Assignment Traceability

The project must satisfy the DS-20 brief from the supplied 3MTT materials:

- Prepare and clean text data.
- Perform sentiment analysis.
- Track sentiment or topic activity over time.
- Explain the results in a clear write-up.
- Provide a notebook or repository.
- Provide a sentiment model or analysis and its evaluation.
- Provide a README.
- Provide a 2-3 minute demonstration video.

The project is an individual educational MVP. A production application, live data feed, deep-learning model, and Streamlit deployment are not required for a valid DS-20 submission.

## Problem Definition

### Research Question

How has Nigerian online news attention to food prices and cost of living changed over the most recent available three-month period, and how has the sentiment of that coverage changed over time?

### Intended Audience

The analysis is for a reader who wants a simple, evidence-based view of how Nigerian news coverage of food prices and cost of living changes over time.

### Operational Definitions

- **Topic:** Nigerian food prices and cost of living.
- **Interest proxy:** The weekly number of relevant articles and distinct news domains returned by the selected data source.
- **Sentiment:** Positive, neutral, or negative tone expressed in an article headline.
- **Time trend:** Weekly changes in article volume and sentiment proportions.
- **Scope limitation:** Online news attention is not the same as the opinions of all Nigerians, household purchasing behaviour, search interest, or actual food prices.

The project will make this limitation explicit in the README, notebook, findings, and demo.

## Data Strategy

### Primary Source

Use the GDELT DOC 2.0 API to retrieve Nigerian-source news articles related to the topic.

The collection should retain only the fields needed for the MVP:

- Article URL
- Article title
- GDELT `seendate` field, recorded as the time GDELT observed the article
- Source domain
- Source country
- Language

The query, collection date, time window, keyword dictionary, and filtering decisions must be recorded. The raw response will be frozen before modelling begins.

GDELT is preferred because it provides structured dates and source metadata without requiring scraping several publisher websites. The API generally provides a rolling recent window, so the exact collection dates must be recorded rather than implied.

### Query Feasibility Check

Day 1 must verify all of the following before the dataset is frozen:

- The query returns enough records to support a time trend.
- A manual sample is genuinely about food prices or cost of living.
- The records cover more than one week or month.
- The data includes enough relevant headlines for a labelled sentiment sample.
- The sentiment labels are not completely dominated by one class.

The initial volume floor is a heuristic of approximately 80-100 relevant articles per month. It is not a reason to add unrelated terms. If volume is low, expand the keyword dictionary only with closely related terms and re-check topical relevance.

### Keyword Dictionary

The initial dictionary will be tested and refined during Day 1. Candidate terms include:

- food prices
- cost of living
- food inflation
- staple food prices
- rice prices
- bread prices
- cooking oil prices
- market prices
- food affordability
- food scarcity

The final dictionary must be written into the notebook and README.

### Contingency Source

If the GDELT feasibility check fails, use Google News RSS only after verifying that it returns usable dates, titles, and source information for the same topic. Multiple closely related RSS queries from that same service may be used to improve coverage, but they must remain one documented source strategy.

Only one source will be used for the final core analysis. The source decision and reason must be documented. We will not combine GDELT with publisher scraping during the core sprint.

**Current execution decision:** The strict GDELT query failed the local volume and time-coverage gate and was also rate-limited. The current frozen dataset therefore uses seven documented Google News RSS queries as the contingency source. See `references/day1_feasibility_notes.md` and `data/raw/collection_metadata.json`.

### Fallback Dataset

If neither GDELT nor the contingency source provides enough reliable Nigerian records, use the Stanford SNAP Amazon Fine Food Reviews dataset as a documented fallback.

This fallback contains food-review text, ratings, and dates, so it supports text preparation, sentiment, and time-trend analysis. It is not Nigerian and does not represent public interest in Nigeria. It must therefore be described as a scope fallback, not as equivalent evidence.

### Data Ethics and Reproducibility

- Do not collect social-media user profiles or personal identifiers.
- Do not scrape publisher article bodies during the core sprint.
- Keep the source URL, query, dates, and collection timestamp.
- Check the source's reuse and attribution requirements before publishing raw data.
- If raw data cannot be redistributed, include the acquisition instructions and a small documented sample instead.
- Do not put the Fellow ID in the public README unless the official submission instructions explicitly require it.

## Sentiment Method

### Ground Truth

A manually labelled headline sample will be used as the evaluation reference. The target is 100-150 headlines. If the available relevant data is genuinely limited, approximately 80 labelled headlines may be accepted if the class counts and limitation are reported clearly.

The labelling rubric will be written before labelling begins:

- **Positive:** The headline describes falling prices, improved affordability, successful relief, increased supply, or another clearly favourable development.
- **Negative:** The headline describes rising prices, unaffordability, scarcity, worsening hardship, or another clearly unfavourable development.
- **Neutral:** The headline reports information without a clear positive or negative tone.

Ambiguous examples will be recorded rather than forced into a confident label.

### Baseline

Use VADER as a simple rule-based baseline. VADER is not ground truth. Its predictions will be compared against the manual labels and its weaknesses will be discussed.

### Core Model

Train a transparent scikit-learn text-classification pipeline:

1. Split the manually labelled data into training and test sets.
2. Use `TfidfVectorizer` to convert headlines into numerical features.
3. Train `LogisticRegression` on the training features.
4. Evaluate predictions on the held-out test set.
5. Apply the final model to the frozen collection only after evaluation.

The pipeline must fit text transformations only on training data to avoid data leakage.

### Evaluation

Report:

- Accuracy
- Macro F1
- Per-class precision and recall
- Confusion matrix
- Class distribution
- A short manual error analysis with representative examples

Accuracy must not be the only metric because the classes may be imbalanced.

### Optional Comparison

A HuggingFace sentiment pipeline may be tested during the buffer week. It is optional and must not delay the VADER baseline, the scikit-learn model, or the required deliverables.

## Interest and Trend Analysis

The main analysis will keep interest and sentiment as separate measures:

- Weekly article count
- Weekly distinct domain count
- Weekly positive proportion
- Weekly neutral proportion
- Weekly negative proportion
- Optional weekly average mapped sentiment score, clearly labelled as a derived measure

The main conclusions must not rely on an unexplained composite such as volume multiplied by sentiment share. A composite indicator may only appear as a clearly labelled experiment or future idea.

Charts should include:

- A weekly article-volume line chart
- A weekly distinct-source chart or summary
- A weekly sentiment-share chart
- A chart or table identifying notable activity spikes

Any event-based explanation must be phrased cautiously and supported by the available article titles and links. Correlation must not be presented as causation.

## Seven-Day Core Sprint

Each day has approximately 3-4 hours available. The exit criterion must be met before optional work begins.

### Day 1: Frame and Check Feasibility

**Learning focus:** Data sources, APIs, DataFrames, data dictionaries, and research questions.

**Tasks:**

- Create or open the Colab notebook and connect a Google Drive project folder.
- Write the problem statement and research question.
- Test the GDELT query and inspect the returned fields.
- Check record volume, topical relevance, date coverage, source diversity, and likely label balance.
- Finalize the keyword dictionary and time window.
- Record the source, query, collection time, and first observations.

**Exit criteria:** One approved query returns enough relevant, dated Nigerian records to proceed, or the documented contingency is selected.

### Day 2: Collect, Clean, and Freeze

**Learning focus:** Data types, missing values, duplicates, dates, filtering, and reproducible data preparation.

**Tasks:**

- Retrieve the final dataset in repeatable batches if necessary.
- Save the raw response without overwriting it.
- Normalize column names and date types.
- Remove duplicate URLs or duplicate headlines where appropriate.
- Filter irrelevant records using documented rules.
- Save the clean dataset and a data dictionary.
- Freeze the dataset and record its row count and date range.

**Exit criteria:** `data/raw` and `data/clean` contain documented frozen inputs, or the approved fallback has been frozen.

### Day 3: Explore and Start Labelling

**Learning focus:** Exploratory data analysis, grouping, proportions, and chart interpretation.

**Tasks:**

- Inspect missing values and class-unrelated data quality issues.
- Summarize dates, domains, languages, and record counts.
- Produce preliminary weekly volume and source-count summaries.
- Write the sentiment labelling rubric.
- Begin manual labelling of the evaluation sample.
- Track label counts and ambiguous examples.

**Exit criteria:** The dataset is understood, the interest measures are defined, and labelling has started with a written rubric.

### Day 4: Finish Labels and Train Models

**Learning focus:** Features, labels, train/test splits, vectorization, pipelines, and classification.

**Tasks:**

- Complete the labelled sample.
- Review the class distribution and document limitations.
- Run VADER on the evaluation sample.
- Build the TF-IDF plus Logistic Regression pipeline.
- Train only on the training partition.
- Produce first evaluation results.

**Exit criteria:** Both the baseline and core model produce predictions and evaluation output.

### Day 5: Evaluate and Build the Tracker

**Learning focus:** Evaluation metrics, error analysis, time grouping, and visualization.

**Tasks:**

- Calculate the full metric set.
- Compare VADER and Logistic Regression against the manual labels.
- Inspect correct and incorrect examples.
- Apply the evaluated model to the frozen collection.
- Generate weekly interest and sentiment trends.
- Perform basic trend sanity checks against the article titles and dates.

**Exit criteria:** The notebook contains defensible model results, error analysis, and the main trend charts.

### Day 6: Explain and Package

**Learning focus:** Technical writing, limitations, ethics, and reproducibility.

**Tasks:**

- Draft the findings in plain language.
- Explain the media-attention proxy limitation.
- Document the source, query, labels, model, metrics, and limitations.
- Add a short future-use paragraph without claiming product readiness.
- Write the README using the participant name and `DS-20`.
- Clean notebook headings, outputs, comments, and chart labels.
- Confirm that no secret keys or personal identifiers are included.

**Exit criteria:** A reader can understand the problem, reproduce the work, inspect the evaluation, and identify the limitations.

### Day 7: Verify and Demonstrate

**Learning focus:** Reproducibility, quality assurance, and communicating work independently.

**Tasks:**

- Restart the Colab runtime and run the notebook from the beginning.
- Fix errors, stale state, broken paths, and unclear outputs.
- Check that charts and metrics are generated from the frozen data.
- Spend 60-90 minutes preparing and recording the 2-3 minute demo video.
- Ensure the demo explains the problem, data, method, result, and limitation.
- Perform a final submission checklist review.

**Exit criteria:** The core notebook, repository materials, README, evaluation, and demo video are ready for review.

## Buffer Before the 21st

The remaining days are for quality and submission safety, not for expanding the core scope.

Optional work, in this order, is allowed only after the required deliverables pass review:

1. Deploy a simple Streamlit view of the existing trend charts.
2. Compare the evaluated model with a HuggingFace pipeline.
3. Test a simple next-week trend extrapolation and label it experimental.
4. Retake or improve the demo video.
5. Rerun the final notebook and prepare the portal submission.

If any stretch feature threatens the required deliverables, it must be dropped.

## Repository and Notebook Structure

The minimum project structure should remain simple:

```text
sentiment-driven-interest-tracker/
├── README.md
├── implementation_file.md
├── notebooks/
│   └── sentiment_interest_tracker.ipynb
├── data/
│   ├── raw/
│   └── clean/
├── references/
│   └── sources.md
└── requirements.txt
```

The exact structure may be simplified if it helps the project remain understandable. Do not create extra modules merely to look professional.

## Learning Agreement

The project is a learning exercise, not an outsourced submission.

- The assistant will explain concepts before asking for implementation.
- Fortune will write and run the main notebook cells.
- The assistant will provide hints, debugging help, review, and small examples.
- Each milestone ends with Fortune explaining what the code did and why.
- Results must be interpreted from actual outputs, not invented in advance.
- Any code copied from documentation must be understood, adapted, and cited where appropriate.
- We will prefer small working steps over large generated blocks of code.

## Definition of Done

The project is complete when:

- The notebook runs from start to finish in a clean Colab runtime.
- The DS-20 requirements are visibly addressed.
- The final source, query, collection dates, filtering rules, and limitations are documented.
- Text preparation is shown.
- VADER provides a baseline comparison.
- TF-IDF plus Logistic Regression provides the core evaluated model.
- Evaluation includes macro F1, a confusion matrix, class counts, and error analysis.
- Weekly interest and sentiment trends are visualized.
- Findings do not claim that news coverage equals public opinion.
- The README explains setup, data, method, results, limitations, and reproduction.
- The 2-3 minute demo video explains Fortune's own work.
- No secret keys, private credentials, or unnecessary personal identifiers are published.
- Any Streamlit, HuggingFace, or forecasting work is clearly marked optional.

## Key References

### Supplied Assignment Materials

- `Data Science.pdf`
- `Capstone Project Assignment.xlsx`
- `3MTT NextGen Project Brief Bank.xlsx`

Relevant assignment locations include the DS-20 row in the Data Science sheet, the participant assignment row in General Assignments, and the Scoring Guide and Overview sheets.

### Technical References

- [GDELT DOC 2.0 API](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)
- [scikit-learn feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html)
- [scikit-learn pipelines](https://scikit-learn.org/stable/modules/compose.html)
- [scikit-learn model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [NaijaSenti reference dataset](https://github.com/hausanlp/NaijaSenti)
- [Stanford SNAP Amazon Fine Food Reviews fallback](https://snap.stanford.edu/data/web-FineFoods.html)

## Change Control

Any change to the topic, source, labels, model, or stretch features must be recorded in the notebook and README. A change is acceptable only if it improves reproducibility or protects the required DS-20 deliverables. Optional features must never displace the core analysis.

### Log

- **2026-08-14 — Source decision finalized.** GDELT DOC 2.0 confirmed unavailable from this environment (repeated HTTP 429 responses followed by read timeouts across attempts; see `references/day1_feasibility_notes.md`). The documented contingency was selected as the single core source: Google News RSS, collected via seven closely related queries on 2026-08-14. Window set to the latest three months (15 May – 11 Aug 2026). Collection details in `data/raw/collection_metadata.json`.

### Decision Log

- **2026-08-14:** GDELT did not pass the local feasibility gate because the strict query produced insufficient time coverage and repeated rate-limit responses. The project switched to the documented Google News RSS contingency using seven closely related queries from the same service.
- **2026-08-14:** The final collection was frozen at 111 topic-filtered records after deduplication and a three-month date filter. The collection notebook must use replay mode for deterministic verification.
- **2026-08-14:** Streamlit, HuggingFace, and forecasting remain optional buffer work and cannot delay the required notebook, evaluation, README, and demo.
