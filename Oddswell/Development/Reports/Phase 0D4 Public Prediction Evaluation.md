---
tags:
  - development
  - simulation
  - prediction
  - evaluation
status: complete
---

# Phase 0D.4 Public Prediction Evaluation

Version `phase0d4-v1` evaluates public-only pregame predictions after **15 warm-up seasons** on a locked **5-season / 100-game holdout**. Cost: **$0.00**.

## Locked holdout

| Model | Games | Accuracy | Brier | Log loss | 5-bin ECE | Brier skill vs 50% |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed 50% | 100 | 56.0% | 0.2500 | 0.6931 | 0.0600 | +0.0% |
| Public-history Elo | 100 | 53.0% | 0.2417 | 0.6765 | 0.0602 | +3.3% |
| Elo + public availability/rotation | 100 | 51.0% | 0.2416 | 0.6762 | 0.0617 | +3.3% |

**Result:** Elo + public availability/rotation beat the fixed 50% baseline on locked-holdout Brier score.

## Games with a published absence

| Model | Games | Accuracy | Brier | Log loss | 5-bin ECE |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed 50% | 34 | 55.9% | 0.2500 | 0.6931 | 0.0588 |
| Public-history Elo | 34 | 55.9% | 0.2363 | 0.6656 | 0.1004 |
| Elo + public availability/rotation | 34 | 55.9% | 0.2367 | 0.6662 | 0.1025 |

## Leakage and timing boundary

- Each prediction is hashed before the authoritative game transition runs.
- The commitment contains only version, season/game number, team names, public pregame standings, rest days, public roster ratings, published availability, projected minutes, and fixed-model probabilities.
- Seeds, RNG state, scores, winners, replay/action tapes, hidden fatigue, injury risk internals, future games, economy data, and user data are excluded.
- **100/100** holdout commitments verify and link afterward to a winner and replay SHA-256.

## Interpretation

This is an engineering evaluation of fictional simulator data, not a wagering product or evidence of real-world predictive power. The holdout is not used for tuning. A failed baseline is retained as valid evidence.
