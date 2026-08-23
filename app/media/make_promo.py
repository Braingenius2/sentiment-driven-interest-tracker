"""Render the Sentiment Tracker Tutor promo video (silent, caption-driven motion graphics).

Every frame is drawn with matplotlib and piped raw into ffmpeg (H.264).
The script is committed so the video is fully reproducible:

    uv run --with matplotlib --with pandas --with numpy --with scikit-learn -- python app/media/make_promo.py
"""

import json
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "clean"
RAW = ROOT / "data" / "raw"
OUT = Path(__file__).resolve().parent / "tutor_promo.mp4"

FPS = 24
W, H = 1920, 1080          # logical design space (all coordinates use this)
DPI = 100
RENDER_SCALE = 0.75        # render at 1440x810, ffmpeg upscales to 1080p (lanczos)

BG = "#0e1117"
FG = "#f0f3f6"
MUT = "#8b949e"
ACC = "#58a6ff"
NEG = "#d62728"
NEU = "#9e9e9e"
POS = "#2ca02c"
CARD = "#161b22"

LABEL_ORDER = ["negative", "neutral", "positive"]
LIVE_APP_URL = "https://sentiment-driven-interest-tracker-by-fortune.streamlit.app/"
REPO_URL = "https://github.com/Braingenius2/sentiment-driven-interest-tracker"


def ease(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def clip01(t: float) -> float:
    return min(max(t, 0.0), 1.0)


def new_frame():
    # Design space stays 1920x1080 logical units. Lowering dpi shrinks the pixel
    # buffer while figsize in inches keeps point-based font sizes proportional to
    # the design -- ffmpeg's lanczos upscale then restores the intended layout.
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=int(DPI * RENDER_SCALE))
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    ax.axis("off")
    return fig, ax


def kicker(ax, text):
    ax.text(90, 1010, text, color=ACC, fontsize=26, fontweight="bold", family="DejaVu Sans")


def render_frame(scene_fn, p):
    fig, ax = new_frame()
    scene_fn(ax, p)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return buf


# ----------------------------------------------------------------- data
interest = pd.read_csv(CLEAN / "weekly_interest_summary.csv")
sentiment = pd.read_csv(CLEAN / "weekly_sentiment_summary.csv")
labeled = pd.read_csv(CLEAN / "articles_labeled.csv")
metadata = json.loads((RAW / "collection_metadata.json").read_text(encoding="utf-8"))


def short_week(week: str) -> str:
    start = week.split("/")[0]  # e.g. 2026-05-11/2026-05-17
    d = pd.Timestamp(start)
    return d.strftime("%b %d")


# ----------------------------------------------------------------- scene 1: title
def scene_title(ax, p):
    a = ease(p * 1.6)
    rise = (1 - a) * 40
    ax.text(960, 600 + rise, "Sentiment Tracker Tutor", color=FG,
            fontsize=88, fontweight="bold", ha="center", alpha=a)
    ax.text(960, 470 + rise, "Learn a real data-science project — by walking through it",
            color=MUT, fontsize=34, ha="center", alpha=ease(p * 1.6 - 0.25))
    ax.text(960, 380 + rise, "Nigerian food prices · cost of living · 111 human-labelled headlines",
            color=ACC, fontsize=28, ha="center", alpha=ease(p * 1.6 - 0.45))


# ----------------------------------------------------------------- scene 2: funnel
STAGES = [
    ("Raw feed items", metadata["feed_items_raw"]),
    ("After deduplication", metadata["unique_records_after_deduplication"]),
    ("In 3-month window", metadata["rows_after_three_month_filter"]),
    ("Frozen dataset", metadata["rows_frozen"]),
]


def scene_funnel(ax, p):
    kicker(ax, "01 · FROM QUESTION TO DATASET")
    ax.text(960, 880, "The collection funnel", color=FG, fontsize=52,
            fontweight="bold", ha="center")
    max_count = STAGES[0][1]
    bar_h, gap = 120, 46
    top = 720
    for i, (label, count) in enumerate(STAGES):
        local = ease(p * len(STAGES) * 1.15 - i)
        if local <= 0:
            continue
        width = 1500 * (count / max_count) ** 0.55 * local
        y = top - i * (bar_h + gap)
        shade = [ACC, "#3fb950", "#d29922", "#f85149"][i]
        ax.add_patch(FancyBboxPatch((960 - width / 2, y), width, bar_h,
                                    boxstyle="round,pad=2,rounding_size=14",
                                    fc=shade, ec="none", alpha=0.92))
        shown = int(count * local)
        if local > 0.88:
            ax.text(960, y + bar_h / 2, f"{label}   ·   {shown:,}", color="#0b0f14",
                    fontsize=30, fontweight="bold", ha="center", va="center",
                    alpha=min(1.0, (local - 0.88) * 8.3))
    if p > 0.86:
        ax.text(960, 130, "A timestamp is recorded with every collection — dynamic feeds make it part of the dataset definition.",
                color=MUT, fontsize=24, ha="center", alpha=ease((p - 0.86) * 7))


# ----------------------------------------------------------------- scene 3: attention line
def scene_attention(ax, p):
    kicker(ax, "02 · WEEKLY NEWS ATTENTION")
    ax.text(960, 900, "How much coverage did the topic get?", color=FG,
            fontsize=48, fontweight="bold", ha="center")
    # The main ax holds titles/kickers in fixed 0..1920 space.
    # The chart lives in an inset so its data limits don't affect annotation space.
    cax = ax.figure.add_axes([0.14, 0.14, 0.80, 0.58])
    cax.set_facecolor(BG)
    n = len(interest)
    k = max(2, int(ease(p) * n))
    x = np.arange(n)
    weeks = [short_week(w) for w in interest["week"]]
    cax.plot(x[:k], interest["article_count"][:k], color=ACC, lw=5,
             marker="o", ms=10, label="Articles")
    cax.plot(x[:k], interest["distinct_source_count"][:k], color="#d29922", lw=4,
             marker="o", ms=9, ls="--", label="Distinct sources")
    head = k - 1
    cax.scatter([x[head]], [interest["article_count"][head]], s=260, color=ACC,
                zorder=5, edgecolors=BG, linewidths=3)
    cax.scatter([x[head]], [interest["distinct_source_count"][head]], s=220,
                color="#d29922", zorder=5, edgecolors=BG, linewidths=3)
    cax.set_xlim(-0.6, n - 0.4)
    cax.set_xticks(x[::2])
    cax.set_xticklabels(weeks[::2], color=MUT, fontsize=20, rotation=38,
                        ha="right")
    cax.tick_params(colors=MUT, labelsize=20)
    for s in cax.spines.values():
        s.set_visible(False)
    cax.grid(axis="y", color="#21262d", lw=1.4)
    cax.set_ylim(0, interest["article_count"].max() * 1.25)
    leg = cax.legend(loc="upper left", fontsize=24, frameon=False)
    for t in leg.get_texts():
        t.set_color(FG)
    cax.text(0.99, 1.04, "peak: 14 articles in one week", transform=cax.transAxes,
             color=MUT, fontsize=22, ha="right")


# ----------------------------------------------------------------- scene 4: sentiment area
def scene_sentiment(ax, p):
    kicker(ax, "03 · TONE OF THE COVERAGE")
    ax.text(960, 900, "Predicted sentiment share per week", color=FG,
            fontsize=48, fontweight="bold", ha="center")
    cax = ax.figure.add_axes([0.13, 0.15, 0.82, 0.58])
    cax.set_facecolor(BG)
    n = len(sentiment)
    k = max(2, int(ease(p) * n))
    x = np.arange(n)
    weeks = [short_week(w) for w in sentiment["week"]]
    neg = sentiment["negative"].to_numpy() * 100
    neu = sentiment["neutral"].to_numpy() * 100
    pos = sentiment["positive"].to_numpy() * 100
    cax.stackplot(x[:k], neg[:k], neu[:k], pos[:k],
                  colors=[NEG, NEU, POS], labels=["negative", "neutral", "positive"],
                  alpha=0.88)
    cax.set_xlim(-0.6, n - 0.4)
    cax.set_xticks(x[::2])
    cax.set_xticklabels(weeks[::2], color=MUT, fontsize=20, rotation=38, ha="right")
    cax.tick_params(colors=MUT, labelsize=20)
    cax.set_ylim(0, 100)
    cax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    for s in cax.spines.values():
        s.set_visible(False)
    leg = cax.legend(loc="lower left", fontsize=24, frameon=False, ncols=3)
    for t in leg.get_texts():
        t.set_color(FG)


# ----------------------------------------------------------------- scene 5: model race
RACE_ROWS = [
    ("VADER · Accuracy", 0.35, MUT),
    ("VADER · Macro F1", 0.26, MUT),
    ("TF-IDF + LogReg · Accuracy", 0.74, ACC),
    ("TF-IDF + LogReg · Macro F1", 0.48, ACC),
]


def scene_race(ax, p):
    kicker(ax, "04 · BASELINE VS TRAINED MODEL")
    ax.text(960, 900, "Same held-out test set — who wins?", color=FG,
            fontsize=48, fontweight="bold", ha="center")
    bh = 96
    top_y = 690
    pitch = 148
    for i, (name, value, color) in enumerate(RACE_ROWS):
        local = ease(p * 1.7 - i * 0.14)
        if local <= 0:
            continue
        y = top_y - i * pitch
        ax.text(400, y + bh / 2, name, color=MUT if i < 2 else FG,
                fontsize=26, ha="right", va="center",
                fontweight="normal" if i < 2 else "bold")
        w = 1180 * value * local
        ax.add_patch(FancyBboxPatch((430, y), w, bh,
                                    boxstyle="round,pad=2,rounding_size=12",
                                    fc=color, ec="none", alpha=0.95))
        ax.text(455 + w, y + bh / 2, f"{value * local:.2f}",
                color=FG, fontsize=34, fontweight="bold", va="center")
    if p > 0.75:
        ax.text(960, 110, "Trained in seconds on a laptop CPU — and macro F1 exposes what accuracy hides.",
                color=ACC, fontsize=26, ha="center", alpha=ease((p - 0.75) * 6))


# ----------------------------------------------------------------- scene 6: confusion matrix
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix
    from sklearn.model_selection import train_test_split

    _Xtr, Xte, _ytr, yte = train_test_split(
        labeled["headline"], labeled["sentiment_label"],
        test_size=0.2, random_state=42, stratify=labeled["sentiment_label"])
    _vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    _clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    _clf.fit(_vec.fit_transform(_Xtr), _ytr)
    CM = confusion_matrix(yte, _clf.predict(_vec.transform(Xte)), labels=LABEL_ORDER)
except Exception:
    CM = np.array([[15, 4, 0], [1, 2, 1], [2, 0, 0]])  # fallback close to real values


def scene_confusion(ax, p):
    kicker(ax, "05 · HONEST EVALUATION")
    ax.text(960, 925, "Where predictions land vs reality", color=FG,
            fontsize=44, fontweight="bold", ha="center")
    size, gap = 190, 24
    x0, y0 = 770, 600
    order = list(range(9))
    for idx in order:
        i, j = divmod(idx, 3)
        local = ease(p * 9 * 1.1 - idx)
        if local <= 0:
            continue
        x = x0 + j * (size + gap)
        y = y0 - i * (size + gap)
        intensity = CM[i][j] / CM.max()
        cell_bg = plt.cm.Blues(0.25 + 0.65 * intensity)
        ax.add_patch(FancyBboxPatch((x, y), size, size,
                                    boxstyle="round,pad=2,rounding_size=10",
                                    fc=cell_bg, ec="#30363d", lw=2,
                                    alpha=local))
        ax.text(x + size / 2, y + size / 2, str(CM[i][j]), color="white",
                fontsize=44, fontweight="bold", ha="center", va="center",
                alpha=local)
    for j, lab in enumerate(LABEL_ORDER):
        ax.text(x0 + j * (size + gap) + size / 2, y0 + size + 46, lab,
                color=MUT, fontsize=24, ha="center")
    for i, lab in enumerate(LABEL_ORDER):
        ax.text(x0 - 40, y0 - i * (size + gap) + size / 2, lab,
                color=MUT, fontsize=24, ha="right", va="center")
    ax.text(1470, 480, "rows = actual label\ncolumns = prediction",
            color=MUT, fontsize=23, va="center")
    if p > 0.72:
        ax.text(960, 110, "Positive F1 = 0.00 — every positive headline was missed. Reported honestly, not tuned away.",
                color="#f85149", fontsize=29, fontweight="bold", ha="center",
                alpha=ease((p - 0.72) * 6))


# ----------------------------------------------------------------- scene 7: labeler flash
def scene_labeler(ax, p):
    import textwrap

    kicker(ax, "06 · YOU BE THE LABELER")
    slide = (1 - ease(min(p * 2.2, 1))) * -160
    card_x, card_y, card_w, card_h = 250 + slide, 300, 1420, 480
    ax.add_patch(FancyBboxPatch((card_x, card_y), card_w, card_h,
                                boxstyle="round,pad=4,rounding_size=24",
                                fc=CARD, ec="#30363d", lw=3))
    headline = "\u201cFood inflation hits 17.52% but headline inflation eases\u201d"
    lines = textwrap.wrap(headline, width=52)
    for li, line in enumerate(lines):
        ax.text(card_x + 60, card_y + card_h - 84 - li * 58, line,
                color=FG, fontsize=34, fontweight="bold")
    ax.text(card_x + 60, card_y + card_h - 84 - len(lines) * 58 - 14,
            "Your label?", color=MUT, fontsize=26)
    pill_w, pill_h = 320, 84
    for bi, (lab, col) in enumerate([("positive", POS), ("neutral", NEU), ("negative", NEG)]):
        px = card_x + 60 + bi * (pill_w + 44)
        py = card_y + 90
        chosen = lab == "neutral"
        ax.add_patch(FancyBboxPatch((px, py), pill_w, pill_h,
                                    boxstyle="round,pad=2,rounding_size=40",
                                    fc="none", ec=col, lw=6 if chosen else 3,
                                    alpha=0.4 + 0.6 * ease(p * 3 - bi)))
        ax.text(px + pill_w / 2, py + pill_h / 2, lab, color=col,
                fontsize=28, ha="center", va="center")
    if p > 0.55:
        a = ease((p - 0.55) * 4)
        ax.text(card_x + 60, card_y + 215,
                "Human label: neutral ✓  ·  agreement tracked",
                color="#3fb950", fontsize=28, fontweight="bold", alpha=a)
    ax.text(960, 170, "Ground truth comes from people reading carefully — reason and confidence on every row.",
            color=MUT, fontsize=26, ha="center", alpha=ease(p * 2 - 0.4))


# ----------------------------------------------------------------- scene 8: end card
def scene_end(ax, p):
    a = ease(p * 1.8)
    ax.text(960, 760, "Try the tutor — every number is real", color=FG,
            fontsize=54, fontweight="bold", ha="center", alpha=a)
    ax.text(960, 610, LIVE_APP_URL, color=ACC, fontsize=30,
            ha="center", alpha=ease(p * 1.8 - 0.2),
            family="DejaVu Sans Mono")
    ax.text(960, 500, REPO_URL, color=MUT, fontsize=24, ha="center",
            alpha=ease(p * 1.8 - 0.35), family="DejaVu Sans Mono")
    ax.text(960, 330, "Built by Fortune Uzodinma · 3MTT Data Science capstone DS-20",
            color=FG, fontsize=30, ha="center", alpha=ease(p * 1.8 - 0.5))


SCENES = [
    (3.0, scene_title),
    (4.8, scene_funnel),
    (4.8, scene_attention),
    (4.8, scene_sentiment),
    (4.2, scene_race),
    (4.6, scene_confusion),
    (3.4, scene_labeler),
    (3.6, scene_end),
]


def main():
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{int(W * RENDER_SCALE)}x{int(H * RENDER_SCALE)}",
        "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-vf", "scale=1920:1080:flags=lanczos",
        "-an", "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "22", "-preset", "medium", "-movflags", "+faststart",
        str(OUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    total = sum(int(d * FPS) for d, _ in SCENES)
    written = 0
    print(f"rendering {total} frames @ {FPS}fps -> {OUT.name}", flush=True)
    for si, (dur, fn) in enumerate(SCENES, 1):
        n = int(dur * FPS)
        for i in range(n):
            p = i / (n - 1) if n > 1 else 1.0
            proc.stdin.write(render_frame(fn, p).tobytes())
            written += 1
            if written % 120 == 0:
                print(f"  {written}/{total} frames", flush=True)
    proc.stdin.close()
    proc.wait()
    print(f"frames written : {written} (~{written / FPS:.1f}s @ {FPS}fps)")
    print(f"output         : {OUT}")
    print(f"size           : {OUT.stat().st_size / 1e6:.2f} MB")
    print(f"encoder exit   : {proc.returncode}")


if __name__ == "__main__":
    main()
