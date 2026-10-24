---
tags:
  - development
  - simulation
  - season
status: active
---

# Phase 0D Schedule and Standings

Deterministic **20-game** first league run using seeds `10000`-`10019`, league `phase0d-v1`, and brain `baseline-v2`.

## Standings

| Rank | Team | W | L | Win% | PF | PA | Diff |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Harbor City Waves | 12 | 8 | 60.0% | 1961 | 1940 | +21 |
| 2 | Mesa Vista Sol | 8 | 12 | 40.0% | 1940 | 1961 | -21 |

## Schedule and results

| Game | Seed | Away | Score | Home | Winner | Replay hash |
| ---: | ---: | --- | ---: | --- | --- | --- |
| 1 | 10000 | Mesa Vista Sol | 92-99 | Harbor City Waves | Harbor City Waves | `78cd88e1eff7` |
| 2 | 10001 | Harbor City Waves | 82-112 | Mesa Vista Sol | Mesa Vista Sol | `c545d0ef1007` |
| 3 | 10002 | Mesa Vista Sol | 111-107 | Harbor City Waves | Mesa Vista Sol | `d19c2bb7b820` |
| 4 | 10003 | Harbor City Waves | 101-98 | Mesa Vista Sol | Harbor City Waves | `3ea67be29fc2` |
| 5 | 10004 | Mesa Vista Sol | 102-109 | Harbor City Waves | Harbor City Waves | `a780e3ef191d` |
| 6 | 10005 | Harbor City Waves | 115-110 | Mesa Vista Sol | Harbor City Waves | `49810d52b379` |
| 7 | 10006 | Mesa Vista Sol | 92-93 | Harbor City Waves | Harbor City Waves | `e33391e9bc88` |
| 8 | 10007 | Harbor City Waves | 110-84 | Mesa Vista Sol | Harbor City Waves | `859d24195c79` |
| 9 | 10008 | Mesa Vista Sol | 98-105 | Harbor City Waves | Harbor City Waves | `59e501570b77` |
| 10 | 10009 | Harbor City Waves | 90-92 | Mesa Vista Sol | Mesa Vista Sol | `8ca617caf66d` |
| 11 | 10010 | Mesa Vista Sol | 96-109 | Harbor City Waves | Harbor City Waves | `2a2c11b73bda` |
| 12 | 10011 | Harbor City Waves | 96-86 | Mesa Vista Sol | Harbor City Waves | `e15826b5d51c` |
| 13 | 10012 | Mesa Vista Sol | 103-88 | Harbor City Waves | Mesa Vista Sol | `0f689c467891` |
| 14 | 10013 | Harbor City Waves | 105-73 | Mesa Vista Sol | Harbor City Waves | `a0b74218e896` |
| 15 | 10014 | Mesa Vista Sol | 106-100 | Harbor City Waves | Mesa Vista Sol | `244e2f73559d` |
| 16 | 10015 | Harbor City Waves | 77-105 | Mesa Vista Sol | Mesa Vista Sol | `ae08b1ec919b` |
| 17 | 10016 | Mesa Vista Sol | 110-87 | Harbor City Waves | Mesa Vista Sol | `d80b50457b40` |
| 18 | 10017 | Harbor City Waves | 102-79 | Mesa Vista Sol | Harbor City Waves | `3e3c10d3d08e` |
| 19 | 10018 | Mesa Vista Sol | 96-103 | Harbor City Waves | Harbor City Waves | `47f88d139e7e` |
| 20 | 10019 | Harbor City Waves | 83-95 | Mesa Vista Sol | Mesa Vista Sol | `08b9560920d7` |

## Scope

This first Phase 0D slice proves balanced home/away scheduling, deterministic season history, standings with stable tie-breakers, and a verified replay-integrity hash for every game.

Injuries, between-game fatigue, public information, prediction scoring, and live LLM control remain separate measured steps. No credits, wagers, purchases, or paid model calls are part of this run.
