# Phase 1K.9 Corrective Retained Movement and Networked Studio Fail-Fast Measurement

## Outcome

**COMPLETE - FRESH COMPONENTS 1-2 PASSED WITH RETAINED PEER MOVEMENT PROOF; COMPONENT 3 FAILED AT ITS FIRST STUDIO BOUNDARY.**

Attempt `phase1k9-corrective-fresh-20260806T220449Z` used fresh isolated owner and passive-peer profiles with the unchanged accepted Phase 1K.8a Windows Development package. The normal owner selected `masculine_tone_2`, joined the loopback Sundale peer, reached `clients=2`, preserved the exact starter appearance, and produced a visible replicated position change in retained fixed-view passive-peer screenshots. The peer received zero gameplay input.

Only after that evidence closed component 2 did the same attempt measure component 3. At the spawn-side Studio doorway, the required `Press E to enter your empty Studio` prompt was absent. One normal `E` left the owner in networked `SundaleGraybox`, emitted no Studio-transition marker, created no housing SaveGame, and created no owner ledger file. The attempt stopped there before job input or any later component.

The interrupted attempt rooted at `C:\tmp\OddsWellPhase1K9Corrective-20260806T215804Z` is not acceptance evidence. Computer Use was stopped before it returned input timestamps or a post-state; its setup record marks it interrupted and no unreturned input is claimed.

## Fixed identity and boundary

- Evidence root: `C:\tmp\OddsWellPhase1K9CorrectiveFresh-20260806T220449Z`
- Measurement repository baseline: `dc122414cb60a18beac1dc2a84dce3fea5ff8d2b`
- Package source commit: `7e0c507d78da9c59f982a97e10e810fa94f53083`
- Game executable SHA-256: `F4BA693DF3CD125689528B7298517096E1E8E053FF439136FDBD9A485EC03E54`
- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- Package inventory: `50` files, `1,049,384,876` bytes, `0` Python files.
- Passive peer: wrapper/game PIDs `28816`/`16328`, window `2230410`, exact gameplay endpoint `127.0.0.1:17777`.
- Owner: wrapper/game PIDs `17436`/`30940`, window `2492530`, normal package start with no map URL or QA flag.
- QA flags: `[]`; teleport: `false`; direct-location action: `false`; after-setup developer interventions: `0`.
- Passive-peer gameplay action count: `0`.

Exact commands, profiles, PIDs, package identities, and setup timestamps are retained in `Evidence/setup.json`.

## Fresh component evidence

1. Supported Computer Use observed the production eight-card chooser.
2. Normal `Right` at `2026-08-06T22:06:29.275Z` selected non-default `masculine_tone_2`; one `Return` at `22:06:29.339Z` confirmed it.
3. The production appearance SaveGame was written at `22:06:29.3926680Z`, `2,183` bytes, SHA-256 `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`.
4. The peer logged `ODDSWELL_SHARED_CITY_JOIN|clients=2|boundary=local_listen_server` and accepted Player 2 with `masculine_tone_2`, `starter_offwhite_top`, and `starter_offwhite_bottom` from `client_rpc`.
5. The retained peer-before image shows fixed Player 1 plus labeled tan Player 2. After ordinary owner-only viewport focus and normal locomotion input, the retained peer-after image shows Player 2 displaced while Player 1 and the surrounding wall/background remain fixed.
6. All raw owner movement inputs and timestamps are retained in `Evidence/owner-movement-inputs.json`; the passive peer received no gameplay input.

Retained peer evidence:

- `Evidence/PeerCaptures/before-owner-movement.png`: `934A50B257274DAB69B93979B3C3802DAB46BF2850291EB802611299076A490C`, captured `2026-08-06T22:06:55.8434185Z`.
- `Evidence/PeerCaptures/after-owner-movement.png`: `3A1C4925CAF328F49838105435AA1F544B5531103938B4CEBDD864E5014F44D5`, captured `2026-08-06T22:13:58.8337251Z`.
- `Evidence/owner-movement-inputs.json`: `6AD8F907528B14D5BB8070D374B04D10B3693DD101F07EB71246607494350F5A`.
- `Evidence/peer-capture-audit.json`: `F3F1809CBC07F108A909B17F23EC62AC81A893AD48FDB78162ABFEB8FC540310`.

The image audit is a reproducible diagnostic, not an authoritative world-coordinate record. Within the disclosed fixed crop and tan-avatar mask, the centroid changes by `(-8.39, +4.93)` pixels (`9.73` pixels total), consistent with the visible game-native displacement.

## First fail-fast boundary

After returning toward the spawn-side Studio doorway with inverse normal movement, the owner capture showed no `Press E to enter your empty Studio` prompt. One normal `E` occurred at `2026-08-06T22:15:53.901Z`.

- Before `E`: networked `SundaleGraybox`, prompt absent, `0` Studio transition markers, `0` housing saves, `0` owner ledger files.
- After `E`: still networked `SundaleGraybox`, prompt absent, `0` Studio transition markers, `0` housing saves, `0` owner ledger files.
- `Evidence/OwnerCaptures/studio-before-e.png`: `539E7C4F4C5B1523A145A9561537619F62D80454149685AD74EEBA63AD4E1EA8`.
- `Evidence/OwnerCaptures/studio-after-e.png`: `94D4DCEFBF77C17A27625CAD88F2B619A03F809EE2467E90261A82E504C53B2C`.
- `Evidence/studio-input.json`: `569EF4A13131D7988A08D5729CE47AA856D323FFE32A137A38E4845DE735B220`.

Production `PollStudioInteraction()` returns whenever `GetNetMode() != NM_Standalone`. The shared-city owner is an `NM_Client`, which is consistent with the missing prompt and no-op interaction. This phase measures that boundary; it does not change production code.

The first component-3 failure prevented Studio entry, interior movement, exit, exact-doorway return evidence, later location discovery, and all components 4-8. No job `E`, payout, ledger mutation, wager, purchase, or equip action occurred.

## Verification

- Package identity and inventory: PASS.
- Fresh component 1: PASS.
- Fresh component 2 membership, appearance, mutual visibility, retained peer-visible movement, and passive-peer boundary: PASS.
- Component 3: FAIL at the first Studio prompt/entry boundary; later component-3 requirements and components 4-8 are **NOT REACHED**.
- Owner and peer logs: `0` fatal, assertion, ensure, travel-failure, or network-failure matches.
- Owner log SHA-256: `E15AAF2743CF4EBF0502B42D05EBBED145FBB067B8298872DECA903C0CAD1327`.
- Peer log SHA-256: `B07110D7129268BA5EE3F62DEB29F0FD680EDC8FF32B3BB8A14D3C9207E1AB30`.
- `Evidence/session.json`: `6487ED0C7D3F3353074E7060155A30A630418F27801E29586F12BA0192D55490`.
- Repository-pinned Python `3.12.13` frozen suites: PASS `9 + 2 + 8 + 46 + 40 = 105/105` in `133.637s` of reported test time.
- Brain Admin `python -B -m brain_admin.server --check`: PASS at `2026-08-06T22:27:55.9543444Z`.
- Cleanup: normal owner/peer Alt+F4 exits; `0` relevant OddsWell processes and `0` UDP `17777` endpoints.

Production source and package are unchanged. The completed Phase 1K.8a native `1/1`, full native `49/49`, editor/game builds, and BuildCookRun remain the applicable build evidence; Ponytail skips a no-op rebuild. One preliminary Phase 0D test command ended at the shell runner's time limit before returning a result. The accepted unchanged rerun passed all `46/46`; no code, fixture, threshold, or environment setting changed.

## Scope boundary

No C++, Python, Unreal content, package, fixture, schema, brain, simulator, ledger, economy, wager, inventory, housing, backend, telemetry, deployment, paid service, or model behavior changed. Cost was `$0.00`.

## Next gate

Phase 1K.9a should correct only the measured network-client Studio prompt/private-transition boundary while preserving the existing local housing SaveGame and exact-return authority. Rebuild, repeat fresh components 1-2, and re-measure component 3 only. Stop before any job `E` or ledger mutation.
