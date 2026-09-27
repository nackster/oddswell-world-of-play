---
tags:
  - development
  - beta
  - character
  - review
status: rejected-visual-correction-required
date: 2026-09-27
---

# Phase 1L.5cd Combined Starter-Outfit Offline Visual Acceptance Review

## Verdict

`REJECTED_VISUAL_CORRECTION_REQUIRED`

Technical export/import preparation stops. The retained technical outfit remains stable and separated, but the starter top is not visually acceptable: its broad span, flat torso and nearly orthogonal shoulder-to-sleeve transition still read as a box/armor shell.

The smallest correction is to replace only the top shoulder/sleeve/side profile with rounded, body-conforming shaping. The exact body, shorts, DEC-035 skeleton and `walk_candidate_v1` must remain unchanged.

## Exact custody

- Source Blend SHA-256: `253E2680478A30133A0DC49614D9C997FEC06B70B42C470372CD0AF0CF44D7EA`.
- Body mesh: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Starter top: `20DEC799B15A77DC97EB4CCE521A84362AB952725ACD38C028918AABEC29C73C`.
- Starter shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- Armature: exact DEC-035 twelve-bone hierarchy.
- Action: `walk_candidate_v1` identity `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Review identity: `A770A549961A75312F5802308057928A8B3479F03A186DD9A45E2A8BBC5143C3`.
- Combined board: `1,111,234` bytes, SHA-256 `548C4F69E1CA2D68A82710F05B06A3A7E016B79362B04556CD96BA3AF141B1C1`.

Mesh, weights, materials, Action, skeleton, Unreal/client files and package inputs changed `0`.

## Criterion ledger

| Criterion | Result | Evidence |
|---|---|---|
| Separation | PASS | Every integer frame `1–21` retains zero evaluated body/top, body/bottom and top/bottom intersections. |
| Neckline / shoulders / sleeves / hem | FAIL | Neutral front/rear/profile show an over-wide, nearly orthogonal shoulder transition and flat torso shell. |
| Waistband / rise / crotch / legs | PASS | Neutral views retain a readable waistband, balanced rise/crotch split and two tapered legs at technical-proof fidelity. |
| Proportions | FAIL | The top span and straight side profile overpower the body and fitted shorts. |
| No rejected silhouettes | FAIL | Front/rear/profile remain visibly box/armor-like. |
| No exposure or collision | PASS | Five retained views show body coverage and the 21-frame ledger reports zero evaluated intersections. |
| Stable opposing extremes | PASS | Frames `6` and `16` retain coverage; root/armature translation is zero and frame `21` equals frame `1`. |

The machine-readable ledger is `starter_outfit_visual_acceptance.json`; its verdict is restricted to the two allowed states and fails closed when any criterion fails.

## Verification

- Evidence builder/rebuild and `--validate`: PASS; identity and board hash reproduced.
- Exact 1L.5cc cold Blender reopen: PASS; semantic identity `E56486E7D7DCB87586E6AFC9EF07E8FB85008D78F9231F75D9019B32D1D0E0C4`.
- Full frozen native automation: `75/75` PASS, exit `0`, failure markers `0`; log SHA-256 `D4423EACC11DD779C20AA6A6A1E3328325BE5E36208DFFC5A6ED5D6CD8D27B86`.
- Isolated frozen Python regression: `105/105` PASS in `168.188s` (`9 + 2 + 8 + 46 + 40`).
- Brain Admin self-check: PASS.
- Retained packaged character verification: locomotion, Studio/prompt presentation, camera, listen server and client PASS; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- Retained package payload remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Boundary

This is an offline visual decision record, not a new asset. It authorizes no export, import, runtime replacement, fabric/UV/material/LOD claim, performance claim, final character art, Phase 1L exit or beta readiness.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cd combined starter-outfit offline visual acceptance review]], [[Development/Reports/Phase 1L5cc Believable Starter Top Tailoring Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
