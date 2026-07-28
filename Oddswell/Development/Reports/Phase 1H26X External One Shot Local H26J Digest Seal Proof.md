# Phase 1H.26X — External One-Shot Local H26J Digest Seal Proof

**COMPLETE for one fixed exact H26W receipt only.**

## Result

H26X adds one separate, explicit, nonresident local-engineering command for the already implemented H26J digest-seal boundary:

`C:\Users\reali\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m phase1h.seal_supervisor`

The command accepts no arguments. It reuses the H26W interpreter, frozen-revision, child-process, Windows Job, timeout, output, and audit controls. It also pins the exact H26W supervisor control file, reads only the fixed H26W handoff and receipt directories, and writes only to separate fixed H26X seal, attempt, and log directories.

Ponytail reused `phase1h.execution` and its H26J verifier unchanged. No dependency, generalized runner, client launcher, automatic chain, service, watcher, queue, backend, or network path was added.

## Authority and lifecycle

The supervisor requires the absolute allowlisted Python `3.12.13` interpreter, the unchanged `28`-file frozen runtime manifest SHA-256 `6a92c3067e2cab3a14e70accd5f6c4b3bcf4df9b8cddbb3413950ea2301c137c`, H26W supervisor-control SHA-256 `5a892d3f045069d6ba3b157203d298c80be95c312687d3cd643e0602cdc99b6a`, exactly one valid fixed handoff, and exactly one valid fixed `executed_pending_seal` receipt.

For a fresh commitment it creates one separate commitment-keyed seal-attempt claim with create-new semantics, then launches at most one fixed child: the allowlisted interpreter, `-B -m phase1h.execution`, and the three fixed handoff, receipt, and seal directories. The child tree remains bounded by the existing `120`-second Windows Job. The supervisor accepts only exit `0` and one exact bounded `sealed:` or `duplicate:` line, independently validates the resulting canonical seal, writes bounded private metadata, and exits.

An exact existing seal is independently validated and returns `duplicate` without creating an attempt or child and without rewriting the seal. A race loser, uncertain prior attempt, crash, timeout, nonzero exit, unexpected output, missing/malformed/tampered/multiple upstream evidence, conflicting attempt, or malformed/tampered/multiple seal stops without retry, overwrite, deletion, or repair.

## Real external proof

The fixed H26W evidence supplied commitment `335d8b798898627d3a39ad092b303487241a52b5659c0b0b2b1fa21e8c9ea1e7`, a `7,102`-byte handoff with file SHA-256 `1f5996d1382932f80262b0f816ee7cffd06237983cc6039fccfb28a736984225`, and a `515`-byte receipt with file SHA-256 `4e2a1f37a63658055ff78c80c6fd145d93df85db8aa075373590d65ee8aa75a5`.

The first manual H26X invocation produced:

- one `245`-byte seal-attempt claim, file SHA-256 `f29fefc7db3597cdcfdb0580bc6140d08fd180749ff5a3feebf8301a9d23e2ab`;
- one `671`-byte canonical seal, file SHA-256 `bcf8fc469c90720af0acf31ff9c8c87209ae43674c1fd3b1336444357361416f`;
- seal status `sealed_pending_result`; and
- verified digest `35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db`, exactly matching the H26I receipt.

The second manual invocation returned `duplicate`. The seal and both upstream files retained exact bytes, SHA-256, and mtime. The bounded `903`-byte audit log contains exactly `sealed` then `duplicate`. There are zero H26K result, score, winner, settlement, or player artifacts.

The unchanged H26U Windows package also ran in a fresh isolated H26X user directory. It completed the H26U boundary with `python_consumer=false`, `process=false`, `receipt=false`, `seal=false`, and `auto_h26j_to_h26p=false`; private packaged evidence contained only its handoff. The external H26X command is not launched by the game.

## Validation

- Focused H26X seal-supervisor tests: PASS `8/8`; combined H26W/H26X supervisors: PASS `20/20` in `1.340s`.
- Full Python simulator/brain/league/odds/execution suite: PASS `97` tests in `135.037s`.
- Full native Unreal automation: PASS `34/34`.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Unchanged final package: `50` files, `1,047,999,614` bytes, zero Python files.
- Client process-launch references: `0`.
- Lingering approved Python or Unreal processes: `0`.
- Cost: `$0.00`.

Final evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26X-20260728`.

## Not delivered and next gate

H26X stops at one private `sealed_pending_result` digest seal. It does not record or publish a score, winner, statistics, replay, or result; link a wager; decide or settle a wager; modify the client; bundle Python; start a service; call a backend; use a network; or change simulator or brain behavior.

The next Scope Director review may consider only whether one separate explicit external H26K result invocation is the smallest truthful next proof. No automatic H26K–H26P chain is authorized.
