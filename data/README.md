# Data

Ingestion and storage for ECI historical results, ADR/affidavit filings, and news/sentiment sources.

## Currently populated

- `up_assembly_election_2017.csv` -- all 403 UP assembly constituencies,
  2017 election results (winner/runner-up candidate, party, votes, vote
  share, margin). Extracted from the Wikipedia results table for the 2017
  election (fetched 2026-09-08).
- `up_assembly_election_2022.csv` -- same, for the 2022 election, plus
  per-constituency turnout %, which is not available for 2017 on the same
  source page.

These feed `contest_risk/score_constituencies.py`. See
[`docs/contest_risk.md`](../docs/contest_risk.md) for full provenance,
column definitions, and known gaps.

## Not yet implemented

ADR/affidavit filings, news/sentiment sources -- these belong to the
candidate transparency and sentiment monitoring layers, which are not
built yet.
