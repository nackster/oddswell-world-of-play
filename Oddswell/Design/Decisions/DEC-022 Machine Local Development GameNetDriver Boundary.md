---
tags:
  - decision
  - beta
  - networking
  - security
status: accepted
date: 2026-08-04
---

# DEC-022 Machine-Local Development GameNetDriver Boundary

## Decision

The owner selected Option A with the exact response, `Ok let's do A. Continue`.

For the current machine-local Windows Development first-hour measurement only, Phase 1K's gameplay-network setup boundary applies to the Unreal `GameNetDriver`. The Phase 1K.2 evidence that the exact OddsWell game PID owned one gameplay UDP endpoint at `127.0.0.1:17777` satisfies that bounded gameplay-network prerequisite for a fresh Phase 1K.3 setup attempt.

This decision is prospective. It does not retroactively pass Phase 1K.1 or Phase 1K.2 setup, does not complete `setup_end_utc`, and gives no credit to route components 1-8.

## Recorded Development security debt

The same packaged OddsWell Development PID also owned Unreal's non-game trace-control TCP listener at `0.0.0.0:1985`. This is accepted only as explicit machine-local Development diagnostic debt. It must be removed or contained and freshly verified before any external beta, release, deployment, shared or untrusted network, or production use.

## Prohibited claims

- No whole-process loopback or whole-process network-isolation claim.
- No external-network, shared-network, untrusted-network, beta-distribution, release, deployment, or production-safety claim.
- No firewall, transport-security, backend-authority, internet-multiplayer, or remote-service claim.
- No claim that trace control is harmless merely because the gameplay endpoint is loopback-only.

The frozen simulation, event log, settlement, Odds Bucks, inventory, and history boundaries remain unchanged.

## Next gate

Phase 1K.3 may run one fresh owner/setup measurement using the proven `GameNetDriver` flags and stop at the first measured contract failure. This decision does not launch that attempt and does not authorize route, chooser, runtime, configuration, firewall, packaging, deployment, or engine-source changes.

See [[Development/Reports/Phase 1K2 Loopback Only Passive Peer Launch Correction and Proof]] and [[Development/Reports/Phase 1K2a Owner Accepted Machine Local Development GameNetDriver Boundary]].
