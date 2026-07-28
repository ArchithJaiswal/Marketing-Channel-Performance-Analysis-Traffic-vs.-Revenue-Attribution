# Marketing Channel Performance Analysis: Traffic vs. Revenue Attribution

## Overview
An end-to-end analysis of 400,000+ website sessions from the Google Merchandise Store (Google Analytics sample dataset) to answer a core marketing question: **which traffic channels are actually worth the investment, and which ones bring visitors without bringing revenue?**

Marketing teams often measure channel success by traffic volume alone. This project shows why that's misleading — some channels bring huge visitor numbers but almost no revenue, while others convert far above average with less traffic. The analysis quantifies that gap and translates it into a clear budget-reallocation recommendation.

## Business Problem
Not all website traffic is equal. A channel bringing 40% of all visitors but only 15% of revenue is a poor use of marketing spend compared to a channel bringing 35% of visitors but 67% of revenue. Without separating **volume** from **value**, marketing budgets get allocated based on vanity metrics instead of business impact.

## Tools & Workflow
**SQL (Google BigQuery) → Python (pandas, scipy, statsmodels) → Power BI**

1. **SQL**: Queried 6 months of raw session-level data (400,010 sessions) from BigQuery's public Google Analytics sample dataset, aggregating by traffic source and medium using `GROUP BY`, `COUNTIF`, and `SUM`.
2. **Python**: Cleaned the aggregated data, filtered out low-volume noise channels (<100 sessions) while retaining 99.49% of total session volume, calculated session-share/revenue-share/revenue-per-session metrics, and ran statistical significance tests (two-proportion z-tests, chi-square test) to confirm channel performance differences were real, not random variation.
3. **Power BI**: Built an interactive single-page dashboard with KPI cards, a session-share-vs-revenue-share comparison chart, a conversion-rate ranking chart, a full channel detail table, and a medium slicer for filtering.

## Key Insights
- **YouTube referral traffic**: 10.2% of all sessions, but only 0.01% of revenue — a clear volume-without-value channel.
- **Direct traffic**: just 35% of sessions, but 67% of total revenue — the strongest-converting channel, likely driven by returning/loyal customers.
- **Google Organic**: the single largest channel by volume (42% of sessions) but converts at less than a third of Direct's rate.
- All conversion-rate gaps were statistically significant (p < 0.05, confirmed via z-tests and chi-square testing), ruling out random chance as the explanation.

## Recommendation
Marketing spend and content strategy anchored on YouTube referral traffic should be re-evaluated given its negligible revenue contribution. Direct traffic warrants continued retention investment, while Google Organic's high volume but low conversion suggests a landing-page or search-intent mismatch worth investigating separately.

## Data Notes
- Source data covers August 2016–August 2017; this analysis uses the February–July 2017 window (6 months).
- Revenue values in the raw GA schema are stored in micros (1,000,000 micros = 1 currency unit) and were converted during SQL extraction.
- 189 of 223 raw channel rows were filtered out for having fewer than 100 sessions over the 6-month period; these represented only 0.51% of total traffic and were excluded to avoid drawing conclusions from statistically unreliable sample sizes.

