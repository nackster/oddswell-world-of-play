# Phase 1H.26S — Automatic Exact Canonical Tipoff Lock

**COMPLETE for the exact pending Harbor City Waves / `40` Odds Bucks request only.**

## Delivered

GameMode now schedules at most one non-looping timer after either:

1. exact H26R placement has persisted and reloaded; or
2. the same authoritative pending request cold-restores before H26A tipoff.

The timer carries no client time, command, offer, team, or stake. At exact H26A tipoff its callback invokes the existing parameterless H26G transition. H26G still independently reloads and validates H26A/H26B/H26C, derives its stable command, and persists its separate immutable lock. The open ticket booth refreshes only after that lock reloads durably, then shows the existing `MATCH WINNER UNAVAILABLE / LOCKED` panel.

## Timing and failure boundary

- Production schedules from the precise UTC duration remaining to H26A tipoff.
- A second schedule request while the timer exists is inert.
- Early and late callbacks cannot invoke H26G.
- At or after tipoff no timer is scheduled, no offline catch-up runs, and no timestamp is backdated.
- A process restarted before tipoff may schedule one new process-local timer for the same immutable request.
- Missing, malformed, or tampered H26A/H26B/H26C/request evidence schedules nothing or fails closed through H26G.
- Downstream H26H-H26P evidence is neither required nor created. Persistence failure does not refresh the booth.

Package QA shortened only the wait to four seconds and reused H26G's pre-existing exact-H26A QA clock observation. This proves the timer-to-H26G integration without claiming a production 30-minute wall-clock run.

## Validation

- Unreal Editor build: PASS in `14.93s`.
- Unreal Win64 Development game build: PASS in `20.13s`.
- Focused `OddsWell.Locomotion.CanonicalAutomaticTipoffLock`: PASS `1/1`.
- Retained `OddsWell.League.CanonicalMatchWinnerLock`: PASS `1/1`.
- Full native OddsWell suite: PASS `34/34`.
- Frozen simulator/brain/league/odds suite: PASS `77` tests and `106` subtests.
- Brain Admin Python compilation and self-check: PASS.
- League export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Explicit `Bootstrap+SundaleGraybox` BuildCookRun: PASS in `49.52s`.
- Package: `50` files, `1,047,983,742` bytes, zero Python files.

Fresh packaged QA proved job `100` → booth → Harbor `40` → pending receipt → one scheduled callback → one H26G lock → locked panel. The ledger remained sequence `1/+100`, sequence `2/-40`, count `2`, balance `60`; the request stayed `accepted_pending_lock`; result links and every H26H-H26P transition stayed absent. The route log contains exactly one `SCHEDULED`, one durable lock `PASS`, and one H26S QA `PASS`.

A separate package first stopped with the exact pending request, then restarted before tipoff. The cold process logged `restart_rescheduled=true`, exactly one timer, exactly one lock, and stable repeated ticks/reloads.

Across that restart and lock transition, all three upstream files retained exact length, SHA-256, and UTC mtime:

| Record | Bytes | SHA-256 |
|---|---:|---|
| H26A schedule | `2,771` | `ef95a8621194eecdf6ed4e7b6162a41f95ab048343edffebcc178e7bba10f059` |
| H26B commitment | `5,153` | `528c14c390f2eb73e04fde312489aa0efcb1269eb8b241f5eb11c178f89fe312` |
| H26C offer | `2,960` | `41bc615f7839c497e94a2d2276c612e9e85c9d39add9292115798e40a006ae24` |

The retained `1280x800` screenshot was visually inspected. The locked panel is legible and unclipped and exposes no teams, prices, selections, or wager controls.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26S-20260727`. Cost was `$0.00`.

## Not delivered

H26S does not automatically create H26H-H26P, simulate a game, publish a result, decide or settle a wager, pay or refund Odds Bucks, publish history, repair evidence, catch up offline, generalize placement, add Mesa/other stakes, add a market, alter the simulator or brains, add a backend, or deploy anything.
