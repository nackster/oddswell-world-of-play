# Deterministic shared-skeleton character FBX export provenance

Phase 1L.5bs exports only the exact retained Phase 1L.5bq Blender source under the frozen Phase 1L.5br handoff contract at `$0.00`.

- Source `.blend`: `B837C11190DE64F5848F4880FA0098473DFAA3C8BA4E5D8564566587E11721FE`.
- Source custody manifest: `499A4622BF744B936513BD6BC42309A3C83FB1D52DA70C4196FB5D4C2B898ABC`.
- Frozen handoff contract: `3DAA1D94A19148F03D31682D15B2FA40D9D43133008A1DA099097FCC4AAD88C6`.
- Partition: exactly four skeletal-mesh FBXs and four animation-only FBXs, each with one uppercase SHA-256 sidecar.
- Determinism gate: two isolated exports must produce the same binary SHA-256 for every named FBX before outputs are accepted.
- Export process: Blender must start with `PYTHONHASHSEED=0` so FBX object identifiers remain stable across independent invocations.
- Skeleton gate: exact retained 12-bone shared skeleton, no leaf bones, no renamed or added bones, and exact-zero animation root translation.

This proof performs no Unreal import, creates no UAsset, and changes no Blender source, rig, Action, mesh, clothing, runtime, client, map, configuration, package input, gameplay authority, persistence, economy, wager, simulator, brain, final-art status, or readiness status.
