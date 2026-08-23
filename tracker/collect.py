#!/usr/bin/env python3
"""Weekly live refresh of the interest-tracker rolling dataset.

Same RSS queries, parsing, and topic filter as the capstone notebook,
but merged into a rolling archive instead of overwriting the frozen copy.
Only derived headline metadata is committed; raw RSS XML is never stored
by this script.

Usage:
    python tracker/collect.py            # fetch, merge, write tracker/data/
    python tracker/collect.py --dry-run  # fetch only, don't write
"""

import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote, urlparse

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
TRACKER_DATA = ROOT / "tracker" / "data"

RSS_QUERIES = [
    "Nigeria food prices",
    "Nigeria food inflation",
    "Nigeria cost of living",
    "Nigeria rice prices",
    "Nigeria food affordability",
    "Nigeria staple food prices",
    "Nigeria purchasing power food",
]

FOOD_TERMS = [
    "food", "rice", "bread", "cooking", "staple", "grocery", "diet",
    "maize", "yam", "beans", "food security", "food crisis",
]
PRICE_TERMS = [
    "price", "prices", "inflation", "affordability", "cost",
    "expensive", "scarcity", "shortage", "market", "hardship",
]
TOPIC_PHRASES = [
    "cost of living", "purchasing power", "food inflation",
    "food prices", "food crisis", "food affordability",
]
HEADERS = {"User-Agent": "3mtt-sentiment-tracker/1.0 (+https://github.com/Braingenius2/sentiment-driven-interest-tracker)"}


def contains_any(text: str, terms: list[str]) -> bool:
    t = text.lower()
    return any(term in t for term in terms)


def fetch_feeds() -> list[dict]:
    """Fetch the 7 RSS feeds sequentially (rate-limited)."""
    all_rows: list[dict] = []
    for query in RSS_QUERIES:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-NG&gl=NG&ceid=NG%3Aen"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        for item in root.findall("./channel/item"):
            src = item.find("source")
            src_label = src.text if src is not None else ""
            src_url = (src.attrib.get("url", "") if src is not None else "")
            raw_title = item.findtext("title", default="")
            suffix = f" - {src_label}"
            headline = raw_title[:-len(suffix)] if src_label and raw_title.endswith(suffix) else raw_title
            all_rows.append({
                "query": query,
                "feed_url": url,
                "article_url": item.findtext("link", default=""),
                "headline": re.sub(r"\s+", " ", headline.strip()),
                "headline_raw": raw_title,
                "pub_date_raw": item.findtext("pubDate", default=""),
                "source_label": src_label,
                "source_domain": urlparse(src_url).netloc.lower(),
            })
        time.sleep(1)
    return all_rows


def build_frame(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["pub_datetime"] = pd.to_datetime(df["pub_date_raw"], errors="coerce", utc=True)
    df["collection_time"] = pd.Timestamp.now(tz="UTC")
    df["headline_key"] = (
        df["headline"].str.lower()
        .str.replace(r"[^a-z0-9 ]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True).str.strip()
    )
    df = df.dropna(subset=["headline", "pub_datetime"])
    df = df[df["headline"].str.strip() != ""]
    df = df.drop_duplicates(subset=["article_url"]).copy()
    df = df.drop_duplicates(subset=["headline_key", "source_label", "pub_datetime"]).copy()
    df["has_food_term"] = df["headline"].map(lambda v: contains_any(v, FOOD_TERMS))
    df["has_price_term"] = df["headline"].map(lambda v: contains_any(v, PRICE_TERMS))
    df["has_topic_phrase"] = df["headline"].map(lambda v: contains_any(v, TOPIC_PHRASES))
    df["is_topic_relevant"] = (df["has_food_term"] & df["has_price_term"]) | df["has_topic_phrase"]
    return df[df["is_topic_relevant"]].copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("[tracker] collecting live feeds...")
    rows = fetch_feeds()
    fresh = build_frame(rows)
    print(f"[tracker] fetched {len(rows)} raw items -> {len(fresh)} relevant in-window candidates")

    existing_path = TRACKER_DATA / "articles_live.csv"
    if existing_path.exists():
        existing = pd.read_csv(existing_path)
        if "pub_datetime" in existing.columns:
            existing["pub_datetime"] = pd.to_datetime(existing["pub_datetime"], errors="coerce", utc=True)
        if "collection_time" in existing.columns:
            existing["collection_time"] = pd.to_datetime(existing["collection_time"], errors="coerce", utc=True)
        combined = pd.concat([existing, fresh], ignore_index=True)
        combined = combined.dropna(subset=["headline", "pub_datetime"])
        combined["headline_key"] = (
            combined["headline"].str.lower()
            .str.replace(r"[^a-z0-9 ]", "", regex=True)
            .str.replace(r"\s+", " ", regex=True).str.strip()
        )
        combined = combined.drop_duplicates(subset=["article_url"]).copy()
        combined = combined.drop_duplicates(subset=["headline_key", "source_label", "pub_datetime"]).copy()
        combined = combined.sort_values("pub_datetime").reset_index(drop=True)
    else:
        combined = fresh.sort_values("pub_datetime").reset_index(drop=True) if not fresh.empty else fresh

    if args.dry_run:
        print(f"[tracker] dry-run: would write {len(combined)} rows")
        print(f"[tracker] dry-run: would write {len(combined)} rows (not writing)")
        return

    TRACKER_DATA.mkdir(parents=True, exist_ok=True)

    # Only write relevant rolling records
    combined.to_csv(existing_path, index=False)
    print(f"[tracker] wrote {len(combined)} rows -> {existing_path}")

    # Weekly summary (all-time; app applies 3-month window)
    combined["pub_datetime"] = pd.to_datetime(combined["pub_datetime"], errors="coerce", utc=True)
    combined["week"] = combined["pub_datetime"].dt.tz_localize(None).dt.to_period("W").astype(str)
    weekly = (
        combined.groupby("week")
        .agg(article_count=("article_url", "nunique"), distinct_source_count=("source_label", "nunique"))
        .reset_index().sort_values("week")
    )
    weekly_path = TRACKER_DATA / "weekly_interest_live.csv"
    weekly.to_csv(weekly_path, index=False)
    print(f"[tracker] weekly periods: {len(weekly)} -> {weekly_path}")

    last = {
        "last_collected_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "rows": int(len(combined)),
        "distinct_sources": int(combined["source_label"].nunique()) if not combined.empty else 0,
        "oldest": combined["pub_datetime"].min().isoformat() if not combined.empty else None,
        "newest": combined["pub_datetime"].max().isoformat() if not combined.empty else None,
        "weekly_periods": int(len(weekly)),
    }
    (TRACKER_DATA / "last_collected.json").write_text(json.dumps(last, indent=2), encoding="utf-8")
    print(json.dumps(last, indent=2))


if __name__ == "__main__":
    main()
