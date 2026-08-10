# Phase 1L.3b Sundale Architectural Language Review Board

Date: 2026-08-10
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW - OWNER ACCEPTANCE AND PRODUCTION PROMOTION PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Blender `4.5.5 LTS` builder produces exactly six low-poly facade samples and six low-poly tower silhouettes, one pair for each accepted district. The board is exterior shape-and-palette evidence only. It preserves the owner-accepted Phase 1L.3a planning baseline and changes no production system.

This is new-art-batch Phase `1/6`. Decision cursor remains `0`; no sample is approved for production use until the owner accepts it.

## Scope authority

- [[Development/Beta Delivery Roadmap]] Phase 1L delivery steps `1`, `2`, and `5`.
- [[Design/Sundale Art Direction and Core Loop]].
- [[Design/Sundale Production Asset Scope]].
- The owner-accepted Phase 1L.3a business-clustered planning baseline recorded in [[Development/Reports/Phase 1L3a Sundale Business Clustered Mega City Replacement Preview]].

## Exact sample contract

| District ID | Facade ID | Facade triangles | Tower ID | Tower triangles |
| --- | --- | ---: | --- | ---: |
| `FINANCIAL_DOWNTOWN` | `FACADE_SAMPLE__FINANCIAL_DOWNTOWN` | `120` | `TOWER_SILHOUETTE__FINANCIAL_DOWNTOWN` | `24` |
| `ARENA_ENTERTAINMENT` | `FACADE_SAMPLE__ARENA_ENTERTAINMENT` | `96` | `TOWER_SILHOUETTE__ARENA_ENTERTAINMENT` | `24` |
| `SHOPPING_RETAIL` | `FACADE_SAMPLE__SHOPPING_RETAIL` | `132` | `TOWER_SILHOUETTE__SHOPPING_RETAIL` | `24` |
| `DINING_NIGHTLIFE` | `FACADE_SAMPLE__DINING_NIGHTLIFE` | `96` | `TOWER_SILHOUETTE__DINING_NIGHTLIFE` | `24` |
| `HOME_DESIGN_FURNITURE` | `FACADE_SAMPLE__HOME_DESIGN_FURNITURE` | `84` | `TOWER_SILHOUETTE__HOME_DESIGN_FURNITURE` | `24` |
| `RESIDENTIAL_NEIGHBORHOOD_SERVICES` | `FACADE_SAMPLE__RESIDENTIAL_NEIGHBORHOOD_SERVICES` | `96` | `TOWER_SILHOUETTE__RESIDENTIAL_NEIGHBORHOOD_SERVICES` | `60` |

Every facade is below the exact `240`-triangle ceiling and every tower is below the exact `96`-triangle ceiling. The exact review-board bounds are `x=-19.01..19.01 m`, `y=-13.01..13.01 m`, and `z=-0.51..18.0 m`.

Materials are limited to the accepted warm limestone `#D8C8A9`, muted terracotta `#A65F47`, sand concrete `#B9A783`, sage green `#6D7F62`, restrained cobalt `#315F79`, burnt orange `#C46D3B`, and charcoal gray `#4D5051` planning palette.

## Artifact evidence root and exact hashes

The repository evidence root is `Oddswell/Art/Reviews/SundaleArchitecturalLanguage`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleArchitecturalLanguage.blend` | `1,115,150` | `AA82D170128AB0180286DB090EA45C1CB6C7F08F063AC22DC3D1D909530E2D17` |
| `build_sundale_architectural_language.py` | `25,275` | `68081C7435CFF01814DCCCDDC1DF8AD2F931989FA3926CFBD8B1338558010DB1` |
| `manifest.json` | `7,003` | `394EC4A1CF78E3BFAF322DB60CFD666461B4070E725B650C79D2154A412DA2F9` |
| `PROVENANCE.md` | `893` | `6CAFA2600FEE838F86BB98C68DA535C0E5F80F72BF4D0C896153B6FED5C18827` |

The Blend is covered by the existing Git LFS rule. Its exact prospective pointer is:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:aa82d170128ab0180286db090ea45c1cb6c7f08f063ac22dc3d1d909530e2d17
size 1115150
```

No `.blend1` backup exists.

## Render evidence

| Accepted review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `renders/Unified_SundaleArchitecturalLanguage.png` | `1920x1080` | `1,955,863` | `FB9548173BF74E127171002038BB8A65445D795FE44743163A121A92166DBDDC` |
| `renders/Closeup_FinancialDowntown.png` | `1280x720` | `628,731` | `DBDE89E37CCDDD1999FFC0462937F97E0C82C199F0FE09845C9C49A39EB96FE3` |
| `renders/Closeup_ArenaEntertainment.png` | `1280x720` | `645,302` | `64BFB8EF5C5FDEF627D26B09519B9637A968A0E9FAABF091FA76A3FDF04CA090` |
| `renders/Closeup_ShoppingRetail.png` | `1280x720` | `629,007` | `90AACB1E58E5D98EC9BE13C8291C7E1CC21DE97FB6615F6B4EBF3340EA424B4B` |
| `renders/Closeup_DiningNightlife.png` | `1280x720` | `572,866` | `B57F14B778369B5B3C821C5C467BDD283A7565FD4B00B8AF9F3B05BD096D237F` |
| `renders/Closeup_HomeDesignFurniture.png` | `1280x720` | `572,088` | `09DE80D00832981D0BCA8DEC73BD0B4FF01087D630141DD68538E02EEB8D0DD2` |
| `renders/Closeup_ResidentialNeighborhoodServices.png` | `1280x720` | `571,593` | `444FA6AC1F45DE0D327E06FDCF60A7400D2B52398D7E03F502B798DA2DF6D3F8` |

All seven refreshed PNGs were reopened at original resolution after the final build, and every file hash matches `manifest.json`. The bounded correction places each closeup camera `28 m` from its district center at `z=7.5 m`, targets the same `z=7.5 m` centerline, and uses a `14 mm` closeup lens. Each of the six `1280x720` closeups shows the complete district facade and complete target tower silhouette, including the crown, with visible clearance on every frame edge. The unified view remains the clean divided review board. The saved-Blend validators independently confirm the exact geometry contract and bounds.

### Superseded pre-evidence hashes

The final retained-evidence rerun replaces all prior generated identities. The following initial pre-evidence hashes are noncanonical and superseded; they have no retained Phase 1L.3b log root and are not the staged artifact identities:

| Superseded output | Pre-evidence SHA-256 |
| --- | --- |
| `SundaleArchitecturalLanguage.blend` | `42AEC1D07E2E4890F2DDB5C1F56B4C87D8C9DBAEF2C75BB8846188DB80525A2D` |
| `manifest.json` | `B2F4A611E45F509635B3C3C708963117C61CCE86768151B10D3AC7746A90A75E` |
| `renders/Unified_SundaleArchitecturalLanguage.png` | `1123B423C6487CF44F73E8C310FDBC34804634DEA761BF328AFFE0327A07511E` |
| `renders/Closeup_FinancialDowntown.png` | `5178168624385D4B2CE4191E417091B9BAA76A5BDAB12EAA84479D7C7E184BA0` |
| `renders/Closeup_ArenaEntertainment.png` | `B7FBD58F8E38C123771FCAEEFB2FE673FBA548D7EE70205EA56BB98FC7369D9B` |
| `renders/Closeup_ShoppingRetail.png` | `C3A8CB1F5ADF267C7180887C54E4A0BF9922EB0A1BECFB47A09242E67B1C26B9` |
| `renders/Closeup_DiningNightlife.png` | `21010DDC7AEC09A6268ADDDD84CC1CF793EB1A39F2D134DF5A4B11B4BBDF05DF` |
| `renders/Closeup_HomeDesignFurniture.png` | `76A2C32270078E83F0ED09C5ECE72E25CB50465F32287F0E0078273918B2A67E` |
| `renders/Closeup_ResidentialNeighborhoodServices.png` | `0B5FC9681E0BAFBBF6BE9D2D6E3F6DD94778BC67A7CF27F7B710E55B644300F0` |

A later retained-evidence candidate was also rejected during original-resolution review because closeup crowns touched or crossed the frame. Its evidence logs were overwritten by the final camera/framing repair, and every identity below is noncanonical and superseded:

| Rejected framing output | Rejected SHA-256 |
| --- | --- |
| `SundaleArchitecturalLanguage.blend` | `C842684D3E413FFD117CC8BE4A748831041A99ABC0FC1CF0443A6A9667D5A77D` |
| `manifest.json` | `C6F53572D08B8A5ED66566DEE6624D7A74B52E2D5A0403FBC6839D78E885B844` |
| `renders/Unified_SundaleArchitecturalLanguage.png` | `694D09C4AA91DE28628281D0E29AD960E3C6E2FA60CC0DDAF29120831ADB5873` |
| `renders/Closeup_FinancialDowntown.png` | `775DBD66CFAB11A736665310F72B77454AAFBCBF83DAE0A79054E037718E15B1` |
| `renders/Closeup_ArenaEntertainment.png` | `666569AE29488589384317AA1C4F60BEFE868100E48EE7B434A1E7A722FAB680` |
| `renders/Closeup_ShoppingRetail.png` | `D4017A3B1F91C38F7B97CEA3C65CC0A52BFE18BC9B7D9CA2EC7D8B08572C79C2` |
| `renders/Closeup_DiningNightlife.png` | `41806B78A498F6CBEB971E8D001925EEDA559287246C5F67BB96BCCA80E44DE0` |
| `renders/Closeup_HomeDesignFurniture.png` | `7B092F3CDD81BC351F6D31049BFA822708A5AD8B4279E99108F262C0DC7A3448` |
| `renders/Closeup_ResidentialNeighborhoodServices.png` | `2444AEB9FC45FF5181827D89119AED4EBCB54B4BEF54BEA9A275B7AEE3A1EA84` |

## Headless build, reopen, and focused evidence

The final headless build, saved-Blend reopen, and focused pass were executed from repository root `C:\Users\reali\Documents\SaaS\Oddswell`. Their machine-local evidence root is `C:\tmp\OddsWellPhase1L3b\Evidence`. Reopen validated the saved Blend SHA-256 `AA82D170128AB0180286DB090EA45C1CB6C7F08F063AC22DC3D1D909530E2D17`; focused validation used builder SHA-256 `68081C7435CFF01814DCCCDDC1DF8AD2F931989FA3926CFBD8B1338558010DB1` and manifest SHA-256 `394EC4A1CF78E3BFAF322DB60CFD666461B4070E725B650C79D2154A412DA2F9` and rechecked all seven render hashes. Only the six explicitly listed paths below are canonical retained evidence; legacy-named candidate logs in the same machine-local root are noncanonical and excluded.

| Fresh phase-local evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `C:\tmp\OddsWellPhase1L3b\Evidence\BlenderBuild.log` | `9,096` | `3CA76007525BE61C75F64E4925EC00131B669D310E7A11DBBF398D26FD35AFF5` |
| `C:\tmp\OddsWellPhase1L3b\Evidence\BlenderBuild.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `C:\tmp\OddsWellPhase1L3b\Evidence\BlenderReopenValidate.log` | `1,300` | `B971FA7BBC2FAF88709CD1952173F1F18518B081933B3F51F70376C80E20141B` |
| `C:\tmp\OddsWellPhase1L3b\Evidence\BlenderReopenValidate.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `C:\tmp\OddsWellPhase1L3b\Evidence\BlenderFocusedValidate.log` | `1,302` | `69A615CE4F3169E0D8899EF5E4C62EA23EDA8FFAD361AC924BD37D6EFA93EFBC` |
| `C:\tmp\OddsWellPhase1L3b\Evidence\BlenderFocusedValidate.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

```text
ODDSWELL_SUNDALE_ARCHITECTURAL_LANGUAGE_BUILD|result=PASS|artifacts=10|manual_input=false
ODDSWELL_SUNDALE_ARCHITECTURAL_LANGUAGE_VALIDATION|result=PASS|districts=6|facades=6|towers=6|views=1_unified+6_closeup|engine=eevee|palette=7_accepted|facade_tri_ceiling=240|tower_tri_ceiling=96|external_refs=0|interiors=0|gameplay=0|production_counts_changed=false|route_changed=false|business_behavior_changed=false
ODDSWELL_SUNDALE_ARCHITECTURAL_LANGUAGE_REOPEN|result=PASS|manifest=true|render_hashes=7|manual_input=false
ODDSWELL_SUNDALE_ARCHITECTURAL_LANGUAGE_FOCUSED|result=PASS|manifest=true|render_hashes=7|manual_input=false
```

The builder and validators lock the exact sample IDs and roles, one pair per district, bounds, triangle ceilings, seven accepted materials, one unified plus six district camera/render identities and hashes, and zero external libraries, images, textures, interiors, brands, catalogs, frameworks, armatures, volumes, or gameplay additions.

## Concrete reused production-evidence ledger

No no-op Unreal build, production test, or package rerun was performed because this phase changes no production client, runtime, map, test, or config path. The proportional regression evidence is retained under `C:\tmp\OddsWellPhase1L3aFinal`; the canonical package evidence root is `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows`.

| Gate | Retained evidence | Result |
| --- | --- | --- |
| Full native Unreal automation | `C:\tmp\OddsWellPhase1L3aFinal\FullNativeFinal.log`, `339,253` bytes, SHA-256 `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` | REUSED PASS `72/72`, exit `0`, failures `0` |
| Python phase0a | `Python_phase0a.log`, `882` bytes, SHA-256 `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` | REUSED PASS `9/9` |
| Python phase0b | `Python_phase0b.log`, `854` bytes, SHA-256 `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` | REUSED PASS `2/2` |
| Python phase0c | `Python_phase0c.log`, `880` bytes, SHA-256 `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` | REUSED PASS `8/8` |
| Python phase0d | `Python_phase0d.log`, `1,010` bytes, SHA-256 `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` | REUSED PASS `46/46` |
| Python phase1h | `Python_phase1h.log`, `1,008` bytes, SHA-256 `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` | REUSED PASS `40/40` |
| Repository-pinned Python `3.12.13` aggregate | the five retained logs immediately above | REUSED PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | `C:\tmp\OddsWellPhase1L3aFinal\BrainAdmin.log`, `43` bytes, SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` | REUSED PASS |
| Production client diff | current Phase 1L.3b scope contains `0` `client/` paths | PASS |
| `client/OddsWell/Content/Maps/SundaleGraybox.umap` | direct file hash | PASS SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |

The five Python stderr records are also retained under `C:\tmp\OddsWellPhase1L3aFinal`: `Python_phase0a.err.log` SHA-256 `8BAD5FD54888B5DE64EEA5A7AAC90442A1636A4057C19BCB40D629445DF8C843`, `Python_phase0b.err.log` `DC1CF009407407F93A9110B028BBDC921FFAAB99ECFE15E418EEE374BEB23480`, `Python_phase0c.err.log` `E96DD1C702697D37E7EC61C03020A1EB5271EB3D2A6993AF1696323724954C07`, `Python_phase0d.err.log` `1AD2A774EB9A6AA899A42EB11C1EEA9A63455121B5323FC53FC7929E7CFDC134`, and `Python_phase1h.err.log` `2143E8C94EDEF5D13A268160B1FBAADAFC2BF5A9C5EDF5667740A0409DC319E2`.

The retained canonical Phase 1L.2 package is audited before postlaunch `Saved` output and remains exact:

- files: `50`;
- bytes: `1,050,423,644`;
- Python artifacts: `0`;
- wrapper `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows\OddsWell.exe` SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`;
- game executable `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows\OddsWell\Binaries\Win64\OddsWell.exe` SHA-256: `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`;
- UFS container `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows\OddsWell\Content\Paks\OddsWell-Windows.ucas` SHA-256: `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Preserved boundary

This work does not import or replace Unreal geometry, revise the accepted Phase 1L.3a massing composition, change the `2400x1800 m` planning boundary, six districts, `144` masses, sixty towers, production `800 m` route, or any business behavior. It makes no final-art, placement, collision, accessibility, performance, interior, branding, catalog, service, or beta-readiness claim.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

After commit and Notion closure, return to the Scope Director for exactly one new-art-batch Phase `2/6` independent review subphase. The owner may accept, request one bounded revision, or reject this architectural-language board, but that owner gate applies only to promoting or expanding the Phase 1L.3b samples into a production family; it does not block later independent review subphases. This does not authorize roadmap Phase 2.
