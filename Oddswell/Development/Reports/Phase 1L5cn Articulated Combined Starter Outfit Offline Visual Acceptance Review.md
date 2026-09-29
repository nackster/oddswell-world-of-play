---
tags:
  - development
  - beta
  - character
  - review
status: complete-review-rejected-visual-correction-required
date: 2026-09-29
---

# Phase 1L.5cn Articulated Combined Starter-Outfit Offline Visual Acceptance Review

## Outcome

Phase 1L.5cn is complete as an evidence-only review with verdict `REJECTED_VISUAL_CORRECTION_REQUIRED`. The exact Phase 1L.5cm custody and mechanical gates pass, but the exact retained views fail two of the unchanged seven qualitative criteria: neckline/shoulders/sleeves/hem and no rejected silhouettes. The verdict is derived from the criterion statuses rather than fixed in advance; numeric gates do not override qualitative failures.

This rejection stops export/import preparation. It is not an export, import, runtime replacement, final-art approval, Phase 1L exit, beta-readiness, Version 1 readiness or production-readiness determination.

## Exact custody

- Source Blend: `13,907,177` bytes, SHA-256 `10315DEC1E2F1EAB3F3D7DDA6828AB5B9867957B9D108C5A2F462201D3E059FC`.
- Phase 1L.5cm semantic identity: `6E219986ED018BFF27BB61AD308346C33217795B5C883893806E661D589579B0`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Articulated top: `9ED01AAA3F060F237D2CCADCD5ED7E15F65E864F013DC0BCB51266A31A34FA58`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Frame-ledger identity: `84589A1CAC04FFF8E0176E794C8430F7806FD0B3E0913457373D6DDEB465F261`.
- Topology identity: `64BD03BA4EAB3A529B303860427453B47C2807C8AF25F520329CC2E5078C8FE3`.
- Opening identity: `C90E1A6D9A2F1D9A259281D275EC1922250596BBFE862DC65AC5A8A5EC4D0D95`.
- Exact five-view identity: `912F1D0FD8FC980AEC8972B70F13AAAA76A3F4FC9D2086A079A5E298562C99F0`.

Geometry, weights, topology, materials, action, skeleton, export, Unreal/client files, package inputs and runtime changes are all `0`.

## Unchanged seven-criterion review

| Criterion | Result | Evidence |
|---|---|---|
| Separation | PASS | The exact retained `21`-frame ledger reports body/top, body/bottom and top/bottom evaluated intersections `0`. |
| Neckline / shoulders / sleeves / hem | FAIL | The one-component/four-opening contract passes and the articulated shoulder line and hem remain stable, but both outer sleeves still terminate as abrupt rectangular blocks rather than continuous rounded armhole caps. |
| Waistband / rise / crotch / legs | PASS | Exact accepted connected shorts retain three openings, zero other non-manifold edges and two readable legs. |
| Proportions | PASS | Neutral top width is `0.944817424 m` versus body width `0.675352 m`, ratio `1.398999964`, within the unchanged `1.4` ceiling. This numeric pass does not override qualitative failures. |
| No rejected silhouettes | FAIL | Width ratio `1.398999964` and waist inset `0.132244272` pass their numeric gates, but neutral and opposing-extreme views retain detached-looking sleeve blocks and an armor-like outer top silhouette. |
| No exposure or collision | PASS | All five exact views retain body coverage without visible interpenetration; the ledger also reports zero evaluated intersections. |
| Stable opposing extremes | PASS | Frames `6` and `16` keep the corrected shoulder line and lower hem near the neutral silhouette; zero root/armature translation and frame-21/frame-1 equality remain exact. |

The one smallest next correction is only the top outer sleeve/armhole block geometry within `|X| >= 0.389245 m` and `1.20 m <= Z <= 1.40 m`, reshaped into a continuous rounded cap while preserving the Phase 1L.5cm articulation weights, central torso, waist and neckline boundaries, four-opening contract and all non-target assets.

## Deterministic evidence

- Review identity: `31F420AB306F577D947D712888A03F5FB13A89C622D882044F06C338F83387C5`.
- Deterministic board: `1,045,713` bytes, SHA-256 `8B534681A614AD6FF1D7B3756DD67CEFA35772D92B3E33BC32B215C39CF94F61`.
- Exact retained views: front `69E2CD778C351B8DE4ED5F5BFD72559995C4AC9D449982C8F672028D04201EBD`, rear `1DC0B9AAB7995D4D0ACE7BF738C6C2AC340FE9C3ABACEF61CFA1F64CBDF470D3`, profile `A7A95784F9E24D2F3E319089A5AC2FB97A734A2D79272311A8073FB05394FEA6`, frame-6 extreme `B8BA8BEAF7C99C8230CA2305A0FBF8CBC83466DE75F5E1943E4B51B3DFAC1BDB`, frame-16 extreme `829F338AC0D2548A0705C51EC70A0E8CCE867FCEEC621E478D8D47783FF4F4C8`.

## Verification

- Deterministic build and independent validation: PASS; rejection identity `31F4...7C5` and board `8B53...4F61` reproduced.
- Full frozen native suite: PASS, `75/75`, with `0` non-success markers; retained log SHA-256 `3D64CF2BE70B973C863D22569FBF8715CE59FF1FA36E8F8978D9FF3754BF40C8`.
- Isolated Python regression: PASS, `105/105` (`9 + 2 + 8 + 46 + 40`) in `167.255 s` of reported test time.
- Brain Admin self-check: PASS; exact `43`-byte stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Windows verification: PASS. Locomotion and character-motion markers passed; Studio and interaction-prompt-presentation markers passed; camera-orbit passed; shared-city server/client, skeletal appearance and skeletal motion markers passed. All five processes emitted exit-status `0`, and UDP `17777` was released. Log hashes: locomotion `F550BCE4C571A4F7B83F11191419469B4E00C52DA43FF83FE71C6EAA284BEB66`, Studio `ADBEBCCFA175D40CE1391AA1AD4B88C416ED76B0FF8EE03C84DC6F7FB8D14D12`, camera `4FD9B66B714E8C7ED0A552100725602C534F45CD0D40E5E71BB67FE8C71DDD6C`, server `917C0706C0462288B8E518B3A4FC4D21624BAA39FA1B49F0072BC477A83DDA7D`, client `F28F0DA19297C0C5CD1F4A3162144C9ABB0AC783C39B594249130888D9B248EA`.
- Retained package audit: `50` files, `1,038,710,362` bytes, `0` Python files. Final process audit found `0` OddsWell, Unreal Editor or Blender processes.

## Boundary and next gate

Export/import preparation is not eligible. The only bounded next correction is the measured top-only outer sleeve/armhole rounded-cap correction above. This review itself changes no asset or runtime input. Fabric, production UVs, LODs, final materials, runtime replacement, performance, hands-on usability, Phase 1L exit and beta readiness remain separate unproven gates.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cn articulated combined starter-outfit offline visual acceptance review]], [[Development/Reports/Phase 1L5cm Shoulder Cap Sleeve Hem Articulation Correction Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
