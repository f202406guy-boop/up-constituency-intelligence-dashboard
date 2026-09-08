"""
contest_risk / score_constituencies.py

Computes a transparent "contest-risk" score for each Uttar Pradesh assembly
constituency from two real historical result sets: the 2017 and 2022 UP
Legislative Assembly elections.

WHAT THIS DOES NOT DO
----------------------
It does not predict who wins the next election. It flags, using only
observed history, which seats look genuinely contestable (close, trending
closer, or already prone to flipping) versus which look like foregone
conclusions. It is a prioritization aid for where campaign/monitoring
attention might be worth spending, not a forecast.

DATA SOURCES (see docs/contest_risk.md for full provenance notes)
-------------------------------------------------------------------
- data/up_assembly_election_2017.csv
- data/up_assembly_election_2022.csv
Both were extracted from the constituency-wise results tables on the English
Wikipedia articles "2017 Uttar Pradesh Legislative Assembly election" and
"2022 Uttar Pradesh Legislative Assembly election" (fetched 2026-09-08).
Coverage is all 403 assembly constituencies for both years.

Known data gap: per-constituency turnout percentage is available for 2022
but NOT for 2017 on the source page (only phase/district-level turnout is
published there for 2017). Turnout-change is therefore NOT used as a risk
signal in this version, rather than approximating or fabricating a 2017
turnout figure. See docs/contest_risk.md.

SIGNALS USED (every one of these is a plain column or a two-column
difference from the CSVs above -- nothing here is fitted, learned, or
opaque)
-------------------------------------------------------------------
1. closeness_2022   -- how close the 2022 result was, as the gap between
                        the winner's and runner-up's share of votes polled
                        (winner_pct - runnerup_pct from the 2022 table).
                        Smaller gap = closer race = higher risk.

2. margin_trend      -- how that gap changed since 2017:
                        (margin_pct_2017 - margin_pct_2022).
                        Positive = the margin narrowed between cycles
                        (race getting closer) = higher risk.
                        Negative = the margin widened (race getting safer).

3. seat_turnover     -- binary flag: did the winning party in 2022 differ
                        from the winning party in 2017? A seat that already
                        changed hands once in the last cycle has demonstrated
                        it can flip, which this treats as a volatility signal
                        independent of the current margin.

COMPOSITE SCORE
----------------
risk_score (0-100, higher = more contestable / higher-risk for the
incumbent-holding party) is a fixed weighted average of three 0-100
sub-scores derived from the signals above. Weights are constants declared
below (WEIGHT_CLOSENESS, WEIGHT_TREND, WEIGHT_TURNOVER) -- change them
directly in this file if a different weighting is wanted; nothing is
hidden in a config file or learned from data.

    closeness_score = clip(100 - 2 * closeness_2022, 0, 100)
        # a dead-even (0-point) 2022 margin scores 100
        # a >=50-point 2022 margin scores 0

    trend_score = clip(50 + 2 * margin_trend, 0, 100)
        # no change in margin between cycles scores 50 (neutral)
        # every 1-point narrowing in margin adds 2 points of risk
        # every 1-point widening in margin removes 2 points of risk

    turnover_score = 100 if seat_turnover else 0

    risk_score = WEIGHT_CLOSENESS * closeness_score
               + WEIGHT_TREND     * trend_score
               + WEIGHT_TURNOVER  * turnover_score

No other input (candidate identity, caste, religion, party ideology, news,
polling) feeds this score. It is intentionally narrow.

USAGE
-----
    python contest_risk/score_constituencies.py
    python contest_risk/score_constituencies.py --top 20

Writes:
    contest_risk/output/contest_risk_scores.csv
    contest_risk/output/contest_risk_scores.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

# ---- scoring weights (must sum to 1.0) -------------------------------
WEIGHT_CLOSENESS = 0.5
WEIGHT_TREND = 0.3
WEIGHT_TURNOVER = 0.2

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUT_DIR = REPO_ROOT / "contest_risk" / "output"


def _clip(series: pd.Series, low: float, high: float) -> pd.Series:
    return series.clip(lower=low, upper=high)


def load_results(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_2017 = pd.read_csv(data_dir / "up_assembly_election_2017.csv")
    df_2022 = pd.read_csv(data_dir / "up_assembly_election_2022.csv")
    return df_2017, df_2022


def build_scores(df_2017: pd.DataFrame, df_2022: pd.DataFrame) -> pd.DataFrame:
    # Join on ac_no (assembly constituency number). Constituency boundaries
    # and numbering did not change between the 2017 and 2022 elections, so
    # this is a stable key. A handful of seats have minor transliteration
    # differences in ac_name between the two sources (e.g. "Bagpat" vs
    # "Baghpat") -- ac_no avoids that entirely.
    merged = df_2017.merge(
        df_2022,
        on="ac_no",
        suffixes=("_2017", "_2022"),
        validate="one_to_one",
    )

    merged["margin_pct_2017"] = merged["winner_pct_2017"] - merged["runnerup_pct_2017"]
    merged["margin_pct_2022"] = merged["winner_pct_2022"] - merged["runnerup_pct_2022"]
    merged["margin_trend"] = merged["margin_pct_2017"] - merged["margin_pct_2022"]
    merged["seat_turnover"] = (
        merged["winner_party_2017"].str.strip() != merged["winner_party_2022"].str.strip()
    )

    merged["closeness_score"] = _clip(100 - 2 * merged["margin_pct_2022"], 0, 100)
    merged["trend_score"] = _clip(50 + 2 * merged["margin_trend"], 0, 100)
    merged["turnover_score"] = merged["seat_turnover"].map({True: 100.0, False: 0.0})

    merged["risk_score"] = (
        WEIGHT_CLOSENESS * merged["closeness_score"]
        + WEIGHT_TREND * merged["trend_score"]
        + WEIGHT_TURNOVER * merged["turnover_score"]
    ).round(2)

    out = merged[
        [
            "ac_no",
            "ac_name_2022",
            "district_2022",
            "risk_score",
            "winner_party_2022",
            "winner_candidate_2022",
            "winner_pct_2022",
            "runnerup_party_2022",
            "runnerup_candidate_2022",
            "runnerup_pct_2022",
            "margin_votes_2022",
            "margin_pct_2022",
            "margin_pct_2017",
            "margin_trend",
            "seat_turnover",
            "closeness_score",
            "trend_score",
            "turnover_score",
        ]
    ].rename(
        columns={
            "ac_name_2022": "constituency",
            "district_2022": "district",
            "winner_party_2022": "winner_party_2022",
        }
    )

    out = out.sort_values("risk_score", ascending=False).reset_index(drop=True)
    out.insert(0, "risk_rank", out.index + 1)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--top", type=int, default=15, help="How many highest-risk seats to print to console."
    )
    args = parser.parse_args()

    df_2017, df_2022 = load_results(args.data_dir)
    scores = build_scores(df_2017, df_2022)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "contest_risk_scores.csv"
    json_path = args.output_dir / "contest_risk_scores.json"
    scores.to_csv(csv_path, index=False)
    scores.to_json(json_path, orient="records", indent=2)

    print(f"Scored {len(scores)} constituencies.")
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"\nTop {args.top} highest contest-risk seats:\n")
    cols = ["risk_rank", "constituency", "district", "risk_score",
            "winner_party_2022", "margin_pct_2022", "margin_trend", "seat_turnover"]
    print(scores[cols].head(args.top).to_string(index=False))


if __name__ == "__main__":
    main()
