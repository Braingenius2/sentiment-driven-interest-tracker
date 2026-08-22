# Sentiment Tracker Tutor (teaching app)

**Post-submission extension** of the DS-20 capstone in this repository. The graded capstone
content (notebooks, data, results) is unchanged; this folder adds an interactive app that
*teaches* the workflow to 3MTT peers and data-science beginners using the project's real
artifacts.

## What it teaches

Five modules, one light quiz each:

1. **The Story** — research question, data-source feasibility gate, the 676 → 111 funnel.
2. **You Be the Labeler** — label real headlines, compare with the human ground truth
   (label + reason + confidence), track your agreement rate.
3. **Baseline vs Model** — type any headline; VADER's compound score vs a TF-IDF +
   Logistic Regression prediction retrained in-app (seeded), with the tokens driving it.
4. **Honest Evaluation** — confusion matrices on the held-out test set, accuracy vs
   macro F1, and the real misclassifications.
5. **Trends and Limits** — weekly attention and sentiment charts, plus what the data
   cannot measure (news coverage ≠ public opinion).

## Run locally

```bash
pip install -r app/requirements.txt
streamlit run app/streamlit_app.py
```

The app reads `data/clean/*.csv` and `data/raw/collection_metadata.json` from this repo —
no copies, no separate data step.

## Deploy (Streamlit Community Cloud)

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. New app → repo `Braingenius2/sentiment-driven-interest-tracker` → branch `main` →
   main file path `app/streamlit_app.py`.
3. Deploy. Streamlit Cloud installs from `app/requirements.txt` automatically.
