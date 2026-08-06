---
tags:
  - decision
  - beta
  - architecture
  - basketball
  - execution
  - security
status: accepted
date: 2026-07-27
---

# DEC-019 Private Local Execution Supervisor Boundary

## Decision

For local-beta engineering, the only recommended future H26I consumer authority is an **external, explicitly invoked, one-shot development supervisor**. It must run as a separate trusted developer process. The packaged client may write the H26U handoff but may never launch, bundle, watch, poll, or control Python.

This decision freezes an authority boundary for a separately approved implementation phase. It adds no supervisor, launcher, process, execution receipt, service, backend, dependency, runtime path, simulator behavior, or user interface.

## Options reviewed

| Option | Decision | Reason |
| --- | --- | --- |
| External opt-in local one-shot supervisor | **RECOMMEND AND FREEZE FOR LOCAL-BETA ENGINEERING** | Keeps execution outside the player client, preserves package-zero-Python, supports a bounded auditable local proof, and can reuse the existing exact `phase1h.execution` consumer without inventing a service. |
| Bundled or client-spawned Python | **REJECT** | Gives a player-controlled process authority over executable lookup and private paths, expands the package and attack surface, complicates lifecycle/crash handling, and violates the current game-to-private-handoff stop boundary. |
| Trusted backend worker | **DEFER** | It is the likely production authority direction, but accounts, authentication, trusted clocks, queues, deployment, operations, and backend ownership are not authorized or proved. |

## Current trust and call graph

The normal local-beta route is:

`player two-confirm placement → parameterless server wager transition → server tipoff timer → H26G lock → durable H26H commitment → H26U fixed private handoff → STOP`

The game-side authority ends at one canonical JSON file under `Saved/PrivateExecution/Handoff`. H26U accepts only a created file or an exact duplicate and does not spawn a process. The existing H26I development consumer is a separate manual command, `python -m phase1h.execution <handoff-directory> <receipt-directory>`. It requires exactly one valid handoff, executes the frozen simulator once, atomically writes one commitment-keyed opaque digest receipt, treats an exact receipt as a duplicate without re-execution or rewrite, and rejects conflicts without repair.

The Windows package contains zero Python files. Game source contains no sanctioned process launcher, and the repository has no approved watcher, service, or backend for this path.

## Frozen future local boundary

A future implementation may proceed only after separate approval and must satisfy all of these constraints:

- **Authority:** one separate trusted development process operated by an authorized developer; never the game client, player UI, Admin UI, or a player-controlled script.
- **Trigger:** one explicit opt-in invocation for one commitment. No automatic game callback, startup hook, watcher, polling loop, schedule, queue, port, network request, or background service.
- **Executable:** one normalized absolute interpreter path on an engineering allowlist. No `PATH`, environment-variable, registry, shell-association, handoff, or caller-controlled executable resolution.
- **Module and arguments:** invoke only the existing `phase1h.execution` module from the approved repository revision. The supervisor owns fixed private handoff and receipt directories; it accepts no arbitrary module, command, path, seed, input, output, port, or extra argument.
- **Single flight:** before a first execution, atomically create one commitment-keyed private attempt claim using create-new semantics. Only its creator may launch the child. An existing claim with no exact receipt means uncertain prior execution and must stop without retry or repair.
- **Duplicate:** if the exact receipt already exists, the existing consumer may validate and return `duplicate`; it must not call the simulator or rewrite bytes, hash, or mtime.
- **Lifecycle:** launch one child, wait at most `120` seconds, require a clean exit code `0`, capture bounded output, close all handles, and terminate the entire child process tree on timeout.
- **Cleanup:** never delete or rewrite the handoff, receipt, attempt claim, or conflicting evidence. Clean up only supervisor-owned temporary output after a cleanly identified failure. A crash or timeout remains a stopped, review-required state.
- **Logging:** write one private commitment-keyed engineering audit log containing only the commitment hash, allowlisted interpreter identity/version, fixed module, start/end time, duration, terminal status, and exit code. Never log raw seed material, frozen input, output digest, scores, wager fields, tokens, secrets, or arbitrary child output.
- **Failure:** missing, multiple, malformed, noncanonical, tampered, conflicting, wrong-version, or unexpected evidence; failed allowlist checks; duplicate workers; timeout; crash; nonzero exit; or unexpected output must stop. Nothing retries, repairs, falls back, seals, records a result, links a wager, or settles.

## Threat model

| Threat | Required control and failure result |
| --- | --- |
| Client or player launches the consumer | No game/client launcher exists; supervisor is external and explicitly developer-operated. Any client-spawn path fails review. |
| Executable, module, or path injection | Absolute interpreter allowlist, fixed module, fixed directories, fixed arguments; reject every override. |
| Duplicate workers or race | Atomic commitment-keyed attempt claim; only one child may start. Losers stop. |
| Crash after simulation but before receipt | Persist the attempt claim before launch. No automatic second attempt; stop for review. |
| Timeout or hung child | Hard `120`-second limit, terminate the full child tree, retain evidence and claim, and stop. |
| Handoff tamper or multiple handoffs | Existing exact validator rejects before simulation; no repair or selection heuristic. |
| Forged, conflicting, or multiple receipts | Existing receipt validator rejects before simulation; no overwrite or repair. |
| Sensitive data in logs | Allowlisted metadata only; never copy child output or private simulation material into general logs. |
| Supervisor grows into a service | One-shot lifecycle only; no ports, network, polling, watcher, scheduler, queue, or resident process. |

## Pre-registered implementation acceptance tests

A future implementation phase requires separate approval and must prove:

1. the game package still contains zero Python and game source still has no process-launch path;
2. only the explicit external developer trigger can start the supervisor;
3. interpreter, repository revision, module, handoff directory, and receipt directory are fixed and allowlisted;
4. arbitrary arguments, paths, modules, executables, environment overrides, ports, and network use reject before child creation;
5. one fresh exact H26U handoff creates one atomic claim, launches one child, calls the simulator once, and creates one exact atomic receipt;
6. concurrent supervisors for the same commitment launch exactly one child;
7. an exact existing receipt returns duplicate success without simulation or bytes/hash/mtime change;
8. malformed/tampered/multiple handoffs and forged/conflicting/multiple receipts stop without execution, overwrite, deletion, or repair;
9. crash and timeout retain the claim, create no automatic retry, terminate remaining child processes, and require manual review;
10. only clean exit `0` plus an exact validated receipt is success; unexpected output or nonzero exit is failure;
11. private audit logs contain only the approved metadata and no seed, input, digest, score, wager, secret, or arbitrary child output;
12. H26A-H26U evidence, frozen simulator/brain hashes, package contents, and the locked booth remain unchanged, with cost `$0.00`.

## Deferred production authority

A trusted backend worker remains deferred until the owner separately authorizes backend identity, authentication, queue ownership, deployment, observability, recovery, secrets, clock authority, and operational responsibility. This local supervisor design must not be treated as production wagering infrastructure.

## Phase 1H.26W implementation closure

Phase 1H.26W implements only the approved external local proof. The explicit command is the allowlisted Python `3.12.13` interpreter running `-B -m phase1h.supervisor` with no arguments. The supervisor fixes the H26W private handoff/receipt directories internally, verifies the unchanged `28`-file frozen Python manifest, atomically reserves one commitment-keyed attempt, launches at most one allowlisted `phase1h.execution` child, enforces the `120`-second Windows Job timeout, validates the exact receipt, writes bounded private metadata, and exits.

All twelve pre-registered tests passed. A fresh unchanged packaged client still stopped after H26U with zero Python, process, or receipt; the separate supervisor then created one exact receipt, and cold duplicate returned without child execution or byte/hash/mtime change. No H26J seal, result, settlement, service, watcher, network path, backend, client launcher, or packaged Python was added. See [[Development/Reports/Phase 1H26W External One Shot Local H26I Supervisor Proof]].
