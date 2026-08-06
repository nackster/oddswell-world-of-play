---
tags:
  - development
  - phase-1c
  - sundale
  - unreal
  - graybox
status: complete
date: 2026-07-20
---

# Phase 1C.2 — Primitive Sundale Graybox and Packaged Route Measurement

## Outcome

Phase 1C.2 converts the approved Sundale plan into one separate, primitive Unreal Engine 5.8 map. A fresh packaged build spawns the existing placeholder avatar at the Studio, completes the full clockwise `800 m` acceptance route at both approved speeds, returns home, and proves continuous blocking-floor collision.

This is a measured graybox, not final city art. See [[Design/Sundale Art Direction and Core Loop]], [[Visual Maps/Sundale Core Loop]], and [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]].

## Smallest implementation

- `Content/Maps/SundaleGraybox.umap` contains `45` labeled `Sundale_` actors made only from Unreal built-in primitives and native light/environment actors.
- The `340 m × 280 m` bounded ground includes the `140 m × 90 m` commons, an `800 m` outer route, two commons shortcuts, primitive Studio/job/clothing/arena/sportsbook/furniture masses, a public court, four placeholder trees, and six separately named collision-safe thresholds.
- The map owns `OddsWellLocomotionGameMode`, so a normal direct map launch spawns the existing character without a URL override or global default-map change.
- The existing character gained only an opt-in packaged route QA path: `-SundaleRouteQa`, optional `-SundaleRouteRun`, and the existing `-LocomotionAutoExit`. It uses normal `AddMovementInput`; it does not teleport, accelerate time, add a navigation framework, or alter player controls.
- Native automation locks the eleven ordered waypoints, matching labels, and exact `80,000 cm` centerline.

## Corrective evidence

The first archive was rejected because Sundale had not been explicitly included in the cooked package. The corrected BuildCookRun names `/Game/Maps/SundaleGraybox` directly.

The first run-speed traversal was also rejected. The furniture mass touched the west route centerline and could catch a capsule at running speed. Moving that primitive wall ten meters clear produced a new map, verification, package, and complete walk/run evidence. Rejected runs are not counted below.

## Final Unreal and map evidence

- Final deterministic graybox construction: `0.776s`, `45` actors.
- Fresh reopen verification: `45` actors, `6` thresholds, exact route distance `80,000 cm`, `OddsWellLocomotionGameMode`, collision profiles passed.
- Map Check: `0` errors, `0` warnings.
- Final map: `83,147` bytes; SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.
- Existing UE 5.8 editor and game builds passed after the route code change; native `OddsWell.Character` automation passed `5/5`.
- Final Windows Development BuildCookRun succeeded in `58.57s`. Before runtime output, the archive held `50` files totaling `1,041,481,602` bytes.
- A local ignored `1920 × 1080` overview shows the complete primitive footprint; SHA-256 `D0768461DA0D9B4F43B95201F3FE8D719B485AABA1A87794BEBDDBDACD30265D`.

## Accepted packaged route evidence

| Mode | Projection | Measured | Traveled | Checkpoints | Return/floor |
| --- | ---: | ---: | ---: | ---: | --- |
| Walk at `260 cm/s` | `307.7s` (`5:08`) | `307.074s` (`5:07`) | `79,987.6 cm` | `11/11` | home, grounded, blocking floor, `1.8 cm` vertical range |
| Run at `520 cm/s` | `153.8s` (`2:34`) | `155.201s` (`2:35`) | `79,936.5 cm` | `11/11` | home, grounded, blocking floor, `1.7 cm` vertical range |

Both accepted processes loaded `SundaleGraybox` directly and reported `OddsWellLocomotionGameMode`; neither launch supplied a game-mode override.

## Representative rendered profile

A separate rendered `1280 × 720` Windows Development capture recorded `600` frames. Excluding the first `60` warm-up frames, `540` samples averaged `8.062 ms` frame time with `9.422 ms` p95; GPU time averaged `7.082 ms` with `7.513 ms` p95. One bounded process sample reported `1,472.4 MiB` working set and `3,560.9 MiB` private bytes. These are local primitive-graybox measurements, not a final-art performance promise.

## Regression and integrity

- Frozen Python regressions: `65/65` passed in `163.078s`.
- Brain Admin self-check: passed in `3.239s`.
- Python compilation: passed in `0.086s`.
- Frozen Bootstrap map SHA-256 remains `44FC5E531591672E10E3740A780EAFB34326C2EADC7D85A37CFA352541932C16`.
- Frozen BlockCourtBenchmark SHA-256 remains `F970A2F4609F2D6EC24475AE48C98E12DB53BDE2CD95A238F2015C3FF0840018`.
- Generated build, cook, package, log, screenshot, and CSV output remains ignored. Cost was `$0.00`.

## Scope boundary

No final asset, production material, interior, store catalog, item ownership, apartment system, NPC, multiplayer, backend, account, Odds Bucks, wagering rule, deployment, paid service, model, training, or retraining behavior was added. The arena, sportsbook, job, stores, court, commons, and Studio are only readable primitive location masses or thresholds.

## Phase result and next gate

The Phase 1C exit contract is satisfied: the placeholder avatar can traverse the entire required city loop with no dead end, required jump, fall, or broken floor collision. Phase 1D is next, but its first shared-city proof remains an owner gate for local-client count/capacity direction, player collision, visible names, and external hosting boundaries.
