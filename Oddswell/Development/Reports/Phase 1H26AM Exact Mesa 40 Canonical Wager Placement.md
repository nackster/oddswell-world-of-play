# Phase 1H.26AM - Exact Mesa/40 Canonical Wager Placement

## Outcome

The normal physical ticket-booth flow can now place either exact current Match Winner selection at the approved `40`-Odds-Bucks stake. This phase adds the owner-approved Mesa Vista Sol route:

- the player selects Mesa and `40` at the Sundale ticket booth;
- the first confirmation only arms the bet and mutates nothing;
- the second confirmation sends one bounded selection flag to server authority;
- the server reloads the immutable current offer, maps that flag to exact Mesa, owns the offer ID, stake, odds, time, and request command, and invokes the existing atomic request/debit primitive;
- the ledger changes from the job-credit state `1/100` to `2/60` with one `-40` stake debit; and
- the existing authoritative pending receipt shows Mesa, probability `42413307`, decimal odds `2.3577`, stake `40`, potential gross return `94`, and `accepted_pending_lock`.

Harbor City Waves at `40` remains available through the same path.

## Smallest truthful implementation

Ponytail reused the H26Q graphical slip, H26R two-confirm interaction, H26E atomic request/debit, and H26F receipt. One exact Mesa/`40` server wrapper was added beside the retained Harbor wrapper. The RPC accepts only a bounded selection flag; raw offer IDs, team names, stakes, odds, times, balances, and command identities do not cross from the client.

The shared receipt validator now finds the exact offered selection in the immutable two-team offer instead of assuming selection zero. It still requires exactly one request, the exact `+100/-40` ledger, balance `60`, the selected probability and odds, the approved integer payout formula, and no forbidden downstream evidence.

## Safety boundary

- A first confirmation, team change, stake change, market-tab change, close, leave, or repeated input cannot debit the ledger.
- No selection, any stake other than `40`, insufficient balance, invalid offer evidence, tipoff, conflicts, and persistence failure remain fail-closed.
- The server allowlist maps the only two selection values to Harbor or Mesa and independently validates the current persisted offer.
- Only one current canonical request can exist because the immutable H26E command remains offer-owned and duplicate/conflict safe.

This phase does not add variable stakes, multiple wagers, another market, automatic simulation, automatic Mesa win decision/finalization/payout, generalized history, correction, online accounts, a trusted backend clock, deployment, real-money purchase, simulator behavior, or brain behavior.

## Verification

- Unreal Editor and Windows game builds: PASS.
- Focused native `OddsWell.Locomotion.CanonicalFortyPlacement`: `1/1` PASS.
- Full native OddsWell automation: `40/40` PASS.
- Frozen simulator/brain regressions: `105/105` PASS in `135.810s`.
- Brain Admin `--check` and Python compilation: PASS.
- Explicit `Bootstrap+SundaleGraybox` Windows BuildCookRun: PASS in `30.28s`.
- Package: `59` files, `1,048,537,267` bytes, zero Python files.
- Packaged end-to-end route: PASS for job `100` -> physical ticket booth -> Mesa `40` -> first confirm with zero mutation -> second confirm -> exact debit -> pending receipt.
- Packaged receipt: Mesa, stake `40`, gross return `94`, ledger entries `2`, requests `1`, balance `60`.
- Repeated packaged input after durable success: zero additional mutation.
- Cost: `$0.00`.

## Roadmap and next gate

This advances the Beta Game Bible's **First-hour player journey / Place and watch the first wager**, **Basketball and wagering / Beta wager markets**, **Wager integrity**, and **Odds Bucks economy** sections for the one exact current Match Winner offer.

Stop for fresh Scope Director review. The smallest likely follow-up is a separately approved automatic normal-player Mesa-win lifecycle using the already proven H26AI/H26AJ decision and finalization primitives. That would apply a payout and must not be inferred from this placement phase.
