---
tags:
  - development
  - beta
  - phase-1l
  - blender
  - unreal
  - art-pipeline
status: complete-bounded-pass
date: 2026-08-08
---

# Phase 1L.2 - Sundale Job Canopy Blender-to-Unreal Pilot

**Status:** COMPLETE - BOUNDED NONCANONICAL BLENDER-TO-UNREAL PILOT
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`
**Authority:** [[Development/Beta Delivery Roadmap|Phase 1L delivery steps 1, 2, and 5]] and [[Design/Beta Game Bible|Art, music, storytelling and first-hour Job journey]].

## Outcome

One original Blender `4.5.5 LTS` source now proves the smallest complete asset path from local authoring through deterministic validation/export, Unreal import, cook, package, and runtime load. The source contains exactly two one-meter beveled meshes: `SM_JobCanopy_Pier`, reused for the existing left/right Job piers, and `SM_JobCanopy_Header`, used once for the existing header.

Ponytail kept the runtime change inside the existing Sundale presentation helper. Only `JobFrontagePierLeft`, `JobFrontagePierRight`, and `JobFrontageHeader` map to the two pilot assets. `JobFrontageLanding` and `JobFrontageApproach` retain the Engine cube. No asset framework, catalog, map edit, external dependency, material system, fallback path, sign, text, brand, final architecture, or final art was added.

## Original source, provenance, and LFS

The phase-local script `Oddswell/Art/Pilots/SundaleJobCanopy/build_job_canopy.py` creates the two objects from original beveled cubes, applies transforms, generates one UV layer, assigns one material slot, saves one Blend, exports exactly two FBX files, and writes `manifest.json`. `PROVENANCE.md` records that no external model, texture, font, image, paid service, or third-party source was used.

Headless Blender validation passed with metric units, unit scale `1.0`, zero location/rotation, unit scale transforms, normalized `[1.0, 1.0, 1.0] m` source bounds, one UV channel, one material slot, `24` vertices and `44` triangles per object, and `88/512` combined triangles.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleJobCanopy.blend` | `400,736` | `D836A407054FB8C338D68E354283ACCBC2AC742EC78A64CCBB3BE7FF100BC9F6` |
| `SM_JobCanopy_Pier.fbx` | `16,156` | `F80F8ADA046BF6198639A6BC3B20136776D5BDA36D91E546CE3FD20320A47221` |
| `SM_JobCanopy_Header.fbx` | `16,156` | `8C2C42F0605BBAD69D6D33D07973FF1A4FF6643688823B2BB377E213A59C7D94` |
| `build_job_canopy.py` | `4,728` | `301EEDE1B3578CAFD186F89E5D2D76E4B4A632C570FD6600E61DFC7851AC1E96` |
| `manifest.json` | `1,199` | `E37665A4BABE11BF9CC8591CF95DA6B48FB6058C42295B973E1B7CD32A49FCD5` |
| `PROVENANCE.md` | `783` | `A92D04201DA53CA7885B94C34D0A2CA2D9315A506E4C3D97A807E87A915DCE7F` |

Existing `.gitattributes` rules report `filter=lfs`, `diff=lfs`, and `merge=lfs` for the Blend, both FBX files, and both UAssets. `git lfs pointer --file` produced valid pointers whose OIDs and sizes match the five binary files. No Git LFS rule change or install was needed.

## Unreal import and runtime contract

The accepted automated import created exactly:

- `/Game/Art/Pilots/SundaleJobCanopy/SM_JobCanopy_Pier` - `130,459` bytes, SHA-256 `B79BAB34DE322881EF64243C99633976EEB1BF4262BEE4286CFF0DBDFA6A4782`
- `/Game/Art/Pilots/SundaleJobCanopy/SM_JobCanopy_Header` - `130,501` bytes, SHA-256 `1E9243207EB624CEF9450142E97565BEEB39E8ED87F6927D62FFFFEE7678A3D4`

Focused automation loads those exact objects, proves no required pilot part can fall back to the Engine cube, confirms `100 cm` bounds, one material slot, `44 + 44` triangles, and the `88/512` budget. Editor-only checks retain the one-UV-channel import contract.

The five pre-existing Job IDs, four roles, transforms, scales, and colors are unchanged. Runtime actors remain transient, local-only, non-replicated, collision-disabled, overlap-disabled, physics-disabled, and absent on dedicated servers. The final packaged marker reports `parts=5`, `roles=4`, `pilot_mesh_parts=3`, `pilot_assets=2`, `cube_parts=2`, and `cube_fallback=false`.

Because runtime asset paths are loaded by string rather than a hard asset reference, the initial successful cook did not discover the two UAssets. The smallest correction adds exactly one `/Game/Art/Pilots/SundaleJobCanopy` `DirectoriesToAlwaysCook` entry. The final UFS container grew by `14,400` bytes and the packaged runtime loaded both assets without fallback. No broader cook directory or Asset Manager framework was added.

## Frozen gameplay and authority boundary

The exact Job anchor `(9500, 0)`, `350 cm` radius, exact prompt `Press E to complete a shift (100 Odds Bucks once every 24 hours)`, E/latch/server path, `100` payout, rolling `86,400`-second cooldown, result panels, immutable ledger, save/schema/authority/time boundary, city route, brains/simulator, wagers/settlement, inventory, stores, housing, networking, and every Phase 1L.1a-u layer remain unchanged.

The authored Sundale map, Studio-home save, housing catalog, and Odds Bucks ledger sources remain byte-identical to their protected baselines. No gameplay actor coordinate, collision surface, route point, interaction threshold, prompt, material palette, economy value, save shape, replication rule, or authority rule changed.

## Verification

| Check | Result |
| --- | --- |
| Headless Blender build/validate/export | PASS; Blender `4.5.5 LTS`, exact 2 objects/2 FBX, `88` triangles |
| Unreal automated import | PASS; exact 2 UAssets, zero accepted errors/warnings |
| UE 5.8 editor Development build | PASS; `4` actions / `11.06s` |
| Focused `OddsWell.Character.SundaleJobCanopyBlenderPilot` | PASS `1/1` |
| Full native OddsWell automation | PASS `72/72`; zero failed tests |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| UE 5.8 game Development build | PASS; `3` actions / `17.95s` |
| Final BuildCookRun `Bootstrap+SundaleGraybox` | PASS; `27.32s` |
| Final package audit | `50` files / `1,050,423,644` bytes / `0` Python files |
| Standard and compact Job prompt/payout/cooldown | PASS |
| Standard and compact cold restore/cleanup | PASS |
| Automated Sundale run route | PASS `11/11`; clean auto-exit |

Final package hashes:

- wrapper: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- game executable: `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`
- UFS container: `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`

## Packaged Job and route evidence

Fresh standard `1280x720` and compact `888x500` processes each loaded the two pilot assets and used them for three exact mesh parts with no cube fallback. Both retained prompt absence outside and the complete exact prompt inside, credited `+100` exactly once through the unchanged E/latch/server path, produced one ledger entry/balance `100`, and blocked the immediate retry. Separate standard and compact cold processes restored one entry/balance `100`, retained the cooldown, and cleaned the QA save.

Accepted final logs contain zero fatal, assertion, ensure, unhandled-exception, or OddsWell QA failure markers:

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| Standard fresh | `97,661` | `5FDC4DC633E17F77BFF1E49738C7648D354D10A0FA72C88E326D912E05B9871F` |
| Standard cold | `95,371` | `998F3CF3D2BA4E4B998431639D0861FE4BD07EF02DAF6DB7C2B1FE6DFF42087C` |
| Compact fresh | `98,331` | `9CB48E490CD3C84A8A549B67F751C2AD472229968D677654B4758905B78476F7` |
| Compact cold | `95,873` | `FF781B9F030F273798536369D36BF738F8F917EEDDAA2F3EA060ABDB295A3C02` |
| Canonical run route | `97,033` | `3DB63ACF93D9E2DE0139802D7A8BA94FA9A77D5022D34DB72AC22FE66DA501F2` |

The unchanged route ran `80,000 cm`, reached `11/11` points in `154.456s`, traveled `79,783.7 cm`, returned home, remained landed with blocking floor collision, held `1.0 cm` vertical range, and exited normally under `-LocomotionAutoExit`. No player, keyboard, mouse, or manual input drove the route.

## Visual and performance evidence

Original-resolution inspection shows the pilot canopy in the same close Job prompt view at standard `1280x720` and compact `888x500`. The exact prompt and both existing result lines are complete without observed panel/text clipping or prompt/result overlap in the six accepted frames.

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| Standard prompt | `1,290,193` | `58F6FDCACDF0CCC3BFD51EEAA27F266A57D658C6073B26A045EC69D6B8C68225` |
| Compact prompt | `611,427` | `DEA3739CDDE1B2930E0DE6863D9EDD52BE0A09F0F204AFD69144B780E998AAAC` |
| Standard success | `1,239,407` | `670AF65FCEE1BB9CEC38941EA02CB79B32205B8AB497631E53F02249A276ABD0` |
| Compact success | `566,313` | `880864E02677AC3D5F2E42C3A63445B1514684D5D6EE573CE729C32B30FE6A9C` |
| Standard cooldown | `430,347` | `CD259159045441999AE4CC56FC6E3DA0D7CE16520C96F15A4AB2B4A0855F4208` |
| Compact cooldown | `195,436` | `665AA4F2C2EA1A1983E141F938DBA6B5BC6D94C5ADDED27870614FA83529F89B` |

Same-view prompt comparisons against the Phase 1L.1u images are deliberately close because the approved transforms, scales, colors, and one-meter normalized source bounds are frozen. After converting both inputs to RGB and excluding their invariant alpha channels, standard PSNR is `47.554 dB` with RGB SSIM `0.993437`; compact PSNR is `47.965 dB` with RGB SSIM `0.991449`. The visible delta is limited to the pilot meshes' bevel/normal detail plus normal capture noise. This is pipeline evidence, not a claim of a substantial visual upgrade.

Largest active OddsWell-process sampling at roughly `500ms` intervals:

| Process | Samples | Working set avg / peak MiB | Private avg / peak MiB |
| --- | ---: | ---: | ---: |
| Standard, all | `16` | `1172.3 / 1723.4` | `2437.3 / 3746.0` |
| Standard, warm after `2.5s` | `11` | `1502.3 / 1723.4` | `3333.0 / 3746.0` |
| Compact, all | `14` | `1283.4 / 1751.7` | `2589.7 / 3564.1` |
| Compact, warm after `2.5s` | `10` | `1467.7 / 1751.7` | `3111.6 / 3564.1` |

These are short descriptive Development-package samples, not minimum-PC evidence.

## Rejected diagnostics

- The first Unreal import invocation supplied only group-level destinations. It wrote the exact assets but returned commandlet exit `1` on the empty global destination check; it is rejected. The accepted retry supplied the same exact source/destination globally and per group and exited `0`.
- The first game link exposed editor-only `GetNumUVChannels` use in an EditorContext test. It is rejected. The final source keeps that assertion under `WITH_EDITOR`; editor validation still proves one UV channel, and the final editor/game builds pass.
- The first successful cook omitted the string-loaded UAssets. It is rejected. The exact one-directory cook entry produced the accepted final package and runtime load proof.
- An initial walk-mode route omitted the established run/auto-exit switches. It reached `11/11` and emitted PASS but required a bounded stop after the marker; it is diagnostic only. The accepted replacement used run mode plus auto-exit and exited normally.

## Protected boundaries

- Sundale map: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`
- Studio home save cpp: `2943D697E1E630BA8D76F71A9F0E0B2976F15013C633BF61511F5E8939371B3C`
- Studio home save header: `3E7B067C82D4B0C65EBC961ED2C55DB59C91FD6AAA22A0BC809715EAD23017B9`
- housing catalog cpp: `8629D23577E891555FB711F9E472CBF9E4D6A4F1171E055F950E0692D4FA90AF`
- housing catalog header: `BAF8775550414305F900AF2A4CA2F0F68A0B2935AC64A22FF926E0BCB4CD72EA`
- Odds Bucks ledger cpp: `4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7`
- Odds Bucks ledger header: `A98DEC2027A403B7AC2A66F612A84A611E20710353E3A7E8399467B98B897FE9`

## Truth boundary and phase stop

The fixed close views show the retained Job frontage layout, complete prompt/result text, and the imported pilot meshes from one angle. The cooldown views retain the pre-existing bright graybox horizon and dark lower field. The frames do not prove a substantial visual improvement, every angle, normal player approach, text/color readability, comprehension, accessibility, subjective usability, final architecture/materials/lighting/branding, minimum-PC performance, or beta readiness.

The Blend, FBX files, UAssets, script, manifest, and provenance are noncanonical pilot artifacts. No manual player input or owner testing was used. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. Stop after Coordinator, local commit, and Notion closure; return to the Scope Director before expanding the asset catalog.
