# Phase 1L.5a Current First-Hour Accessibility Evidence Inventory

**Date:** 2026-08-13
**Status:** COMPLETE — READ-ONLY CURRENT-EVIDENCE INVENTORY; VERIFIED AT COMMIT `91cddb3cf82d56ea2c0426e903560a3a3620c966` WITH NOTION CLOSURE COMPLETE
**Scope:** Eleven named first-hour surfaces; existing accepted evidence and current source only
**Cost:** $0
**Cursor tasks:** 0

## Verdict

This is a descriptive inventory of evidence currently retained for eleven first-hour surfaces. It is not an accessibility standard, compliance score, remediation plan, readiness finding, or new playtest. `EVIDENCED` means the cited artifact directly supports only that cell. `ABSENT` means inspected current source or an accepted artifact directly demonstrates absence. `NOT APPLICABLE` is used only for a surface-specific content reason. Everything else is `UNPROVEN`.

The inventory contains 143 classified cells: **54 EVIDENCED, 39 ABSENT, 18 NOT APPLICABLE, and 32 UNPROVEN**. Automated and source evidence does not prove physical hardware use, human recognition, comprehension, hesitation, usability, accessibility, or contiguous first-hour completion. Phase 1K physical proof remains incomplete, deferred, and not waived.

## Status key

| Status | Meaning in this report |
|---|---|
| EVIDENCED | Direct accepted evidence exists for this exact surface and field. |
| ABSENT | Current inspected source or accepted evidence directly shows the capability/evidence is absent. |
| NOT APPLICABLE | The named surface does not contain the relevant content type. |
| UNPROVEN | No direct retained evidence supports a stronger classification. |

## Matrix

Abbreviations: `E` = EVIDENCED, `A` = ABSENT, `N` = NOT APPLICABLE, `U` = UNPROVEN. “Standard” means exact 1280x720 evidence; “Compact” means exact 888x500 evidence. Source mappings establish implementation only, never physical use.

| # | Surface | Keyboard | Mouse | Controller | Physical hardware | Standard | Compact | Fixed-view clipping | Text / non-color state | Contrast | Motion / skip | Captions | Remapping | Human/manual |
|---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Character chooser | E | A | E | U | E | U | E | U | U | N | N | A | A |
| 2 | Sundale destination/route cues | E | E | E | U | E | U | N | E | U | U | N | A | A |
| 3 | Studio enter/leave prompt | E | A | A | U | E | E | E | E | U | N | N | A | A |
| 4 | Job interaction prompt | E | A | A | U | E | E | E | E | U | N | N | A | A |
| 5 | Ticket-booth browser | E | E | E | U | U | E | E | E | U | N | N | A | A |
| 6 | Stadium watch / player-S skip | E | A | A | U | E | U | E | E | U | E | N | A | A |
| 7 | Settled wager receipt | E | U | U | U | E | E | E | E | U | N | N | A | A |
| 8 | Clothing purchase/equip feedback | E | A | A | U | E | E | E | E | U | A | N | A | A |
| 9 | Furniture purchase feedback | E | A | A | U | E | E | E | E | U | A | N | A | A |
| 10 | Housing upgrade feedback | E | A | A | U | E | E | E | E | U | A | N | A | A |
| 11 | Athlete-story pages | E | A | A | U | E | U | E | E | U | N | N | A | U |

### Per-surface basis and limitations

1. **Character chooser.** `CharacterSelectionScreen.cpp:22-25,106-120` directly binds keyboard arrows/WASD, controller D-pad, Enter/Space, and controller A. The inspected chooser source contains no mouse binding or hitbox and no remapping UI. The accepted 1280x720 no-input capture shows all eight cards without observed clipping. There is no accepted 888x500 chooser capture. The selected presentation uses visual border/background state, but direct text-or-symbol redundancy evidence was not retained. The phase explicitly used automated no-input evidence, not a human or physical-device session. Citations: [[Phase 1L1n Default Character Chooser Presentation Pass]]; `client/OddsWell/Source/OddsWell/CharacterSelectionScreen.cpp`.

2. **Sundale destination/route cues.** Current movement/look mappings directly cover keyboard, mouse look, and controller movement/look in source, but not physical-device use. Accepted 1280x720 views directly show the reviewed destination shapes. The destination identity contract uses distinct silhouettes and does not require text, so fixed-view text clipping is not applicable and the non-color shape distinction is evidenced. Player and camera locomotion make motion/skip applicable, but no exact motion-reduction or skip evidence is retained. No accepted compact evidence, contrast measurement, or human wayfinding/comprehension evidence is retained. Citations: [[Phase 1L1b Sundale Destination Identity Wayfinding Pass]]; `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp`.

3. **Studio prompt.** Current source binds the interaction to keyboard `E`; the inspected exact prompt path contains no mouse or controller interaction equivalent and no remapping UI. Accepted 1280x720 and 888x500 enter/leave originals show the complete exact prompt text with no observed clipping or overlap. This is a static text prompt with no audio/video content, so motion/skip and captions are not applicable to the prompt itself. Contrast and physical/human use remain unproven. Citations: [[Phase 1L1t Studio Entry Exit Prompt Presentation Pass]]; `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp`.

4. **Job prompt.** Current source binds the interaction to keyboard `E`; the inspected exact prompt path contains no mouse or controller interaction equivalent and no remapping UI. Accepted 1280x720 and 888x500 originals show the complete exact prompt without observed clipping or prompt/result overlap. This is a static text prompt with no audio/video content. Contrast and physical/human use remain unproven. Citations: [[Phase 1L1u Job Interaction Prompt Presentation Pass]]; `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp`.

5. **Ticket-booth browser.** The accepted source contract directly supports mouse tabs/close, keyboard left/right plus `E`/Escape, and controller shoulder/face-right actions. Active and locked states are expressed in text as well as color. The exact standard image retained by the browser phase is 1280x800, not 1280x720, so the requested standard cell is unproven. The accepted corrected 888x500 original has no observed clipping/overlap. The static, text-only browser has no caption or motion/skip content in scope. Direct bindings and absence of a remapping interface make remapping absent; physical/human use and contrast remain unproven/absent as classified. Citations: [[Phase 1H24 Graphical Ticket Booth Basketball Market Browser]]; [[Phase 1L1h Ticket Booth Compact Layout Correction]]; `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp`.

6. **Stadium watch/player-S skip.** Current source directly binds player `S` to skip and the accepted replay evidence exercises that same path; no mouse/controller skip binding or remapping UI was found in the inspected replay/input path. The accepted 1280x720 public-view image directly supports the fixed standard presentation and no observed text clipping. Replay callouts communicate state in text, not color alone. The current presentation has motion and an explicit skip, so that field is evidenced. The reviewed presentation has no voice commentary, making captions not applicable to this surface's current audio content; this is not a global caption finding. No compact, contrast, physical-device, or human-watch evidence is retained. Citations: [[Phase 1F4 Readable Three Minute Stadium Presentation]]; [[Phase 1F5 Replay View Result Invariance]]; [[Phase 1L1i Stadium Public Viewing Presentation Pass]]; `client/OddsWell/Source/OddsWell/ReplayBenchmarkActor.cpp`.

7. **Settled wager receipt.** Accepted 1280x720 and 888x500 originals directly show the complete receipt hierarchy and exact settled values without observed clipping. Keyboard `E`/Escape behavior is directly retained. Exact mouse/controller behavior for this receipt was not retained separately and remains unproven. The receipt is static text with no animation, audio, or video, making motion/skip and captions not applicable. No remapping UI is present in the inspected fixed-input path; contrast and physical use remain unproven, and the phase contains no human/manual test. Citation: [[Phase 1L1o Settled Wager Receipt Presentation Pass]].

8. **Clothing feedback.** Current source directly uses keyboard `E`; no mouse/controller interaction equivalent or remapping UI exists in the inspected exact path. Accepted 1280x720 and 888x500 purchase/equip originals show complete exact state text without observed clipping. The five-second panel has no user skip in the inspected path. It is text-only with no captionable content. Contrast and physical use remain unproven; the phase contains no human/manual test. Citation: [[Phase 1L1q Signal Jacket Purchase and Equip Feedback Presentation Pass]].

9. **Furniture feedback.** Current source directly uses keyboard `E`; no mouse/controller interaction equivalent or remapping UI exists in the inspected exact path. Accepted 1280x720 and 888x500 originals show the complete exact purchase state without observed clipping. The five-second panel has no user skip and no captionable audio/video content. Contrast and physical use remain unproven; the phase contains no human/manual test. Citation: [[Phase 1L1r Modular Chair Purchase Feedback Presentation Pass]].

10. **Housing feedback.** Current source directly uses keyboard `E`; no mouse/controller interaction equivalent or remapping UI exists in the inspected exact path. Accepted 1280x720 and 888x500 originals show the complete exact upgrade state without observed clipping. The five-second panel has no user skip and no captionable audio/video content. Contrast and physical use remain unproven; the phase contains no human/manual test. Citation: [[Phase 1L1s One Bedroom Upgrade Feedback Presentation Pass]].

11. **Athlete-story pages.** Current source directly binds keyboard `L`, comma, and period. The inspected exact league-page input path contains no mouse/controller equivalent or remapping UI. The accepted 1280x720 original directly supports the fixed page presentation and no observed clipping. The page fields and explanations are textual, not color-only. The page is static and has no audio/video content, making motion/skip and captions not applicable. No accepted 888x500 capture or contrast measurement is retained. Earlier participant evidence was not retained with a sufficiently exact citation during this bounded audit, so human/manual evidence is conservatively `UNPROVEN` rather than transferred from another phase. Citation: [[Phase 1J1 Public Athlete Story Pages]].

## Accepted image ledger

Image hashes are transcribed only where an accepted source report publishes the exact identity. The linked report paths and source anchors above remain the classification citations.

| Surface | Artifact | Resolution | Bytes | SHA-256 | Disposition |
|---|---|---:|---:|---|---|
| Chooser | `C:\tmp\OddsWellPhase1L1n\NoInputUser\Saved\Screenshots\Windows\ScreenShot00000.png` | 1280x720 | 57,269 | `171545CC16AC3EE2FBFE13218042C5AB51455EE5F5CC5A824F7943C894844407` | ACCEPTED |
| Route cues | Studio/start close view | 1280x720 | 1,163,928 | `FEB97A9383A513DF8F76266C69D37973600E9B29B7727D126DFACFCD953F0EA5` | ACCEPTED |
| Route cues | Arena-return close view | 1280x720 | 1,073,665 | `43328EF05F249A1FA08BCBCAC0C03990ACC46FA577CF010AFB42D0BB04A3CA7B` | ACCEPTED |
| Studio prompt | Standard enter | 1280x720 | 971,610 | `E9280378B387D6B31226909B6CA69BC319BE479AF3F149EB7B3C528881128203` | ACCEPTED |
| Studio prompt | Standard leave | 1280x720 | 1,044,248 | `43263AD6242D3DD93CE266A206B2BB72B0EA0B07EC52FEEAD3C21FF0152E9E53` | ACCEPTED |
| Studio prompt | Compact enter | 888x500 | 466,021 | `C324DF4D44A2FAF3DEAA06FF71343C4C41205BF964A0228B74E96DEC402A954D` | ACCEPTED |
| Studio prompt | Compact leave | 888x500 | 497,174 | `1275EA74DD45F774100DF8DD6242563EAF566B2587539F6DD1DB28FF4774DE42` | ACCEPTED |
| Job prompt | Standard prompt | 1280x720 | 1,296,751 | `80AB383417CE59C29B62F4664A75CCF8B4DFF18270E589410A94F9A4CA6086F3` | ACCEPTED |
| Job prompt | Compact prompt | 888x500 | 610,232 | `FF569BEBD32049F980E80054990262CEC079471F61089E001A4E8BAA2D16E154` | ACCEPTED |
| Ticket browser | Corrected compact | 888x500 | 128,424 | `7D6337638DB9B3DBC22170E6952ACB9968C236DC1D40E00C48ED8339FCF2BA0B` | ACCEPTED |
| Stadium | Public viewing | 1280x720 | 1,257,308 | `F295185EED73F81B67B60A565AB9DA580F74882F1D7E7F706F1AF2D84212B259` | ACCEPTED |
| Settled receipt | Standard | 1280x720 | 719,763 | `D0018CE68E880A61FE5C8C2EFCAC89B19273C97A8BBFDECD87D5136EE9F35FCF` | ACCEPTED |
| Settled receipt | Compact | 888x500 | 209,522 | `BD9243C1FADF7317A533550E56AD1BBE7CF99D2B4E686F84B568BEFAD6D5A215` | ACCEPTED |
| Clothing feedback | Standard purchase | 1280x720 | 1,095,868 | `270A1FEAC32D321BC5696833EE14E2F069210AB9B13433240B58480D4C7EA4B8` | ACCEPTED |
| Clothing feedback | Standard equip | 1280x720 | 1,317,608 | `BB359FD98F5A91E9A50D27A746EB52776D56AB0F89DE47D94CDF439F5E2ADD4E` | ACCEPTED |
| Clothing feedback | Compact purchase | 888x500 | 505,876 | `865B74CC62604D0641A57DB05B01AE3AB24D799EE023344209DFA0DB084B7740` | ACCEPTED |
| Clothing feedback | Compact equip | 888x500 | 598,684 | `B43B68B97D1B134078286FC77B60244044050935D5FCA6D26195B619A7CF06EA` | ACCEPTED |
| Furniture feedback | Standard purchase | 1280x720 | 1,339,918 | `A729BDD36762680BF02BABC0DFAF2538B8F208C1FB6602E495E211D9825D882F` | ACCEPTED |
| Furniture feedback | Compact purchase | 888x500 | 638,390 | `6D29F6FEDD2775C0B5E06A422E80D7F6E89A8296CF58DFB3EC8E761DB40D61E3` | ACCEPTED |
| Housing feedback | Standard purchase | 1280x720 | 885,699 | `1B7A8F6719C0713706A7312C0C3B42BE0FF16C78CC9F2BC4D526A454DC2C267A` | ACCEPTED |
| Housing feedback | Compact purchase | 888x500 | 412,125 | `B285A397380B1DD39698060E6A1FD16E7FDCECF514898F06D4ED91A09F83A891` | ACCEPTED |
| Athlete story | Public page | 1280x720 | 1,630,539 | `6D7527DC5932BCEFDBDD17EB93CD7B18465922CD47D36FF8115D10CC71B2297A` | ACCEPTED |

## Superseded and rejected evidence

- Ticket browser compact “before” frame: 170,005 bytes, SHA-256 `62BDA333...9359` was retained only as the pre-correction defect baseline. The abbreviated hash is not promoted or used for an evidenced current-state cell.
- Studio leave pre-correction capture was rejected because the prompt/default HUD path was missing. No retained exact hash was present in the audit notes; it supports no matrix cell.
- Clothing preliminary standard frames with prompt overlap and camera motion were explicitly rejected. No retained exact hashes were present in the audit notes; they support no matrix cell.
- Sundale BugItGo and capture-only diagnostics with invalid movement/floor or no PNG were explicitly rejected and support no matrix cell.
- No evidence is transferred from rejected, superseded, differently sized, different-surface, automated-mechanics, or unrelated human-study artifacts.

## Direct gaps and blockers

### ABSENT

- Mouse interaction is absent in the inspected chooser, Studio prompt, Job prompt, stadium skip, clothing, furniture, housing, and athlete-story exact paths.
- Controller interaction is absent in the inspected Studio prompt, Job prompt, stadium skip, clothing, furniture, housing, and athlete-story exact paths. Controller movement support elsewhere does not fill these cells.
- A user-facing remapping interface is absent across the inspected named surface paths.
- The retained prompt/feedback/stadium/chooser phases explicitly contain no human/manual test. This is not evidence that future manual use would fail.
- The three five-second clothing/furniture/housing feedback panels have no direct user skip in their inspected paths.

### UNPROVEN

- Physical keyboard, mouse, and controller use is unproven for all eleven surfaces.
- Exact 888x500 evidence is unproven for chooser, route cues, stadium, and athlete-story pages.
- Exact 1280x720 evidence is unproven for the ticket browser; its prior standard artifact was 1280x800.
- Measured contrast is unproven for all eleven surfaces. Fixed images, luminance descriptions, or approved palettes are not contrast measurements.
- Human recognition, comprehension, hesitation, usability, and accessibility remain unproven except that the athlete-story human cell itself is conservatively unproven because its exact retained citation was not part of this bounded audit.
- Mouse/controller receipt behavior is unproven because no exact receipt-specific citation was retained.
- Text/state redundancy for the chooser is unproven; the accepted visual state alone does not prove human recognition.

No fresh runtime spot-check is requested. Missing proof is truthfully classified `UNPROVEN`; a runtime replay would not establish physical hardware, human comprehension, contrast, or remapping evidence.

## Evidence types

- **Accepted fixed-image evidence:** exact standard and/or compact render at the cited surface and resolution only.
- **Source contract:** current fixed bindings, state text, non-color shape use, or direct absence in the inspected exact path; never physical use.
- **Automated runtime/report evidence:** mechanics and fixed-view artifact custody only; never contiguous first-hour or human evidence.
- **Human/manual evidence:** no exact accepted citation retained for a positive cell in this bounded audit.

## Proportionate regression and invariance

- Brain Admin self-check: **PASS** using pinned Python 3.12.13 at `C:\Users\reali\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` with `-B -m brain_admin.server --check`.
- Historical frozen native regression: 73/73; historical pinned Python regression: 105/105. These are custody references only and were not rerun or converted into accessibility evidence.
- Accepted package: `C:\tmp\OddsWellPhase1L4b\PackageFinal\Windows`, excluding runtime `Saved`: 50 files, 1,051,962,028 bytes, 0 Python files.
- Package wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Packaged game SHA-256: `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A`.
- Packaged UFS SHA-256: `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356`.
- Protected production map SHA-256: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.
- Baseline HEAD at audit start: `a719ca74df207bd9cb1689bbaa2fb0461dbb63a4`; worktree/index were clean before this authorized report draft.
- Pre-audit target processes and TCP/UDP ports 17777/1985/7810: 0.
- No client, source, config, test, map, package, art, save, economy, network, or runtime mutation was authorized or performed by the audit.

## Boundaries

- This inventory does not approve accessibility, usability, beta readiness, or production readiness.
- It does not create an accessibility standard, score, target, remediation backlog, or implementation plan.
- It does not claim keyboard source mappings as physical keyboard evidence, controller mappings as physical controller evidence, labels as human recognition, fixed screenshots as comprehension or contrast proof, or separated automated lanes as a contiguous first-hour session.
- Phase 1K remains incomplete, deferred, and not waived.
- Phase `2/6` closed at commit `91cddb3cf82d56ea2c0426e903560a3a3620c966` with verified Notion closure. The later owner deferral is recorded separately in [[Design/Decisions/DEC-025 First Hour Input and Accessibility Remediation Deferral]].
- No Notion or Cursor task is created by Execution.
