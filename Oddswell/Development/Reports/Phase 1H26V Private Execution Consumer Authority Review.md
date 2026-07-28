# Phase 1H.26V — Private Execution-Consumer Authority Review

**COMPLETE as a design-only local-beta authority and threat-model gate.**

## Outcome

H26V recommends and freezes one future local engineering boundary: a separate, explicitly invoked, one-shot trusted development supervisor may consume the exact H26U handoff only after its own implementation phase is approved. The packaged client must continue to stop after H26U and may not launch or bundle Python.

The full accepted boundary is recorded in [[Design/Decisions/DEC-019 Private Local Execution Supervisor Boundary]]. H26V adds no code, process, simulator execution, receipt, launcher, watcher, service, backend, dependency, UI, or runtime behavior.

## Current authority inventory

The current normal chain is:

`player two-confirm placement → server request/debit → server tipoff timer → H26G lock → durable H26H commitment → H26U fixed private handoff → STOP`

H26U runs inside the existing native GameMode authority, calls the existing parameterless handoff writer, and accepts only `Created` or exact immutable `Duplicate`. Its fixed private canonical JSON is the last automatic artifact. No game-side caller supplies executable, module, path, seed, simulator input, time, output, or receipt data.

The existing H26I consumer remains the manual offline command `python -m phase1h.execution <handoff-directory> <receipt-directory>`. It requires exactly one canonical handoff, executes the frozen simulator once, writes one commitment-keyed receipt atomically, returns exact duplicate without re-execution or rewrite, and rejects malformed/conflicting evidence without repair.

Read-only inventory found:

- final H26U Windows package: `50` files, `1,047,999,614` bytes, zero Python files;
- no process-launch API reference in `client/OddsWell/Source`;
- no sanctioned launcher, watcher, service, or backend for private execution;
- no game callback, port, network route, polling loop, or resident consumer;
- `28` frozen Python files across `phase0a`, `phase0d`, and `phase1h`, with aggregate manifest SHA-256 `6a92c3067e2cab3a14e70accd5f6c4b3bcf4df9b8cddbb3413950ea2301c137c`.

## Exactly three options reviewed

| Option | Result | Boundary |
| --- | --- | --- |
| External opt-in local one-shot supervisor | **RECOMMENDED / FROZEN** | Separate trusted development process; fixed private directories; absolute allowlisted interpreter; existing `phase1h.execution` only; one commitment and one bounded attempt. |
| Bundled or client-spawned Python | **REJECTED** | Violates package-zero-Python and the H26U stop boundary while exposing executable/path injection and player-client process authority. |
| Trusted backend worker | **DEFERRED** | Requires separate authorization and evidence for accounts, authentication, queues, trusted clock, deployment, recovery, secrets, observability, and operational ownership. |

## Frozen lifecycle and failure semantics

The recommended future supervisor is manual, one-shot, non-networked, and nonresident. It accepts no arbitrary executable, module, directory, argument, port, seed, input, output, or environment override. It uses an absolute allowlisted interpreter, the approved repository revision, the existing module, and fixed handoff/receipt directories.

Before first execution it must atomically reserve one commitment-keyed attempt. One process may win. An exact existing receipt is validated as duplicate without simulator execution or rewrite. A claim without an exact receipt represents uncertain prior execution and stops without automatic retry or repair.

One child may run for at most `120` seconds. Success requires clean exit `0` and one exact validated receipt. Timeout terminates the complete child process tree. Crash, timeout, nonzero exit, malformed output, missing/multiple/tampered handoff, forged/conflicting/multiple receipt, allowlist failure, or duplicate-worker race stops the chain. The supervisor retains authoritative evidence and the attempt claim, never repairs or falls back, and never advances to H26J-H26P.

Private logs are limited to commitment hash, allowlisted interpreter identity/version, fixed module, start/end time, duration, terminal status, and exit code. Seed material, frozen input, output digest, score, wager data, secrets, and arbitrary child output are forbidden from general logs.

## Threat review

The design explicitly addresses client spawning, executable/module/path injection, duplicate workers, races, crash ambiguity, timeout, handoff tamper, forged receipts, accidental repair, sensitive logging, and service creep. The accepted controls and twelve separately approved future acceptance tests are in DEC-019.

## Evidence and hygiene

- This phase changes documentation and one roadmap canvas only.
- H26A-H26U runtime code and evidence remain unchanged.
- Frozen league export remains `30,288` bytes with SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Frozen replay export remains `421` frames and `256,442` bytes with SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- All Obsidian canvases parse as JSON.
- Cost: `$0.00`.

## Not delivered and next gate

No supervisor implementation is authorized by this review. No process may start and no receipt may be created as part of H26V.

The next Scope Director gate is a separate go/no-go review against DEC-019's pre-registered tests. Approval may authorize only the smallest external local supervisor proof; it may not authorize client-spawned Python, bundled Python, a service, a backend, networking, or automatic H26J-H26P execution.
