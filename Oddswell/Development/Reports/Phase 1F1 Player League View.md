# Phase 1F.1 — Player League View

Date: 2026-07-20
Status: Complete on `agent/phase-0d`
Cost: `$0.00`

## Outcome

The Unreal player client now shows the existing public basketball league without simulating a game. Press `L` to open or close the view and use `,` / `.` to move through seven readable pages:

1. standings;
2. Harbor City Waves roster and availability;
3. Mesa Vista Sol roster and availability; and
4. four schedule/history pages containing all 20 completed games, final scores, winners, and replay-seal prefixes.

The view contains two teams, twelve athletes, two standings rows, twenty verified results, and one athlete currently marked `OUT` in the frozen development season.

## Smallest truthful implementation

`client/tools/export_unreal_league.py` imports the existing cached `brain_admin.server.league_payload()` read model. It does not create another league or copy simulation rules into Unreal. The deterministic export is `29,160` bytes with SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5`.

The exporter rejects keys containing seed, RNG, hidden fatigue, readiness, recovery, injury-risk, or resolver data. Unreal independently requires the `oddswell-public-league-v1` schema, its public-only marker, the frozen two-team/twelve-athlete/twenty-game bounds, and one 64-character replay seal per completed game. The snapshot is staged as non-UFS content beside the existing replay fixture.

## Packaged evidence

The accepted Windows package logged:

`ODDSWELL_PUBLIC_LEAGUE|result=PASS|public_only=true|teams=2|athletes=12|standings=2|games=20|unavailable=1|pages=7`

An offscreen rendered capture showed Page 7 over the live Sundale graybox with Games 16-20, scores, winners, and replay-seal prefixes. The package exited cleanly after the capture.

The first archive attempt was correctly rejected because its command omitted explicit `-pak -iostore` flags and therefore did not contain the cooked maps. The accepted `Phase1F1-Verified-Windows` archive includes the cooked containers, league snapshot, and replay fixture: `53` files totaling `1,042,367,088` bytes.

## Validation

- Unreal editor and game targets compiled with UE `5.8`.
- Native `OddsWell.Character` automation passed `8/8`, including snapshot loading, seven-page construction, unavailable-athlete text, and Game 20 history.
- Corrected BuildCookRun with `-pak -iostore -compressed` passed in `50.25s`.
- Null-RHI packaged QA and an offscreen rendered packaged QA both passed and exited cleanly.
- All `65/65` frozen simulation regressions passed in `135.279s` with the unchanged time-sensitive test first.
- Brain Admin self-check, deterministic re-export, Python compilation, accepted-log audit, repository diff hygiene, and zero-process cleanup passed.

## Boundary and next gate

This is a build-time public snapshot, not live server synchronization. It adds no league mutation, client simulation, future schedule, odds, wager, settlement, Odds Bucks, paid service, account, deployment, retraining, or claim of AI learning. The existing authoritative Phase 0 league remains unchanged.

The next roadmap step is **Phase 1F.2 — graybox the stadium and its physical public viewing location**. Match fidelity, cameras, commentary, skip/condensed rules, duration, and the two-team 82-game variety question remain owner gates for later Phase 1F steps.
