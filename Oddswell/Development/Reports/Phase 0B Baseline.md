---
tags:
  - development
  - simulation
  - validation
status: active
---

# Phase 0B Baseline Report

Reproducible analysis of **1,000 games** using seeds `0`–`999`, alternating home assignment, and engine `phase0b-v1`.

**Calibration result: 9/9 checks passed.**

## Calibration checks

| Metric | Result | Target | Status |
| --- | ---: | --- | --- |
| Average team score | 92.12 | 85–120 points | ✅ Pass |
| Total possessions | 206.62 | 190–230 per game | ✅ Pass |
| Field-goal percentage | 38.3% | 38–55% | ✅ Pass |
| Three-point attempt share | 26.9% | 10–45% | ✅ Pass |
| Turnovers | 9.19 | 5–25 per team | ✅ Pass |
| Home win rate | 50.0% | 43–57% | ✅ Pass |
| Overtime rate | 2.8% | 0–15% | ✅ Pass |
| Maximum player shot attempts | 23.57 | 0–30 per game | ✅ Pass |
| Maximum player rebounds | 16.79 | 0–20 per game | ✅ Pass |

## Team results

| Team | Wins | Win rate | PPG | Possessions | FG% | 3PA share | Turnovers | OREB | DREB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Harbor City Waves | 472 | 47.2% | 91.47 | 103.31 | 38.1% | 27.0% | 9.20 | 15.78 | 51.17 |
| Mesa Vista Sol | 528 | 52.8% | 92.76 | 103.31 | 38.6% | 26.7% | 9.18 | 15.98 | 51.84 |

## Player results

| Player | Team | PPG | FGA | FG% | 3P% | Passes | Turnovers | Rebounds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Jalen Cross | Harbor City Waves | 20.49 | 22.33 | 40.9% | 31.5% | 6.26 | 1.69 | 10.86 |
| Dorian Pike | Harbor City Waves | 19.98 | 23.02 | 39.1% | 29.8% | 5.62 | 1.79 | 13.16 |
| Nico Reyes | Mesa Vista Sol | 19.73 | 21.56 | 41.0% | 31.2% | 6.77 | 1.69 | 10.80 |
| Roman Voss | Mesa Vista Sol | 19.33 | 23.43 | 37.8% | 27.2% | 5.50 | 1.91 | 16.25 |
| Tariq Stone | Mesa Vista Sol | 18.89 | 21.65 | 39.3% | 30.4% | 6.47 | 1.83 | 12.63 |
| Cal Brooks | Mesa Vista Sol | 18.60 | 23.57 | 36.6% | 24.9% | 5.21 | 1.91 | 16.79 |
| Kellan Shore | Harbor City Waves | 17.76 | 22.37 | 36.6% | 24.8% | 5.98 | 1.92 | 15.83 |
| Andre North | Harbor City Waves | 17.12 | 22.68 | 35.1% | 23.8% | 5.55 | 1.97 | 16.70 |
| Eli Mercer | Mesa Vista Sol | 16.21 | 19.16 | 38.4% | 28.5% | 8.34 | 1.84 | 11.35 |
| Micah Vale | Harbor City Waves | 16.12 | 18.80 | 38.8% | 29.1% | 8.28 | 1.83 | 10.40 |

## Interpretation

These are engineering guardrails, not final league-balance promises. Passing every broad check means the baseline is stable enough for deeper analysis; it does not prove realism or entertainment quality.

The next comparison should run the first LLM policy through the same action contract and measure it against this exact baseline.
