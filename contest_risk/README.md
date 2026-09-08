# Contest-Risk Model

Status: MVP implemented. Scores all 403 UP assembly constituencies using
historical margin closeness, margin trend, and seat-turnover signals from
the 2017 and 2022 Legislative Assembly elections.

Run it:

```
python contest_risk/score_constituencies.py
```

Full methodology, data coverage, and known limitations:
[`docs/contest_risk.md`](../docs/contest_risk.md).

Output: `contest_risk/output/contest_risk_scores.csv` / `.json`.
