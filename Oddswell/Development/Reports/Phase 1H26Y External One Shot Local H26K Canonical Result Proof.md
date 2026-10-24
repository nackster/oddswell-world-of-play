# Phase 1H.26Y — External One-Shot Local H26K Canonical Result Proof

**COMPLETE for one fixed exact H26W/H26X evidence chain only.**

## Result

H26Y adds one separate, explicit, nonresident local-engineering command for the already implemented H26K private result recorder:

`C:\Users\reali\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m phase1h.result_supervisor`

The command accepts no arguments. It reuses the H26W interpreter, frozen-revision, child-process, Windows Job, timeout, output, claim, and audit controls plus the H26X seal boundary. It reads only the fixed H26W handoff and receipt and fixed H26X seal, then writes only to separate fixed H26Y result, attempt, and log directories.

Ponytail reused `phase1h.execution` and its H26K recorder unchanged. No dependency, generalized pipeline, automatic chain, client launcher, service, watcher, queue, backend, network, public replay, UI, or Admin feature was added.

## Authority and independent validation

Before child creation the supervisor requires:

- the absolute allowlisted Python `3.12.13` interpreter;
- the unchanged `28`-file frozen runtime manifest SHA-256 `6a92c3067e2cab3a14e70accd5f6c4b3bcf4df9b8cddbb3413950ea2301c137c`;
- H26W supervisor-control SHA-256 `5ab65177e9fba3149b014b95ff7cb93b04f07e25028c41abdbe0e73d631686ef`;
- H26X seal-supervisor-control SHA-256 `7a49cc3f912241d1b0e5140c403d83d4f67b4b139b47e006d2a67e80ded3d716`;
- exactly one valid fixed handoff, receipt, and seal; and
- approved canonical result-record SHA-256 `05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`.

For a fresh commitment it reserves one separate commitment-keyed result attempt with create-new semantics, then launches at most one fixed child: the allowlisted interpreter, `-B -m phase1h.execution`, and the four fixed handoff, receipt, seal, and result directories. The child tree remains bounded by the existing `120`-second Windows Job. Only exit `0` and one exact bounded `recorded:` or `duplicate:` line are accepted.

After the child exits, the supervisor independently validates exact canonical JSON, schema/version/status, commitment and seal links, Season `1`/Game `1`, scheduled team identities, nonnegative integer scores, no tie, winner derived from the score, replay digest equal to H26J, record hash, and the fixed approved record hash. The fixed record hash lets an exact cold duplicate skip both child creation and simulation while still rejecting a validly rehashed score change.

No caller controls a team, score, winner, seed, simulator input, replay digest, record hash, path, module, executable, or output. Race losers, uncertain attempts, crash, timeout, nonzero exit, unexpected output, missing/malformed/tampered/multiple upstream evidence, conflicting attempts, and malformed/tampered/multiple results stop without retry, overwrite, deletion, or repair.

## Real external proof

The fixed chain used commitment `335d8b798898627d3a39ad092b303487241a52b5659c0b0b2b1fa21e8c9ea1e7`, H26J seal SHA-256 `580932546f3041bb3961cf14757b536c31c289d91f984fd0ae1418b98f0ff4ef`, and replay digest `35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db`.

The first manual invocation produced:

- one `249`-byte result-attempt claim, file SHA-256 `3cafaae7ab43d03bfb4618ed91922820f26b9e966f44d4498f6bd1caa9cce691`;
- one `660`-byte canonical result, file SHA-256 `cbadfb9730c5de673b8c76b0a6cf88391a9968ae5c67a43dedae930b0ec8481b`;
- status `recorded_pending_decision`;
- Harbor City Waves `79`, Mesa Vista Sol `113`; and
- winner Mesa Vista Sol.

The second manual invocation returned `duplicate` without child creation or simulation. The result, handoff, receipt, and seal retained exact bytes, SHA-256, and mtime. The bounded `909`-byte audit log contains exactly `recorded` then `duplicate` and contains no score, winner, team, seed, digest, or replay field. There are zero H26L link, decision, settlement, history, ledger, or player/Admin artifacts.

The unchanged H26U Windows package also ran in a fresh isolated H26Y user directory. It produced one private handoff only and reported `python_consumer=false`, `receipt=false`, and `auto_h26j_to_h26p=false`. The game does not launch H26W, H26X, or H26Y.

## Validation

- Focused H26Y result-supervisor tests: PASS `8/8`; combined H26W/H26X/H26Y supervisors: PASS `28/28` in `2.283s`.
- Full Python simulator/brain/league/odds/execution suite: PASS `105` tests in `139.608s`.
- Full native Unreal automation: PASS `34/34`.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Unchanged final package: `50` files, `1,047,999,614` bytes, zero Python files.
- Client process-launch references: `0`.
- Lingering relevant processes: `0`.
- Cost: `$0.00`.

Final evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26Y-20260728`.

## Not delivered and next gate

H26Y stops at one private `recorded_pending_decision` result. It does not create H26L or later wager links, decisions, finalizations, settlement, history, UI, Admin surfaces, public replay, statistics, standings, a service, backend, network path, client Python path, simulator change, or brain change.

The next Scope Director review may consider only whether one separate H26L result-link invocation is the smallest truthful next proof. No automatic H26L–H26P chain is authorized.
