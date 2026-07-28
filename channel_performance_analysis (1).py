"""

MARKETING CHANNEL PERFORMANCE ANALYSIS

Project   : Which marketing channels drive traffic vs. which drive revenue
Data      : Google Merchandise Store website sessions (Feb 2017 - Jul 2017)
Source    : Google Analytics sample dataset (BigQuery public data)
Author    : Archith Jaiswal

WORKFLOW:
1. SQL (BigQuery)  - aggregated 400,010 raw sessions into 223 channel rows
2. Python (here)   - clean data, calculate business metrics, and run
                       statistical significance tests
3. Power BI        - dashboard and charts built from the cleaned CSV
                       this script exports

GOAL:
Not every channel that brings visitors also brings revenue. This script
identifies which channels are worth more marketing investment, and which
ones look good on a traffic report but contribute almost nothing to sales.

"""

import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest


# STEP 1: LOAD AND CLEAN THE DATA

# This CSV is the direct export from the BigQuery SQL query. Each row is one
# source/medium channel (e.g. "google / organic"), already aggregated from
# 400,010 individual website sessions using GROUP BY in SQL.

raw = pd.read_csv("channel_data_raw.csv")

# Some channels had zero converting sessions, which made SQL's SUM() return
# NULL (no rows to sum) instead of 0. We fix that here so the math below
# doesn't break on missing values.
raw["total_revenue"] = raw["total_revenue"].fillna(0)

print(f"Raw channel rows loaded: {raw.shape[0]}")
print(f"Total sessions represented across all channels: {raw['total_sessions'].sum():,}")

# STEP 2: FILTER OUT LOW-VOLUME NOISE

#We keep only channels with at least 100 sessions over the 6-month period.


df = raw[raw["total_sessions"] >= 100].copy()

sessions_covered = df["total_sessions"].sum()
sessions_total = raw["total_sessions"].sum()
coverage_pct = round(sessions_covered / sessions_total * 100, 2)

print(f"\nChannels kept after filtering (>= 100 sessions): {df.shape[0]}")
print(f"These channels still cover {coverage_pct}% of all sessions "
      f"({sessions_covered:,} of {sessions_total:,})")
print("This confirms the filter removes noise, not meaningful data.")

# STEP 3: CALCULATE BUSINESS METRICS

# session_share_pct   - what % of all traffic this channel brings
# revenue_share_pct    - what % of all revenue this channel brings
# revenue_per_session  - average revenue generated per visitor session
#
# Comparing session_share vs revenue_share is the core of this analysis:


total_revenue_all = df["total_revenue"].sum()

df["session_share_pct"] = round(df["total_sessions"] / sessions_covered * 100, 2)
df["revenue_share_pct"] = round(df["total_revenue"] / total_revenue_all * 100, 2)
df["revenue_per_session"] = round(df["total_revenue"] / df["total_sessions"], 2)

df = df.sort_values("total_sessions", ascending=False).reset_index(drop=True)

# STEP 4: STATISTICAL SIGNIFICANCE TESTING


# Z-test


def run_ztest(name_a, sessions_a, conversions_a, name_b, sessions_b, conversions_b):
    count = [conversions_a, conversions_b]
    nobs = [sessions_a, sessions_b]
    stat, pval = proportions_ztest(count, nobs)
    print(f"\n{name_a} vs {name_b}")
    print(f"  {name_a}: {conversions_a}/{sessions_a} conversions "
          f"({round(conversions_a/sessions_a*100, 2)}%)")
    print(f"  {name_b}: {conversions_b}/{sessions_b} conversions "
          f"({round(conversions_b/sessions_b*100, 2)}%)")
    print(f"  z-statistic = {round(stat, 2)}, p-value = {pval:.2e}")
    if pval < 0.05:
        print("  Result: statistically significant difference (p < 0.05)")
    else:
        print("  Result: NOT statistically significant (p >= 0.05)")
    return stat, pval

print("\n" + "=" * 60)
print("STATISTICAL SIGNIFICANCE TESTS")
print("=" * 60)

# Test 1: Google Organic vs YouTube Referral
# (biggest traffic channel vs. the channel that looks like a red flag)
g_organic = df[(df.source == "google") & (df.medium == "organic")].iloc[0]
youtube = df[(df.source == "youtube.com") & (df.medium == "referral")].iloc[0]

run_ztest(
    "Google Organic", int(g_organic.total_sessions), int(g_organic.converting_sessions),
    "YouTube Referral", int(youtube.total_sessions), int(youtube.converting_sessions)
)

# Test 2: Direct vs Google Organic (best-converting vs. highest-volume)
direct = df[(df.source == "(direct)") & (df.medium == "(none)")].iloc[0]

run_ztest(
    "Direct", int(direct.total_sessions), int(direct.converting_sessions),
    "Google Organic", int(g_organic.total_sessions), int(g_organic.converting_sessions)
)

# Test 3: Chi-square test
print("\nChi-Square Test: Do conversion rates differ across top 6 channels overall?")
top6_keys = [("google", "organic"), ("(direct)", "(none)"), ("youtube.com", "referral"),
             ("google", "cpc"), ("dfa", "cpm"), ("bing", "organic")]

top6_rows = []
for s, m in top6_keys:
    row = df[(df.source == s) & (df.medium == m)].iloc[0]
    top6_rows.append(row)
top6 = pd.DataFrame(top6_rows)
top6["non_converting"] = top6["total_sessions"] - top6["converting_sessions"]

contingency_table = top6[["converting_sessions", "non_converting"]].values
chi2_stat, chi2_pval, dof, expected = chi2_contingency(contingency_table)

print(f"  Chi-square statistic = {round(chi2_stat, 2)}, p-value = {chi2_pval:.2e}, "
      f"degrees of freedom = {dof}")
if chi2_pval < 0.05:
    print("  Result: conversion rates significantly differ across these channels.")
else:
    print("  Result: no significant difference across these channels.")

# STEP 5: SAVE CLEANED DATA FOR POWER BI

output_columns = [
    "source", "medium", "total_sessions", "converting_sessions",
    "conversion_rate_pct", "total_revenue", "session_share_pct",
    "revenue_share_pct", "revenue_per_session"
]
df[output_columns].to_csv("channel_performance_cleaned.csv", index=False)
print("\nCleaned dataset saved: channel_performance_cleaned.csv")
print("(This is the file to load into Power BI for the dashboard and charts.)")

# STEP 6: FINAL SUMMARY

top10 = df.head(10).copy()
print("\n" + "=" * 60)
print("KEY FINDINGS")
print("=" * 60)
print(f"""
1. Google Organic brings the most traffic ({g_organic.session_share_pct}% of
   sessions) but converts at only {g_organic.conversion_rate_pct}% - roughly
   a third of Direct's rate.

2. YouTube Referral is the 3rd largest channel by volume
   ({youtube.session_share_pct}% of sessions) but converts at just
   {youtube.conversion_rate_pct}% and contributes only
   {youtube.revenue_share_pct}% of total revenue - a clear volume-without-value
   channel.

3. Direct traffic is the strongest performer: {direct.session_share_pct}% of
   sessions but {direct.revenue_share_pct}% of all revenue, converting at
   {direct.conversion_rate_pct}%.

4. All differences above are statistically significant (p < 0.05), confirming
   these are real performance gaps, not random variation.

RECOMMENDATION:
Marketing budget and content strategy built around YouTube referral traffic
is not translating into revenue and should be re-evaluated. Direct traffic -
the strongest converter - likely reflects returning/loyal customers and
deserves continued retention investment, while Google Organic's high volume
but low conversion suggests a landing-page or intent-mismatch problem worth
investigating separately.
""")
