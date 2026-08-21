# Day 1 Feasibility Notes

## Purpose

These notes record the first local feasibility checks for DS-20. They are not final findings and must not be presented as the project's final analysis.

## GDELT Check

Tested query:

```text
sourcecountry:nigeria Nigeria (food OR "food prices" OR "cost of living" OR inflation OR rice OR bread)
```

Observed in the local comparison run:

- HTTP request eventually succeeded after GDELT rate-limit responses.
- 11 article records returned.
- 5 distinct domains returned.
- `seendate` values covered only approximately 90 minutes on 9 August 2026.
- The notebook's title-keyword screening found 0 matches for its initial topic-term list.
- The provisional gate therefore returned `REVIEW QUERY OR USE CONTINGENCY`.

Additional GDELT requests were temporarily rejected with HTTP 429. GDELT reported that requests should be limited to one every five seconds. This is an operational limitation of the current client, not proof that the topic has no coverage.

The sample also showed that `sourcecountry:nigeria` identifies the source-country classification and does not guarantee that every article is about Nigeria. Headlines must still be audited for topical relevance.

## Google News RSS Contingency Check

Tested feed:

```text
https://news.google.com/rss/search?q=Nigeria%20food%20prices%20cost%20of%20living&hl=en-NG&gl=NG&ceid=NG%3Aen
```

Observed:

- HTTP status: 200
- Items: 100
- Distinct source labels: 37
- Earliest item: 17 September 2025
- Latest item: 4 August 2026
- The results were predominantly relevant at headline level, but some were peripheral to food prices and cost of living.

Representative headlines included coverage of high food prices, food inflation, rising cooking costs, affordability, purchasing power, and cost-of-living pressure.

## Final Decision

GDELT remained unavailable across repeated attempts: HTTP 429 rate-limit responses were followed by read timeouts, and when a response did return, the strict query still failed the volume and time-coverage gate. The Google News RSS contingency is therefore confirmed as the single source for the core dataset.

The expanded multi-query RSS collection (see below) passed the volume, date-coverage, source-diversity, and relevance checks, and the dataset was frozen on that basis. This decision is final for the core sprint; any later switch would require a change-control entry.

Only one source may be used in the final core dataset. GDELT and Google News RSS must not be combined without a documented change to the plan.

## Expanded RSS Collection

To avoid treating one sparse RSS query as representative, the same Google News RSS source was queried with seven closely related phrases:

- Nigeria food prices
- Nigeria food inflation
- Nigeria cost of living
- Nigeria rice prices
- Nigeria food affordability
- Nigeria staple food prices
- Nigeria purchasing power food

The expanded collection produced:

- 676 feed items before deduplication
- 517 unique headline-source-date records after deduplication
- 185 records in the latest three-month window
- 111 records after the documented topic filter
- 51 distinct source labels
- Coverage from 15 May 2026 to 11 August 2026 in the local freeze

This is sufficient for the planned manual sentiment-label sample, but the 111 headlines still require manual review before labels are treated as ground truth. The seven queries remain one source strategy because they all use the same Google News RSS service.

## Contingency Caveats

- Google News RSS is a dynamic media-search snapshot, not an official food-price dataset.
- News coverage is not the same as public interest or household purchasing behaviour.
- Source rankings may be biased and syndicated stories may be repeated.
- RSS links may redirect, expire, or encounter paywalls.
- The feed's copyright notice requires checking reuse and redistribution conditions before publishing raw feed content.
- The project should retain only the fields needed for analysis and provide source and collection documentation.

## Day 2 Trigger

Before collecting the final dataset, run the selected source once more and record:

- final query or feed URL
- collection timestamp
- number of returned records
- date range
- distinct source count
- topical filtering rule
- number of records removed as irrelevant

Do not freeze the data until these values are recorded.

## References

- [GDELT DOC 2.0 API](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)
- [Google News RSS search feed](https://news.google.com/rss/search?q=Nigeria%20food%20prices%20cost%20of%20living&hl=en-NG&gl=NG&ceid=NG%3Aen)
