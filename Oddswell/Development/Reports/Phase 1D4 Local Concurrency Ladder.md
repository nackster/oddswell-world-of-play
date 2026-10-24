# Phase 1D.4 — Local Concurrency Ladder

Date: 2026-07-20
Status: Complete on `agent/phase-0d`
Cost: `$0.00`

## Outcome

One fresh Windows Development package passed a bounded local ladder of **2, 3, and 4 total clients**, including the listen host. At every rung, all clients saw the complete set of temporary player labels and owner-submitted approved appearances, while the server measured every joining client moving at least `300 cm` through normal character movement.

This is local prototype evidence only. It does **not** select a beta instance ceiling or prove external-host, production-network, final-art, long-session, or hardware capacity.

## Smallest implementation

The existing Phase 1D shared-city QA path gained three opt-in arguments:

- `-SharedCityCapacityQa`
- `-SharedCityQaClients=N`, clamped to the measured `2–4` ladder
- `-SharedCityCapacityAutoExit`

Each client emits one capacity visibility record only after it can see the target number of named players and all target appearances are valid and owner-submitted. The listen server passes only after every remote player has moved at least `300 cm` from the position captured when the full rung assembled. No load-testing dependency, online service, account system, matchmaking system, or speculative capacity framework was added.

## Packaged ladder evidence

All game traffic used a local listen server with `-multihome=127.0.0.1` on ports `7793–7795`. NullRHI and audio-off arguments kept this a bounded systems measurement rather than a rendered performance test.

| Total clients | Remote movers | Minimum server distance | Elapsed | Peak packaged processes | Peak combined working set | Exit codes |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 1/1 | `302.7 cm` | `12.34s` | 4 | `685.6 MB` | `0, 0` |
| 3 | 2/2 | `301.3 cm` | `13.16s` | 6 | `1,030.1 MB` | `0, 0, 0` |
| 4 | 3/3 | `300.5 cm` | `14.20s` | 8 | `1,373.9 MB` | `0, 0, 0, 0` |

The process count and working-set values combine each packaged launcher with its spawned game process. They are useful only as like-for-like local ladder samples; they are not per-client requirements or a production server forecast.

The accepted nine process logs contain exactly `9` capacity-visibility markers and `3` server capacity-pass markers. They contain zero fatal, ensure, appearance-rejection, shared-city-fail, connection-timeout, or network-failure matches. No OddsWell process remained after the accepted ladder.

## Corrective evidence

The first 2-client launch was rejected because literal single quotes in the PowerShell argument string caused the packaged server to ignore the requested cooked map and fall back to the uncooked Bootstrap map. The client timed out without entering Sundale. Those processes were closed, the argument quoting was corrected, and all accepted evidence above was regenerated. No security setting or Unreal gameplay behavior was changed for that launcher correction.

## Validation

- Unreal editor and game targets compiled successfully with UE `5.8`, Visual Studio toolchain `14.44.35214`, and Windows SDK `10.0.22000.0`.
- Native `OddsWell.Character` automation passed `5/5`.
- Windows BuildCookRun succeeded in `64.16s`; the archive contains `65` files totaling `1,041,951,158` bytes.
- The complete frozen simulation regression suite passed `65/65` in `138.007s`.
- OddsWell Admin Console self-check passed.
- Python compilation, diff hygiene, accepted-log audit, and zero-process cleanup passed.

## Boundary and next gate

Phase 1D exit evidence is satisfied at the local prototype boundary: multiple measured clients can move together and see the same approved clothing state, and a cold reconnect restores the same visible state. A capacity ceiling, regions, accounts, external hosting, blocking/reporting, moderation, chat, friends, parties, apartment visits, item transfer, stores, Odds Bucks, wagering, final art, deployment, model training, and retraining remain unimplemented or unresolved.

The next roadmap dependency is **Phase 1E — Studio and apartment progression**. Before implementation, the owner must resolve the beta apartment instancing/visit rule and the minimal layout/decorating strategy.
