# Phase 1H.26AI - Exact Current-Offer Mesa 40 Win-Decision Compatibility and Isolated Proof

## Outcome

The server-owned Match Winner decision engine now accepts one additional exact winning evidence chain: the current canonical offer with Mesa selected for `40` Odds Bucks and the authoritative `79-113` Mesa result.

The decision is:

- selected team: Mesa Vista Sol;
- authoritative winner: Mesa Vista Sol;
- outcome: `won`;
- selected probability: `42413307` on the `1e8` scale;
- decimal odds: `23577` on the `1e4` scale;
- stake: `40` Odds Bucks;
- gross return due: `94` Odds Bucks; and
- status: `decided_pending_apply`.

The approved integer formula is unchanged:

`floor(40 * 100000000 / 42413307) = 94`

## Exact authority boundary

The new compatibility path accepts only the fixed current identity:

- offer: `c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d`;
- public commitment: `898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f`;
- result: `05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`;
- replay: `35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db`;
- Season `1`, Game `1`, Harbor City Waves home, Mesa Vista Sol away; and
- final score Harbor `79`, Mesa `113`.

The retained approved legacy win and current Harbor-loss routes are unchanged. Missing offer evidence, a tampered offer, missing result evidence, internally re-priced request evidence, a foreign result, and a conflicting second decision all reject without mutation. Exact cold retry returns `Duplicate` and preserves the SaveGame bytes.

## Economy boundary

H26AI decides the win only. The isolated ledger remains:

- sequence `1`: job `+100`;
- sequence `2`: wager stake `-40`;
- balance: `60`; and
- ledger entry count: `2`.

There is no `+94` payout entry, win finalization, reconciliation publication, player receipt, normal-player Mesa placement route, or automatic transition. Applying the return would require a separate owner-approved phase.

## Verification

- Focused H26AI native automation: `1/1` PASS.
- Retained H26M Harbor-loss automation: `1/1` PASS.
- Full native OddsWell automation: `39/39` PASS.
- Frozen Python regression: `77/77` PASS in `158.277s`.
- Supervisor regression: `28/28` PASS in `2.595s`.
- Combined Python evidence: `105/105` PASS.
- Brain Admin `--check`: PASS.
- Python compilation: PASS.
- Deterministic public league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic archived replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.
- Unreal editor build: PASS.
- Unreal Windows Development game build: PASS in `26.20s`.
- Explicit `Bootstrap+SundaleGraybox` Windows BuildCookRun: PASS in `75.08s`.
- Package audit: `50` files, `1,048,325,759` bytes, zero Python files.
- Cost: `$0.00`.

## Scope boundary and next gate

H26AI proves only the exact current Mesa/`40` win decision. It does not apply the return, finalize the win, publish history, show a receipt, generalize offers, add multiple wagers or markets, change basketball simulation, change any brain, add a backend, or connect real money.

The next implementation requires fresh Scope Director and owner review. The smallest possible candidate is a separate H26AJ atomic `+94` return application and immutable `settled_won` finalization, but it is not authorized by this phase.
