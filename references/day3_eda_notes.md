# Day 3 Exploratory Notes

These are preliminary descriptive observations from the frozen collection. They are not final project conclusions because sentiment has not been labelled or modelled.

## Dataset Shape

- Frozen records: 111
- Date range: 15 May 2026 to 11 August 2026
- Weekly periods represented: 14
- Distinct source labels: 51
- Duplicate article URLs: 0
- Missing headlines: 0
- Missing dates: 0
- Missing source labels: 0

## Weekly Interest Proxy

- Highest article-count week: 13-19 July 2026, with 14 articles.
- Second-highest article-count week: 15-21 June 2026, with 12 articles.
- Lowest article-count week: 11-17 May 2026, with 3 articles.
- Another low-coverage week: 27 July-2 August 2026, with 4 articles.
- The highest distinct-source count was 10 during 15-21 June 2026.
- The first week, 11-17 May 2026, is partial because the three-month cutoff began on 14 May.
- The latest partial week contains 8 articles and should be interpreted cautiously because collection ended during that week.

## Source Concentration

The most frequent source labels were:

- The Guardian Nigeria News: 11 records
- Business News Nigeria: 9 records
- Independent Newspaper Nigeria: 7 records
- PM News Nigeria: 5 records
- Vanguard News: 5 records

The source distribution is not uniform. The project must describe this as source coverage, not a representative sample of all Nigerian media.

## Quality Notes

- The data was collected from seven closely related Google News RSS queries and deduplicated by article URL and headline-source-date combination.
- The topic filter is a screening rule, not a human sentiment or relevance label.
- Some headlines concern general cost of living, housing, fuel, or policy rather than food prices alone. This is allowed by the broader working topic but should be reviewed before sentiment labelling.
- Google News RSS results are dynamic and ranked, so the collection timestamp is part of the dataset definition.
- No sentiment interpretation should be added until the manual labelling rubric is applied.

## Generated Outputs

- `data/clean/articles_frozen.csv`
- `data/clean/weekly_interest_summary.csv`
- `reports/figures/weekly_article_volume.png`
- `reports/figures/weekly_distinct_sources.png`
