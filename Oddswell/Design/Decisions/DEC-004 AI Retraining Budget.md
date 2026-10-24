---
tags:
  - decision
  - ai
  - budget
status: accepted
date: 2026-07-14
---

# DEC-004: AI Retraining Budget

## Context

The Basketball AI Brain will eventually use evaluated league data to produce a candidate policy or model update. Provider and model selection are still unresolved, so the first paid experiment needs a fixed financial boundary before credentials or training jobs are connected.

## Decision

The first retraining experiment has a **hard total ceiling of $5 USD**.

- The ceiling covers provider charges needed to prepare, train, and evaluate that first candidate.
- Do not start a paid job unless its maximum estimated charge fits within the remaining budget and the integration can stop further work before exceeding the cap.
- Record provider, model, job identifier, estimates, actual charges, dataset version, and candidate policy version.
- Use only sanitized sports decisions and outcomes. Credits, wagers, purchases, payment data, hidden seeds, and private chain-of-thought are excluded.
- A candidate never promotes itself. It must pass the existing legality, replay, calibration, fairness, cost, and latency gates.
- Live inference has a separate unresolved budget; this decision does not authorize unlimited model calls.

## Consequences

Provider and model selection must fit the cap or the experiment does not run. Increasing the ceiling requires a new explicit decision. Until a provider is selected and the cap is enforceable in code, Phase 0D continues with the no-cost deterministic brain and recorded evidence.
