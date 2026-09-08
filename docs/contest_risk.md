# Contest-Risk Layer

Status: MVP implemented (Sep 2026). This is layer 1 of the four planned
layers described in the root README. Layers 2-4 (candidate transparency,
sentiment monitoring, response-recommendation) are **not built** -- this
document only covers what exists today.

## What this layer does

It scores each Uttar Pradesh assembly constituency on how "contestable" it
looks, using only historical result data from the 2017 and 2022 Legislative
Assembly elections. A high score means the seat has been close, has been
getting closer, and/or has already changed hands once recently -- i.e. it
looks worth paying attention to. A low score means the seat has historically
been a lopsided, stable result for one party.

This is **not** a prediction of the next election's outcome. It is a
backward-looking prioritization signal built entirely from public historical
results, meant to help route limited analysis/monitoring effort toward seats
where the history suggests a real contest, rather than seats that have been
foregone conclusions for two straight cycles.

## Data coverage

- **403 of 403** UP assembly constituencies, for **both** the 2017 and 2022
  elections.
- Source: the constituency-wise results tables published on the English
  Wikipedia articles
  ["2017 Uttar Pradesh Legislative Assembly election"](https://en.wikipedia.org/wiki/2017_Uttar_Pradesh_Legislative_Assembly_election)
  and
  ["2022 Uttar Pradesh Legislative Assembly election"](https://en.wikipedia.org/wiki/2022_Uttar_Pradesh_Legislative_Assembly_election),
  fetched 2026-09-08. These tables are themselves compiled from Election
  Commission of India (ECI) results.
- Raw extracted data lives at `data/up_assembly_election_2017.csv` and
  `data/up_assembly_election_2022.csv`. Each row is one constituency, one
  year, with: constituency number and name, district, turnout % (2022 only,
  see gap below), winner candidate/party/votes/vote share, runner-up
  candidate/party/votes/vote share, and winning margin in votes.
- Constituencies are joined across years by assembly constituency number
  (`ac_no`), which did not change between the 2017 and 2022 elections. A
  handful of seats have minor transliteration differences in name between
  the two source tables (e.g. "Bagpat" vs "Baghpat", "Dholana" vs
  "Dhaulana") -- these are the same seats and are handled correctly by the
  numeric join, not treated as different constituencies.

### Known gap: no per-constituency 2017 turnout

The 2022 Wikipedia results table publishes turnout % per constituency. The
2017 table does not -- on that page, turnout is only published at the
phase/district level, not per seat. Rather than approximate or backfill a
number that isn't actually in the source, **turnout change is not used as a
risk signal in this version.** If a reliable per-constituency 2017 turnout
figure is sourced later (e.g. from ECI's own statistical reports), it should
be added as a fourth signal.

### Scope limitation

Only 2017 and 2022 are used (two data points per constituency). The root
README references "three election cycles" as an eventual goal; adding 2012
results would let the trend calculation use two intervals instead of one
and would meaningfully strengthen the trend signal. That is unbuilt --
this MVP uses exactly the two cycles described above and does not claim
three-cycle coverage.

## How the score is computed

Everything the score is built from is a plain column, or a simple
subtraction between two columns, in the two CSVs above. There is no model
fitting, no learned weights, no external or unstated inputs. The full
implementation is in `contest_risk/score_constituencies.py`; the summary:

**1. Closeness of the 2022 result** (`closeness_2022`)
The gap between the winner's and runner-up's share of votes polled in 2022
(`winner_pct - runnerup_pct`). A smaller gap means a closer, more
contestable race.

**2. Margin trend between 2017 and 2022** (`margin_trend`)
`margin_pct_2017 - margin_pct_2022`. Positive means the margin narrowed
between the two elections (race getting closer); negative means it widened
(race getting safer for the incumbent party).

**3. Seat turnover** (`seat_turnover`)
Whether the party that won the seat in 2022 differs from the party that won
it in 2017. A seat that already flipped once in the last cycle has
demonstrated volatility, independent of how large this cycle's margin was.

These three signals are each rescaled to a 0-100 sub-score and combined as a
fixed weighted average into the final `risk_score` (0-100, higher = more
contestable):

| Sub-score | Formula | Weight |
|---|---|---|
| `closeness_score` | `clip(100 - 2 * closeness_2022, 0, 100)` | 0.5 |
| `trend_score` | `clip(50 + 2 * margin_trend, 0, 100)` | 0.3 |
| `turnover_score` | `100` if seat changed hands, else `0` | 0.2 |

The weights (0.5 / 0.3 / 0.2) are constants at the top of
`score_constituencies.py`, not a fitted or tuned model -- change them
directly in the file to explore other weightings. Nothing about the score
is hidden: every intermediate sub-score is included in the output alongside
the final score so any number can be traced back to the underlying votes
and percentages.

## Explicit exclusions

By design, this scoring uses **only** vote totals, vote shares, party
labels, and margins from official-derived historical results. It does not
use, and never will use, candidate caste, religion, or any personal-identity
attribute, nor does it apply any party-favorable or party-unfavorable
framing -- every party is scored by the same formula against the same
signals. Candidate names and party abbreviations appear only because they
are part of the sourced results table; the score itself does not weight for
or against any party or individual.

## Output

Running `python contest_risk/score_constituencies.py` writes:

- `contest_risk/output/contest_risk_scores.csv`
- `contest_risk/output/contest_risk_scores.json`

Each row/record contains: constituency, district, `risk_score`, `risk_rank`,
the 2022 winner/runner-up and their vote shares, the 2022 margin (votes and
%), the 2017 margin %, `margin_trend`, `seat_turnover`, and each of the
three sub-scores that fed the final score.

## What's not built yet

This is layer 1 of 4. As described in the root README:

- **Candidate transparency layer** (ADR/affidavit parsing) -- not started.
- **News & sentiment monitoring** -- not started.
- **Response-recommendation layer** -- not started.

No claims are made here about those layers' scope, timeline, or design
beyond what the root README already states.
