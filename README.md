# UP Constituency Intelligence Dashboard

**Status: In Progress — Sep 2026–**

A four-layer analytics system for reading India's largest, most consequential electoral battleground before it happens. 403 assembly constituencies. Three election cycles of history. One dashboard that turns raw electoral signal into a structured, defensible read on where a race actually stands — built the way a strategist would want it, not the way a headline would.

Uttar Pradesh alone decides more parliamentary seats than most countries have. Every cycle, campaigns make high-stakes resourcing calls off partial data, gut instinct, and news cycles that move faster than ground truth. This project's bet: the signal to do better already exists in public records, election commission archives, and news coverage — it's just never been assembled into one structured, constituency-level system. This dashboard is that assembly.

## Why this, why now

Governance and electoral consulting increasingly runs on the same discipline as top-tier management consulting: structured problem-solving, hypothesis-driven analysis, and the ability to turn messy, high-volume data into a recommendation someone can act on under time pressure. This project is a deliberate rep of that muscle — applied to the single largest, densest electoral dataset in the country.

## The four layers

**1. Contest-risk model**
Mines historical ECI margin trends, anti-incumbency signals, and turnout volatility across the last three election cycles for all ~403 UP assembly constituencies to flag which seats are genuinely contestable versus which are foregone conclusions — the difference between spending a campaign's limited time and money well or badly.

**2. Candidate transparency layer**
Parses ADR/affidavit filings to flag anomalies — asset growth inconsistent with declared income, criminal case history, education record mismatches — turning scattered public disclosure documents into a queryable transparency layer.

**3. News & sentiment monitoring**
Tracks real-time media coverage per candidate and constituency, with spike detection on sentiment shifts, so a shift in public mood shows up as a signal instead of getting noticed three news cycles late.

**4. Response-recommendation layer**
When sentiment turns negative on a tracked issue, surfaces the issue and suggested messaging directions **to a human communications team** for review and action. This is explicitly a decision-support layer, not an automation layer: it recommends, humans decide and execute. No automated posting, no bot accounts, no coordinated account activity of any kind — that's a hard boundary for this project, not a limitation to route around.

## Tech stack

Python for the core pipeline; scraping/ETL, NLP/sentiment modeling, and dashboard framework choices are still being finalized as the build progresses. PostgreSQL for storage. This section gets filled in with real specifics — not placeholders — as each layer ships.

## Project status

This is being actively built, one layer at a time. Nothing is published
here until it is real, sourced, and reproducible from the code and data in
this repo.

**Layer 1 (contest-risk model): MVP implemented.** Covers all 403 UP
assembly constituencies using real 2017 and 2022 election results
(Wikipedia-sourced, ECI-derived). Scores each seat on historical margin
closeness, margin trend, and seat turnover between the two cycles -- see
[`docs/contest_risk.md`](docs/contest_risk.md) for the full method, data
provenance, and explicit limitations (notably: only two election cycles so
far, and no per-constituency 2017 turnout figure exists in the source, so
turnout-change is not yet a signal).

**Layers 2-4 (candidate transparency, sentiment monitoring,
response-recommendation): not started.** No code, data, or design beyond
the one-paragraph descriptions above exists for these yet.

## Repository structure

```
contest_risk/          # Layer 1 — historical margin/anti-incumbency/turnout model
candidate_transparency/# Layer 2 — ADR/affidavit anomaly detection
sentiment_monitor/      # Layer 3 — news + sentiment tracking, spike detection
response_layer/         # Layer 4 — human-facing recommendation surface
data/                   # Data ingestion and storage
docs/                   # Design notes and write-ups
```
