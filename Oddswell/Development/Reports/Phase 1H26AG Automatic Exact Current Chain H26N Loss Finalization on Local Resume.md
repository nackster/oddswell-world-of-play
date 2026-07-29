# Phase 1H.26AG — Automatic Exact Current-Chain H26N Loss Finalization on Local Resume

## Outcome

The exact current Harbor-selected, Mesa-winner loss now advances automatically from a durable H26M decision to the existing H26N loss finalization during authoritative local resume. The implementation is deliberately one private wrapper around the existing parameterless transition; it adds no generalized settlement machinery.

Fresh packaged startup proved the normal non-QA chain:

`H26AE Linked -> H26AF Decided -> H26AG Finalized`

The final state is one exact `settled_lost` record, return due/applied `0`, ledger entries `2`, last delta `-40`, and balance `60`. No credit, payout, refund, correction, or third ledger entry exists.

## Exact acceptance predicate

H26AG accepts only the fixed current chain:

- request `canonical:h26e:match_winner:request:c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d`;
- lock for that exact request;
- result `canonical:h26l:match_winner:result:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`;
- decision `canonical:h26m:match_winner:decision:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`;
- finalization `canonical:h26n:match_winner:finalization:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`;
- Harbor City Waves selected, Mesa Vista Sol winner, stake `40`, outcome `lost`;
- gross return due/applied `0`, status `settled_lost`, one loss finalization, zero win finalizations; and
- ledger `+100,-40`, entry count `2`, balance `60`.

Memory is updated only after the state reload proves the entire predicate. On cold restore, the existing H26M transition first returns its exact approved no-later-state rejection because H26N already exists; only that exact message permits the wrapper to ask H26N for an exact `Duplicate`. Any other rejection stops.

## Fail-closed evidence

- Missing private H26K evidence returned H26AE `NOOP`; the `5,502`-byte source save retained SHA-256 `74acbe35ef6a374a9efaced5d85a60e62f49f33659553bc8dd7633f89ded2525` and exact mtime. No reconciliation projection or H26AG event appeared.
- Tampered private evidence returned H26AE `REJECTED` for conflict with exact H26H/H26J evidence. The same source bytes, hash, and mtime remained stable; no projection or H26AG event appeared.
- Retained native H26N coverage rejected missing/tampered identity, winning or nonloss state, nonzero applied return, third ledger entry, foreign/downstream state, and persistence failure without mutation or repair.

## Persistence and projection evidence

Fresh finalization produced the expected `10,082`-byte SaveGame with SHA-256 `4cb4a0f70d45feef46da1dfb88f6086b05b85fbb82fcb90148c3e08dc66f9366`. Cold restart returned H26AG `Duplicate`; SaveGame length, bytes, SHA-256, and mtime stayed exact, and ledger state remained `2/-40/60`.

The reused H26N loader necessarily regenerates the already existing H26O Match Winner reconciliation projection and the general Odds Bucks reconciliation projection. Fresh and cold checks validated the regenerated JSON semantically against the exact request/result/decision/finalization identity and ledger. No projection byte or mtime stability is claimed. H26AG adds no projection writer, endpoint, Admin card, ticket-booth receipt, or other H26O/H26P work.

## Verification

- editor and game builds: PASS;
- focused H26AG: `1/1` PASS;
- retained H26AF: `1/1` PASS;
- retained H26N: `1/1` PASS;
- full native OddsWell suite: `37/37` PASS;
- frozen Python suite: `105/105` tests plus `119` subtests PASS;
- separate supervisors: `28/28` tests plus `13` subtests PASS;
- timing-sensitive paired policy evaluation at High priority: PASS;
- Brain Admin supported `--check`: PASS;
- Python compilation and deterministic league/replay exports: PASS;
- final Windows BuildCookRun: PASS in `195.17s`;
- final package: `50` files, `1,048,202,878` bytes, zero Python; and
- cost: `$0.00`.

For audit transparency, the first Brain Admin attempt used the nonexistent `--self-check` flag and argparse rejected it before work; the corrected `--check` command passed. The first package caller timed out after five seconds but left its UAT child active; a competing retry then correctly refused the live mutex. The original single UAT process completed the accepted package successfully. No preliminary failure is counted as accepted evidence.

## Scope boundary

No timer, poller, watcher, service, backend, deployment, paid API, retraining, new dependency, schema, caller-controlled settlement input, UI, Admin feature, credit, purchase, real-money path, simulator change, or brain change was added. The next implementation requires a fresh Scope Director decision.
