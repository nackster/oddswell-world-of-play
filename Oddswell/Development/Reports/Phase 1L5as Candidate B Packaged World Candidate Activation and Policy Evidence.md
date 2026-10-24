# Phase 1L.5as Candidate B Packaged WORLD_CANDIDATE Activation and Policy Evidence

Status: `COMPLETE LOCALLY — PACKAGED_ACTIVATION_FAIL; SUNDALE_WORLD_CANDIDATE_TARGET_FALSE; BROAD PRODUCT NOT MEASURED; FRESH BATCH PHASE 5/6`

## Scope and authority

This phase performs one direct Candidate-only launch of the already proven Phase 1L.5ar Development package to measure the newly packaged world-selection seam. It does not rebuild or repackage, change source/config/maps, exercise route or gameplay, query Defender, measure broad product behavior or performance, retry, or authorize broader roadmap work.

Phase 1L.5ar is truth-repaired to full commit `ff5d85485e1662e6bb22a05a416816169875a8b2`, with independently verified exactly two canonical Project upserts, count `4/6`, and report identity `6,236` bytes/SHA `A573BE7281D30FB94F8CF58E73267140ECC6643389BE010CB0A4FE53ACB8CE11`/blob `e578f81e26ae4eeeb2c6ccf02f7e1d683ca69131`.

## Decision

| option | identifier | disposition | recommendation | exact reason |
|---|---|---|---|---|
| A | `ONE_PACKAGED_WORLD_CANDIDATE_DIAGNOSTIC_ATTEMPT` | `SELECTED` | `RECOMMENDED` | `smallest direct measurement of the newly packaged world-selection seam` |
| B | `REPEAT_STATIC_OR_PACKAGE_RECONCILIATION` | `NOT_SELECTED` | `REJECTED` | `source compilation and package custody were already proved and cannot measure runtime world selection` |
| C | `EXPAND_TO_ROUTE_GAMEPLAY_OR_SOURCE_CHANGE` | `NOT_SELECTED` | `REJECTED` | `expands authority and confounds the earliest activation diagnostic` |

## Sole packaged attempt

The exact `215`-byte raw argument string has SHA `3AC06073ECB94EC21ACA906AD800B42E62902EEF1BEBC841037D6A7ED4AD83D8`. Retained direct PID `24032` started at `2026-08-23T06:42:19.7521667Z`. At the `120 s` cap, its exact PID/path/start identity was revalidated, the retained PID alone was stopped once, and process drain was observed. Elapsed time is `121.270715 s`; exit `-1` has origin `POST_FORCED_STOP`, not natural product failure. Retry is `0`.

The immutable log is `98,541` bytes/SHA `16CDC22758C5E80BC2C75CD261AA099BCA14D8D488BB8809B05672697BBE5275`, mtime `2026-08-23T06:42:23.3154551Z`. It was stable across observations separated by `6.0223011 s`, is strict UTF-8 with BOM and no NUL, contains `1,016` CRLF records, `2` bare LF records, no bare CR, and ends CRLF.

## Reliable WORLD_CANDIDATE result

FLAG_ACCEPTED occurs once at line `843`. Two escape-valid WORLD_CANDIDATE markers occur: line `892` reports `package=Untitled|target=false|claimed=false`; line `910` reports `package=SundaleGraybox|target=false|claimed=false`. Parse-error, duplicate-target, and claimed-true counts are `0`; target-false is `2`; target-true is `0`. The exact target package `/Game/Maps/SundaleGraybox` is therefore not selected even though map completion occurs once at line `940`.

This reliable loaded-Sundale `target=false` contradiction establishes `PACKAGED_ACTIVATION_FAIL / SUNDALE_WORLD_CANDIDATE_TARGET_FALSE` and controls the later timeout boundary. WORLD_BOUND, BEGIN_PLAY, NEXT_TICK_DISPATCHED, START, FIELD, RESULT, and project REQUEST_EXIT markers are all `0`. Fatal and security marker counts are `0/0`. Policy evaluation was never reached, so it is `INDETERMINATE`, not a policy failure or policy result.

## Exact-four evidence

| artifact | bytes | SHA-256 | custody |
|---|---:|---|---|
| `CandidateBActivation.log` | 98,541 | `16CDC22758C5E80BC2C75CD261AA099BCA14D8D488BB8809B05672697BBE5275` | process-created and immutable |
| `session_custody.tsv` | 5,991 | `73BBB73B1486626D369BD62A4B1AAB436B0AA9E4D88A9B43854A0883714E164F` | repaired exact 155 unique rows |
| `marker_ledger.tsv` | 1,687 | `EA219030F6A54F91C020876207B7866383D1A1C4C582193845F5B1A67511405C` | exact eight ordered marker rows |
| `field_ledger.tsv` | 74 | `E4F30C58376BDD40D1D88A83F10FED382957466FCD5794697DF608C1E413A089` | header-only because FIELD count is zero |

The session duplicate-key defect was detected before evidence writing; Scope removed only the duplicate appended `natural_exit_after_result` row, leaving inherited row 114. The final session has `155/155` unique, nonblank ordered keys. All TSVs are UTF-8 without BOM or NUL, use LF with final LF and no CR. Exact-four postwrite replay mismatch is `0`.

## Package, source, and process custody

The prior package remains `50` files / `1,052,121,260` bytes. Its live ordinal manifest is `6,266` bytes/SHA `00B348B2168F8C66B1B98CF25BB71A8DF7B7E0AF78AD04FEA4CC6B4AD422E4B7`, byte-identical to preserved custody. Candidate source, module, config, maps, repository HEAD `ff5d85485e1662e6bb22a05a416816169875a8b2`, and clean state remained exact. The excluded command process remained identity-exact and untouched. Watched/unreadable process residue, retained-PID TCP/UDP residue, and all TCP/UDP `17777/1985/7810` cells are `0`.

## Credits and nonclaims

Activation is `FAIL`; policy application is `INDETERMINATE`; route is `NOT_RUN`; broad product is `NOT_MEASURED`. Current activation, packaged Candidate-source execution, package-launch, policy application/full validation, visible-client, route, gameplay, broad-product, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, and readiness credits are all `0`. Candidate B remains provisional/unvalidated. Zero security markers are a log observation, not a Defender-clean claim. No broad product defect, policy result, route/gameplay result, performance, compatibility, accessibility, readiness, or beta-exit claim is made.

FRESH BATCH PHASE 5/6 CLOSED — NO AUTOMATIC PHASE 6
