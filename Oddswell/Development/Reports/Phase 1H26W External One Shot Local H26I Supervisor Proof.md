# Phase 1H.26W — External One-Shot Local H26I Supervisor Proof

**COMPLETE for one fixed exact H26U local-engineering handoff only.**

## Result

H26W implements the smallest supervisor authorized by [[Design/Decisions/DEC-019 Private Local Execution Supervisor Boundary]]. It is a separate manual, nonresident Python process outside the game and package. The no-argument command is:

`C:\Users\reali\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m phase1h.supervisor`

The supervisor fixes its H26W handoff, receipt, attempt, and log directories internally. It accepts no path, executable, module, seed, input, output, port, network target, or extra argument from a caller.

Ponytail reused `phase1h.execution` unchanged and added no dependency, service, watcher, scheduler, queue, backend, client launcher, or generalized framework.

## Authority and lifecycle

Before creating a child, the supervisor requires:

- the exact absolute allowlisted Python `3.12.13` executable and the same executable for its own process;
- the exact `28`-file frozen `phase0a`/`phase0d`/`phase1h` manifest, SHA-256 `6a92c3067e2cab3a14e70accd5f6c4b3bcf4df9b8cddbb3413950ea2301c137c`;
- exactly one fixed canonical H26U handoff; and
- no conflicting receipt or attempt set.

For a fresh commitment it creates one commitment-keyed attempt claim with create-new semantics, then launches at most one fixed child: the allowlisted interpreter, `-B -m phase1h.execution`, and the two fixed private directories. The child receives a minimal fixed environment with no `PATH` or inherited Python override. A Windows Job owns the child tree; the supervisor waits at most `120` seconds, terminates the Job on timeout, accepts only exit `0` and one exact bounded `executed:` or `duplicate:` line, independently validates the existing atomic receipt, writes one bounded private metadata record, and exits.

An exact existing receipt is validated in the supervisor and returns `duplicate` without launching a child. Race losers, an existing attempt without an exact receipt, crash, timeout, nonzero exit, unexpected output, malformed/tampered/multiple handoff, conflicting attempt, or forged/conflicting/multiple receipt stop without retry, overwrite, deletion, or repair.

The audit log contains only commitment hash, allowlisted interpreter identity/version, fixed module, start/end time, duration, status, exit code, and supervisor version. It never stores raw handoff data, seed material, frozen input, output digest, score, wager fields, secrets, or arbitrary child output.

## Twelve pre-registered acceptance gates

All twelve DEC-019 gates passed:

1. game source has no Python/process launcher and the package contains zero Python;
2. the supervisor is explicit/manual and rejects every argument before child creation;
3. interpreter, frozen revision, module, and directories are fixed and allowlisted;
4. arbitrary executable/module/path/argument/environment/port/network input cannot reach the child;
5. one fresh handoff creates one claim, launches one child, calls the existing consumer once, and creates one exact receipt;
6. concurrent supervisors launch exactly one child;
7. exact receipt returns duplicate without child execution or byte/hash/mtime change;
8. malformed/tampered/multiple handoff and forged/conflicting/multiple receipt stop without execution or repair;
9. timeout terminates the Job, retains the claim, and prevents automatic retry; crash follows the same retained-claim boundary;
10. clean exit `0`, exact output, and exact validated receipt are all required;
11. the private audit log is bounded and contains only approved metadata; and
12. frozen code/evidence remain exact and no H26J, result, or settlement artifact appears.

## Real packaged-to-external proof

The unchanged H26U Windows package ran in a fresh isolated H26W user directory. It completed the exact job `+100` → Harbor / `40` placement → H26G lock → H26H commitment → H26U handoff route and logged `python_consumer=false`, `process=false`, `receipt=false`, `simulation=false`, and `auto_h26j_to_h26p=false`. Before external invocation, private evidence contained only the `7,102`-byte handoff.

The manual external supervisor then produced:

- H26H commitment SHA-256 `335d8b798898627d3a39ad092b303487241a52b5659c0b0b2b1fa21e8c9ea1e7`;
- handoff: `7,102` bytes, file SHA-256 `1f5996d1382932f80262b0f816ee7cffd06237983cc6039fccfb28a736984225`;
- receipt: `515` bytes, file SHA-256 `4e2a1f37a63658055ff78c80c6fd145d93df85db8aa075373590d65ee8aa75a5`, status `executed_pending_seal`;
- attempt claim: `255` bytes; and
- private audit log: `915` bytes with exactly two records, `executed` then `duplicate`.

The second manual invocation returned `duplicate` without a child. Handoff and receipt bytes, SHA-256, and mtime remained exact. The receipt independently validated against the H26U handoff. There were zero seal, result, settlement, watcher, service, or backend artifacts after both invocations.

## Validation

- Focused H26W supervisor tests: PASS `12/12` in `0.731s`.
- Full Python simulator/brain/league/odds/execution suite: PASS `89` tests in `147.067s`.
- Full native Unreal automation: PASS `34/34`.
- Brain Admin Python compilation and self-check: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Unchanged final package: `50` files, `1,047,999,614` bytes, zero Python files.
- Game/client supervisor or Python-launch references: `0`.
- Lingering OddsWell, Unreal, or Python processes: `0`.
- Cost: `$0.00`.

Final evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26W-20260728`:

- `Focused-Supervisor-Tests-Final.log`
- `Full-Python-Tests-Final.log`
- `Full-Native-Tests-Final.log`
- `Brain-Admin-Self-Check-Final.log`
- `League-Export-Final.log`
- `Replay-Export-Final.log`
- `Packaged-Client-Boundary-Final.log`
- `UserDirFinal/Saved/PrivateExecution/Handoff`
- `UserDirFinal/Saved/PrivateExecution/Receipts`
- `UserDirFinal/Saved/PrivateExecution/SupervisorAttempts`
- `UserDirFinal/Saved/PrivateExecution/SupervisorLogs`

## Not delivered and next gate

H26W stops after one private H26I receipt. It does not seal the digest, record or publish a score, link a result, decide or settle a wager, start a service, call a backend, add a network path, change the client, bundle Python, or change any simulator or brain behavior.

The next Scope Director review may consider only whether one separate explicit external H26J seal invocation is the smallest truthful next proof. No automatic H26J-H26P chain is authorized.
