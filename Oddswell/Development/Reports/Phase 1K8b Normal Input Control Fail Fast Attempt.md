# Phase 1K.8b Normal Input Control Fail-Fast Attempt

## Outcome

**INCOMPLETE — THE FRESH PACKAGE REACHED THE NORMAL CHOOSER, BUT THE WINDOWS INPUT BRIDGE FAILED BEFORE ANY PLAYER INPUT.**

This attempt did not measure the Phase 1K.8b gameplay gate. The game reached the expected normal no-QA character chooser, but Windows Computer Use returned `node_repl exec context not found` during the required observation/action path. Safety rules prohibit substituting PowerShell UI automation or sending an unobserved input.

## Attempt

- Evidence root: `C:\tmp\OddsWellPhase1K8b-20260806T085120Z`
- Package: unchanged committed Phase 1K.8a Windows Development package.
- Passive peer: fresh isolated profile, Sundale listen server, gameplay UDP `127.0.0.1:17777`.
- Owner: fresh isolated profile, normal package start, no map URL, QA flag, chooser driver, preloaded save, or hidden shortcut.
- Peer reached `ODDSWELL_SHARED_CITY_JOIN|clients=1|boundary=local_listen_server`.
- Owner loaded `OddsWellCharacterSelectionGameMode`.
- Computer Use uniquely identified the owner and peer windows, but both the initial observation and one required recovery attempt failed with the same bridge error.

## Integrity

- Owner inputs: `[]`.
- Peer inputs: `[]`.
- No owner appearance SaveGame was created.
- No appearance-save marker, character-handoff marker, travel failure, route action, authority mutation, or hidden repair occurred.
- Owner log SHA-256: `1457FAD1454652F8F93361074314713DEBB85007F27D06DCEFA6D5AF03B8AC7A`.
- Peer log SHA-256: `03D6209471918F7B355CA70576C3B365205B3C3EBEB5B0BF37A3ACC5835CFC18`.
- Cleanup left zero OddsWell processes and zero UDP `17777` endpoints.

## Evidence boundary

Phase 1K.8a remains the latest completed phase. This attempt gives no new credit for shared membership, physical input, mutual visibility, cross-client appearance agreement, replicated movement, component 2, first-time-player usability, beta readiness, or production readiness. No C++, Python, Unreal content, package, configuration, save schema, brain, simulator, ledger, economy, wager, inventory, or network behavior changed.

## Next gate

Resume Phase 1K.8b only when a supported Windows input path can observe and drive the fresh no-QA owner. Use exactly `[Right, Enter]`, first reproduce peer `clients=2`, then—only if membership holds—measure mutual visibility, starter-appearance agreement, and one normal movement. Stop before component 3.

## Resolution

The control issue was later isolated to stale `@oai/sky` objects crossing Node REPL execution boundaries. Resetting the kernel and performing import, target selection, observation, and action within one fresh execution restored the supported Windows control path. The completed follow-up is [[Development/Reports/Phase 1K8b Normal Input Shared City Component Two Proof]].
