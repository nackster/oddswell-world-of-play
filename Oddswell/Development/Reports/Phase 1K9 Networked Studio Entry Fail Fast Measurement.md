# Phase 1K.9 Networked Studio Entry Fail-Fast Measurement

## Outcome

**COMPLETE - FRESH MEASUREMENT FAILED AT THE FIRST COMPONENT-3 STUDIO BOUNDARY.**

A fresh no-QA owner and isolated passive peer repeated the accepted components 1-2 path in the unchanged Phase 1K.8a Windows Development package. The owner selected and confirmed non-default `masculine_tone_2`, joined the loopback Sundale listen server, reached `clients=2`, preserved the exact starter appearance, achieved mutual labeled visibility, and moved through normal controls while the peer remained passive.

At the Studio spawn doorway, the networked owner never received the required `Press E to enter your empty Studio` prompt. One normal `E` press left the owner in shared `SundaleGraybox`, emitted no Studio-transition marker, and created no housing SaveGame. The attempt stopped there. No other component-3 location, Studio interior, job interaction, ledger mutation, or component 4-8 action followed.

This is a Development technical failure measurement. It is not a completed component 3, observed first-time-player result, external-network proof, beta-readiness claim, or production-readiness claim.

## Fresh packaged attempt

- Evidence ID: `phase1k9-20260806T212425Z`
- Evidence root: `C:\tmp\OddsWellPhase1K9-20260806T212425Z`
- Measurement repository commit: `f392b7c6d72a3f66222d9bd664a9b5a6f9b752cd`
- Unchanged package source commit: `7e0c507d78da9c59f982a97e10e810fa94f53083`
- Game executable: `C:\tmp\OddsWellPhase1K8Package-20260806T035603Z\Windows\OddsWell\Binaries\Win64\OddsWell.exe`
- Game SHA-256: `F4BA693DF3CD125689528B7298517096E1E8E053FF439136FDBD9A485EC03E54`
- UFS manifest SHA-256: `278E358F87DA82437AA02FEDF7273CFE6861A59C720D20F914503EAF129D4D73`
- Package inventory: `50` files, `1,049,384,876` bytes, zero Python files.
- Setup ended: `2026-08-06T21:26:44.1428233Z`.
- Passive-peer gameplay endpoint: exact `127.0.0.1:17777`, owned by peer game PID `12320`.
- Owner game PID/window: `30744` / `330738`.
- Peer game PID/window: `12320` / `3342360`.
- QA flags, teleport, direct-location action, hidden action driver, and post-setup developer interventions: `0` / none.
- Passive-peer gameplay action count: `0`.

The exact wrapper commands, package identities, setup actions, profiles, processes, endpoint, and setup boundary are retained in `Evidence/setup.json`. Ordered elapsed checkpoints, raw player inputs, prompt result, hashes, authority boundary, and cleanup are retained in `Evidence/session.json`.

## Repeated components 1-2

1. The owner started without an appearance SaveGame and visibly showed the production eight-card chooser.
2. Normal `Right` selected `masculine_tone_2`; one physical `Return` confirmed exactly once.
3. The production appearance record saved `masculine_tone_2`, `starter_offwhite_top`, and `starter_offwhite_bottom` as `2,183` bytes with SHA-256 `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`.
4. The owner client-traveled to the waiting peer; the peer logged `clients=2` and accepted the exact owner-submitted appearance.
5. Supported Windows Computer Use observations showed both labeled players and the tan owner avatar in the off-white starter clothing. The owner used only normal movement controls; the peer remained an observer.
6. No fallback, travel failure, QA action, teleport, save edit, authority repair, or evidence splice occurred.

## First fail-fast boundary

The first component-3 checkpoint was the Studio door at the normal shared-city spawn. Before `E`, retained `ScreenShot00004.png` shows the shared Sundale world with no required Studio prompt. Its SHA-256 is `B17A2C821A07CC48D69F693E9496889EAADCA61AC04D0B40C534610421FBD820`.

One normal `E` press produced no visible or authoritative change:

- the owner remained in networked `SundaleGraybox`;
- `ScreenShot00005.png` remained in the same world and has SHA-256 `3F308CD858BA066963BBC4E9206CE74C2614F45003D19E6FA1C8BB2699EBDF75`;
- owner log count for `ODDSWELL_STUDIO_TRANSITION` was `0`;
- `OddsWellStudioHome.sav` remained absent;
- no Studio structure, furniture, decoration, snap-point, or return-error evidence could be reached;
- no job `E` occurred and no owner Odds Bucks ledger existed.

The measured source boundary explains the runtime result: production `PollStudioInteraction()` returns when `GetNetMode() != NM_Standalone`. The component-2 owner is an `NM_Client` in the shared Sundale session, so the existing private Studio prompt and transition are unreachable on the required contiguous route.

This phase intentionally adds no speculative correction before the measurement.

## Verification

- Fresh package identity and package inventory: PASS.
- Fresh components 1-2 setup, normal input, membership, appearance, and passive-peer boundaries: PASS.
- Focused runtime/source agreement for the missing network-client Studio interaction: PASS.
- Component 3: FAIL at its first Studio prompt/entry boundary; all later component-3 requirements are **NOT REACHED**.
- Frozen Python suites under repository-pinned Python `3.12.13`: PASS `9 + 2 + 8 + 46 + 40 = 105/105` in `136.3s`.
- Brain Admin `python -m brain_admin.server --check`: PASS.
- Fatal, assertion, ensure, and travel-failure matches: `0`.
- Final OddsWell process count and UDP `17777` endpoint count: `0` / `0`.
- Owner log: `96,535` bytes, SHA-256 `A67CFEAE377AAAC62A671B897A44FDE8B9B87A09973C274BBBB6BB4F7CE477A5`.
- Peer log: `101,898` bytes, SHA-256 `FA3A36761004C84C88EEE8162282299D6B9A425677E0B71E1019C87D72329C99`.
- `Evidence/setup.json`: SHA-256 `9CF304A00BC923F4690DFE9E44C1264B4E94178402E99722ADC5B42F33DFF348`.
- `Evidence/session.json`: SHA-256 `067C6997DF1DD2E8F4F9540D35F5EE4B34108DFA467603FDCD4AB5421AAEB760`.

No C++, Python, Unreal content, package, fixture, schema, brain, simulator, economy, ledger, wager, inventory, backend, telemetry, or deployment behavior changed. Ponytail therefore reuses the unchanged Phase 1K.8a editor/game builds, focused native `1/1`, full native `49/49`, and BuildCookRun evidence instead of performing a no-op rebuild.

## Next gate

Phase 1K.9a should correct only the measured network-client Studio boundary by making the existing empty-Studio prompt and private transition reachable from the normal shared-city owner while preserving the current local housing SaveGame and exact-return authority. It must then rebuild and repeat fresh components 1-2 before re-measuring component 3 only. Stop before any job `E` or ledger mutation.
