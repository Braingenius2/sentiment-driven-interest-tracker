"""Sentiment Tracker Tutor — an interactive teaching app built from a real DS-20 capstone.

Audience: 3MTT peers and data-science beginners.
It teaches the full project workflow with the actual artifacts from the capstone:
frame the question -> choose data -> label ground truth -> baseline vs trained model ->
honest evaluation -> trends and limitations.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "clean"
RAW = ROOT / "data" / "raw"

LABELS = ["positive", "neutral", "negative"]
LABEL_ORDER = ["negative", "neutral", "positive"]  # matches the capstone notebooks


# ----------------------------------------------------------------------------- data & models
@st.cache_data
def load_data():
    labeled = pd.read_csv(DATA / "articles_labeled.csv")
    interest = pd.read_csv(DATA / "weekly_interest_summary.csv")
    sentiment = pd.read_csv(DATA / "weekly_sentiment_summary.csv")
    comparison = pd.read_csv(DATA / "model_comparison.csv")
    errors = pd.read_csv(DATA / "model_error_analysis.csv")
    metadata = json.loads((RAW / "collection_metadata.json").read_text(encoding="utf-8"))
    return labeled, interest, sentiment, comparison, errors, metadata


@st.cache_resource
def train_model(labeled: pd.DataFrame):
    """Retrain the exact capstone pipeline on the 111 manual labels (seeded)."""
    X_train, X_test, y_train, y_test = train_test_split(
        labeled["headline"],
        labeled["sentiment_label"],
        test_size=0.2,
        random_state=42,
        stratify=labeled["sentiment_label"],
    )
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    X_train_vec = vectorizer.fit_transform(X_train)
    model.fit(X_train_vec, y_train)
    return vectorizer, model, X_test, y_test


@st.cache_resource
def get_vader():
    return SentimentIntensityAnalyzer()


def vader_label(text: str) -> tuple[str, float]:
    """Map VADER's compound score to a label using the capstone's thresholds."""
    compound = get_vader().polarity_scores(text)["compound"]
    if compound >= 0.05:
        return "positive", compound
    if compound <= -0.05:
        return "negative", compound
    return "neutral", compound


def driving_tokens(text: str, vectorizer, model, top_n: int = 5):
    """Explain a LogReg prediction by listing the tokens with the biggest push."""
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    class_idx = list(model.classes_).index(pred)
    feature_names = np.array(vectorizer.get_feature_names_out())
    contributions = vec.toarray()[0] * model.coef_[class_idx]
    used = vec.indices
    if len(used) == 0:
        return pred, []
    pairs = sorted(
        ((feature_names[i], contributions[i]) for i in used),
        key=lambda p: abs(p[1]),
        reverse=True,
    )
    return pred, [(tok, float(w)) for tok, w in pairs[:top_n]]


# ----------------------------------------------------------------------------- quiz helper
def quiz(quiz_id: str, question: str, options: list[str], correct: int, explanation: str):
    """A tiny light quiz: one question, instant feedback, no score-keeping pressure."""
    st.markdown(f"**Quick check — {question}**")
    choice = st.radio(question, options, key=f"{quiz_id}_radio", label_visibility="collapsed", index=None)
    if st.button("Check my answer", key=f"{quiz_id}_btn"):
        if choice is None:
            st.info("Pick an option first.")
        elif options.index(choice) == correct:
            st.success(f"Correct. {explanation}")
        else:
            st.error(f"Not quite. {explanation}")


# ----------------------------------------------------------------------------- page setup
st.set_page_config(page_title="Sentiment Tracker Tutor", page_icon="📰", layout="wide")

labeled, interest, sentiment, comparison, errors, metadata = load_data()

st.sidebar.title("Sentiment Tracker Tutor")
module = st.sidebar.radio(
    "Pick a module",
    [
        "0 · Welcome",
        "1 · The Story: from question to dataset",
        "2 · You Be the Labeler",
        "3 · Baseline vs Model (playground)",
        "4 · Honest Evaluation",
        "5 · Trends and Limits",
    ],
)
st.sidebar.caption(
    "Built as a post-submission extension of a real 3MTT DS-20 capstone: "
    "*Sentiment-Driven Interest Tracker — Nigerian food prices and cost of living.*"
)

# ============================================================================= 0 · Welcome
if module.startswith("0"):
    st.title("Sentiment Tracker Tutor")
    st.subheader("Learn a full data-science project by walking through one that really happened")

    st.markdown(
        """
This app teaches one section of **data-science project-based learning** — *text sentiment
tracked over time* — using the real artifacts from a finished capstone:

- **111 real headlines** about Nigerian food prices and the cost of living,
- **111 human labels** (positive / neutral / negative) with a reason and confidence for each,
- two sentiment models that were honestly compared,
- and the weekly trend charts they produced.

Nothing here is synthetic or made up for the lesson. Every number you see is the number
the project actually produced.

**The 2026 lesson baked into this app:** start classical, not fashionable.
A rule-based baseline (VADER) and a classical model (TF-IDF + Logistic Regression)
came first; bigger tools only make sense after you know what the baseline gets wrong.
"""
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Headlines in the dataset", len(labeled))
    col2.metric("Human labels (ground truth)", int(labeled["sentiment_label"].notna().sum()))
    col3.metric("Sources", labeled["source_label"].nunique())

    st.markdown(
        """
**How to use this app**

1. Start with **Module 1** to see how a messy question becomes a frozen dataset.
2. In **Module 2**, label real headlines yourself and compare against the human ground truth.
3. In **Module 3**, type any headline and watch a rule-based baseline and a trained model disagree (or not).
4. **Module 4** shows why "0.74 accuracy" can still hide a broken class.
5. **Module 5** ends with the trend charts and what they *cannot* tell you.

Each module has one short quiz. There are no grades — only understanding.
"""
    )

# ============================================================================= 1 · The Story
elif module.startswith("1"):
    st.title("Module 1 · The Story: from question to dataset")

    st.markdown(
        """
Every data project starts as a fuzzy idea. This one started as:

> *"Track sentiment on a topic over time."* — 3MTT brief DS-20

Before any code, the project pinned down three things:
the **research question**, the **operational definitions** (what exactly counts as
"interest" and "sentiment"?), and the **scope limitation**
(news coverage is not public opinion).
"""
    )

    st.markdown("### The data-source decision")
    st.markdown(
        f"""
The first choice was the GDELT news API. It was tested and **failed the feasibility gate**:
the strict query returned 11 records covering about 90 minutes, then the API kept answering
with rate-limit errors. So the project switched to its documented contingency:
**Google News RSS**, using {metadata['feed_count']} closely related queries from that one service.

> Lesson: a data source is not chosen because it is famous.
> It passes a gate — enough records, enough time coverage, enough variety — or it does not.
"""
    )

    st.markdown("### The funnel: raw noise to frozen dataset")
    funnel = pd.DataFrame(
        {
            "stage": [
                "Raw feed items",
                "After deduplication",
                "Within 3-month window",
                "After topic filter (frozen)",
            ],
            "count": [
                metadata["feed_items_raw"],
                metadata["unique_records_after_deduplication"],
                metadata["rows_after_three_month_filter"],
                metadata["rows_frozen"],
            ],
        }
    )
    fig = px.funnel(funnel, x="count", y="stage", title="Collection funnel (recorded timestamps included)")
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"Collection time was recorded as **{metadata['collection_time_utc']}** because RSS feeds "
        "are dynamic — the same query a week later returns different results. "
        "The timestamp is part of the dataset's definition."
    )

    quiz(
        "m1",
        "Why was the collection timestamp treated as part of the dataset definition?",
        [
            "It makes the README look more professional",
            "Feed results change over time, so without it the data cannot be reproduced",
            "The scoring rubric required it",
        ],
        1,
        "Dynamic sources return different results at different times. Without a timestamp and a frozen copy, nobody could reproduce the analysis.",
    )

# ============================================================================= 2 · Labeler
elif module.startswith("2"):
    st.title("Module 2 · You Be the Labeler")

    st.markdown(
        """
The project's ground truth was **111 headlines labelled by hand**. Every label also recorded
a short *reason* and a *confidence* level — because "trust me" is not a dataset.

Now it is your turn. You will see a real headline. Label it using the project's rubric,
then compare with the human label.
"""
    )

    with st.expander("The rubric used in the project"):
        st.markdown(
            """
- **positive** — falling prices, improved affordability, relief, increased supply
- **negative** — rising prices, inflation pressure, scarcity, worsening hardship
- **neutral** — factual reporting with no clear positive or negative tone

*Label the headline's tone, not whether the news itself is good or bad.*
"""
        )

    if "labeler_stats" not in st.session_state:
        st.session_state.labeler_stats = {"total": 0, "agree": 0}
    if "current_row" not in st.session_state:
        st.session_state.current_row = labeled.sample(1).iloc[0]

    row = st.session_state.current_row
    st.markdown("#### Your headline")
    st.markdown(f"> {row['headline']}")
    st.caption(f"Source: {row['source_label']}")

    guess = st.radio("Your label", LABELS, horizontal=True, index=None, key="labeler_guess")

    if st.button("Reveal the human label"):
        if guess is None:
            st.info("Choose a label first.")
        else:
            truth = row["sentiment_label"]
            st.session_state.labeler_stats["total"] += 1
            if guess == truth:
                st.session_state.labeler_stats["agree"] += 1
                st.success(f"You both said **{truth}**. Agreement!")
            else:
                st.warning(f"You said **{guess}**, the human label is **{truth}**.")
            st.markdown(f"**Recorded reason:** {row['label_reason']}")
            st.markdown(f"**Labeler's confidence:** {row['confidence']}")

            vectorizer, model, _, _ = train_model(labeled)
            pred, _ = driving_tokens(row["headline"], vectorizer, model)
            st.caption(f"For reference, the trained model predicted: **{pred}**")

    if st.button("Next headline"):
        st.session_state.current_row = labeled.sample(1).iloc[0]
        st.rerun()

    stats = st.session_state.labeler_stats
    if stats["total"] > 0:
        st.metric(
            "Your agreement with the human labeler",
            f"{stats['agree']}/{stats['total']} ({stats['agree'] / stats['total']:.0%})",
        )
        st.caption(
            "Disagreement is not failure — it is exactly why labels need written rubrics. "
            "Two careful people can read the same headline differently."
        )

    quiz(
        "m2",
        "Why did every label record a *reason* and a *confidence*, not just the label?",
        [
            "Because the spreadsheet had empty columns",
            "So ambiguous or low-confidence rows can be audited instead of silently trusted",
            "To make the dataset file bigger",
        ],
        1,
        "Ground truth is only as trustworthy as its audit trail. Reasons and confidence let reviewers find the shaky rows instead of assuming all labels are equal.",
    )

# ============================================================================= 3 · Playground
elif module.startswith("3"):
    st.title("Module 3 · Baseline vs Model playground")

    st.markdown(
        """
The project compared two approaches:

- **VADER** — a rule-based baseline: a dictionary of sentiment words with hand-tuned scores.
  No training data needed, but it knows nothing about Nigerian news phrasing.
- **TF-IDF + Logistic Regression** — a classical trained model: TF-IDF turns each headline
  into numbers (how important each word is), and Logistic Regression learns class weights
  from the 111 manual labels.

Type any headline below and watch both answer.
"""
    )

    vectorizer, model, _, _ = train_model(labeled)

    default_text = "Food inflation hits 17.52% but headline inflation eases"
    text = st.text_area("Headline to analyse", value=default_text, height=80)

    if st.button("Analyse", type="primary"):
        if not text.strip():
            st.info("Type a headline first.")
        else:
            v_label, compound = vader_label(text)
            pred, tokens = driving_tokens(text, vectorizer, model)

            col1, col2 = st.columns(2)
            col1.subheader("VADER (rule-based baseline)")
            col1.metric("Compound score", f"{compound:+.3f}")
            col1.metric("Label (≥0.05 pos, ≤-0.05 neg)", v_label)

            col2.subheader("TF-IDF + Logistic Regression")
            col2.metric("Predicted label", pred)
            if tokens:
                tok_df = pd.DataFrame(tokens, columns=["token", "push"])
                fig = px.bar(
                    tok_df,
                    x="push",
                    y="token",
                    orientation="h",
                    title=f"Tokens pushing the prediction toward '{pred}'",
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                col2.plotly_chart(fig, use_container_width=True)
                col2.caption(
                    "Each bar shows how strongly a token pulls the model toward its answer. "
                    "This is why classical models are loved for teaching: you can see the reason."
                )

            if v_label != pred:
                st.warning(
                    "The two approaches disagree. That happened a lot in the real project — "
                    "and it is exactly why evaluation against human labels matters."
                )

    quiz(
        "m3",
        "In 2026, with LLMs everywhere, why start with TF-IDF + Logistic Regression?",
        [
            "It is always more accurate than an LLM",
            "It is fast, free, interpretable, and sets a baseline that bigger models must beat",
            "Because LLMs cannot do sentiment analysis",
        ],
        1,
        "A classical baseline trains in seconds, costs nothing, and shows you its reasoning. If your fancy model cannot beat it, you saved yourself a lot of trouble.",
    )

# ============================================================================= 4 · Evaluation
elif module.startswith("4"):
    st.title("Module 4 · Honest Evaluation")

    vectorizer, model, X_test, y_test = train_model(labeled)
    logreg_pred = model.predict(vectorizer.transform(X_test))
    vader_pred = [vader_label(t)[0] for t in X_test]

    st.markdown(
        """
Both models were tested on the same **held-out test set** (20% of the 111 labels,
never seen during training). Here are the real numbers.
"""
    )

    comp = comparison.set_index("model")[["accuracy", "macro_f1"]]
    st.dataframe(comp.style.format("{:.2f}"), use_container_width=True)

    st.markdown("### Confusion matrices (same test set)")
    col1, col2 = st.columns(2)
    for col, name, preds in [("col1", "VADER", vader_pred), ("col2", "LogReg", logreg_pred)]:
        cm = confusion_matrix(y_test, preds, labels=LABEL_ORDER)
        fig = px.imshow(
            cm,
            x=LABEL_ORDER,
            y=LABEL_ORDER,
            text_auto=True,
            color_continuous_scale="Blues",
            labels={"x": "Predicted", "y": "Actual", "color": "count"},
            title=name,
        )
        (col1 if col == "col1" else col2).plotly_chart(fig, use_container_width=True)

    st.markdown("### The accuracy trap")
    acc = accuracy_score(y_test, logreg_pred)
    f1 = f1_score(y_test, logreg_pred, average="macro")
    per_class = f1_score(y_test, logreg_pred, average=None, labels=LABEL_ORDER, zero_division=0)

    st.markdown(
        f"""
LogReg reached **{acc:.0%} accuracy**. Sounds fine — until you look per class:

- negative F1: **{per_class[0]:.2f}**
- neutral F1: **{per_class[1]:.2f}**
- positive F1: **{per_class[2]:.2f}** — the model missed *every* positive headline.

The dataset had only **9 positive headlines** (2 in the test set). There was not enough
data to learn that class. Accuracy hid this; **macro F1 ({f1:.2f})** surfaced it,
because macro F1 weights every class equally no matter how rare.
"""
    )

    st.markdown("### Read the actual errors")
    st.caption("Real misclassifications from the test set — reading errors teaches more than any metric.")
    st.dataframe(
        errors[["headline", "sentiment_label", "model_prediction", "label_reason"]],
        use_container_width=True,
    )

    quiz(
        "m4",
        "The model scored 0.74 accuracy but 0.00 F1 on the positive class. Which number warned you first?",
        [
            "Accuracy",
            "Macro F1",
            "The number of headlines",
        ],
        1,
        "Macro F1 averages classes equally, so a totally failed rare class drags it down. Accuracy can look healthy while a whole class is being ignored.",
    )

# ============================================================================= 5 · Trends
elif module.startswith("5"):
    st.title("Module 5 · Trends and Limits")

    st.markdown(
        """
The project's output was two weekly views over three months (15 May – 11 Aug 2026):
**attention** (how much coverage) and **sentiment** (the tone of that coverage),
kept as *separate measures* on purpose.
"""
    )

    st.markdown("### Weekly attention")
    fig = go.Figure()
    fig.add_scatter(x=interest["week"], y=interest["article_count"], mode="lines+markers", name="Articles")
    fig.add_scatter(
        x=interest["week"],
        y=interest["distinct_source_count"],
        mode="lines+markers",
        name="Distinct sources",
    )
    fig.update_layout(xaxis_title="Week", yaxis_title="Count", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("The first and last weeks are partial — the collection window cut through them.")

    st.markdown("### Weekly sentiment share (model predictions)")
    sent_long = sentiment.melt(id_vars="week", var_name="sentiment", value_name="share")
    fig2 = px.area(
        sent_long,
        x="week",
        y="share",
        color="sentiment",
        category_orders={"sentiment": LABEL_ORDER},
        color_discrete_map={"negative": "#d62728", "neutral": "#7f7f7f", "positive": "#2ca02c"},
        title="Share of predicted sentiment per week",
    )
    fig2.update_layout(yaxis_tickformat=".0%", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Every week was negative-dominated — a descriptive fact about this sample, not a claim about the country.")

    st.markdown("### What this does NOT measure")
    st.markdown(
        """
- **Not public opinion.** Headlines are what newsrooms chose to publish, not what Nigerians think.
- **Not actual prices.** The tracker reads coverage, not market data.
- **Not complete coverage.** The RSS feed is a ranked, dynamic sample of online news.
- **Not the future.** A trend line describes the window you collected. It does not predict.
"""
    )

    quiz(
        "m5",
        "A week shows 100% negative sentiment share. What is the strongest claim you can make?",
        [
            "Nigerians felt negative about food prices that week",
            "Food prices were at their worst that week",
            "In this collected sample of headlines, every article that week had a negative tone",
        ],
        2,
        "The claim must stay inside the data: this sample, these headlines, that week. Anything about 'the public' or 'actual prices' goes beyond what was measured.",
    )

    st.success(
        "You finished the tour. You just walked a real pipeline: question → source gate → "
        "frozen data → human labels → baseline vs model → honest metrics → careful claims."
    )
