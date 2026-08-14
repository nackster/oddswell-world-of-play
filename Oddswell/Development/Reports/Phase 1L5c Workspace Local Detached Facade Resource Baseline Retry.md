# Phase 1L.5c Workspace-Local Detached Facade Resource Baseline Retry

- Date: 2026-08-13
- Branch: `agent/phase-0d`
- Baseline commit: `79b19575a41bfa54b72822b683baacd4b8053ceb`
- Status: **COMPLETE LOCALLY — EVIDENCE_LIMITED; PRODUCT NOT_MEASURED; FIXED-MACHINE BASELINE CREDIT 0**
- Batch position: Phase `5/6`, pending local commit and verified two Notion upserts
- Attempt count: `1`; no retry
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

The single authorized detached attempt is `EVIDENCE_LIMITED`. Product is `NOT_MEASURED`; fixed-machine baseline, route/resource, minimum-PC, roadmap item-5, and product credit are all `0`. No product defect, resource conclusion, optimization need, or readiness finding is established.

The no-game canary passed its bounded gate: detached controller PID `13096`, sentinel present, exact exit `0`, parameterless drain, and completion in `589 ms`. This proves only that the `10 s` upper bound was met; it creates no minimum-duration claim.

## Attempt and custody

The frozen controller launched once as PID `36288` and started packaged wrapper PID `42448` with the exact `14` intended route tokens. Its Win32 child query returned `Access denied` before it could retain a child handle, parent/command custody, or sampler. The controller therefore produced `0` one-second samples, stopped its owned wrapper in `finally`, and froze the original result as `EVIDENCE_LIMITED` / product `NOT_MEASURED`.

The scope-verified orphan child PID `25920` exited naturally after the controller result and before cleanup authorization could be used. Its operating-system exit code is unknown because no live handle was retained. Later route-log output is not inferred as route, resource, product, baseline, or exit evidence.

## Frozen evidence

Evidence root: `client/OddsWell/Saved/Phase1L5c-20260814T013809Z`

- Original `result.json`: `2,101` bytes; SHA-256 `5795CB8C6C02DE7A673196012B20A2CFA37B256BF4BFB67D9B2C809B1A9F09DF`; unchanged.
- Post-cleanup custody addendum: `1,099` bytes; SHA-256 `1FE4E1883F715E9218E1BE54BE4124AED146978CD4A62C0C85D15616B2CDEE8A`; records natural exit, no forced cleanup, and final target-process/TCP/UDP residue `0`.
- Full `manifest.tsv`: `2,469` bytes; SHA-256 `1435B6E749FD57AB05D7C7A378742DB53B63F67C97C0EB00A3704C25238EE52A`; `23` subordinate rows, `0` missing, `0` mismatched, and `0` unlisted files.
- Frozen canary controller SHA-256: `CE40491EA34C915E854603686F341FC01E22D56067143A1547AF8A3D53728F34`.
- Frozen route controller SHA-256: `B2F56719A78FA36DC62F3153A2EF541707B9A1A2059EFF4AD25564852EAA4E92`.

The accepted Phase 1L.4b package remained exact before and after the attempt: `50` files, `1,051,962,028` bytes, `0` Python files; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A`; UFS SHA-256 `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356`. The protected map remained SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.

## Boundary and next gate

No source, product, runtime, package, map, config, test, art, route, accessibility, input, economy, or gameplay change follows. Phase 1K hands-on evidence and the Phase 1L.5a accessibility/input gaps remain deferred, incomplete, and not waived.

Phase `5/6` counts only after this local commit and verified two Notion upserts. There is no rerun. No Phase `6/6` work begins without a fresh Scope Director gate. See [[Development/Beta Delivery Roadmap]], [[Development/Current Plan]], and [[Design/Beta Game Bible]].
