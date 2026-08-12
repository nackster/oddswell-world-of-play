# Phase 1L.4b - One-Candidate Starter-Studio Unreal In-Place Proof

Date: 2026-08-11
Branch: `agent/phase-0d`
Status: **PRE-STAGE READY - IMPLEMENTATION, EVIDENCE, DOCUMENTATION, AND TARGETED AUDIT PASS**
Cost: `$0.00`

## Scope authority

- [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Beta Delivery Roadmap Phase 1L]]
- [[Design/Beta Game Bible#2. Enter the first city|Beta Game Bible first-city journey]]
- [[Design/Beta Game Bible#3. Discover the starter home|Beta Game Bible starter-home journey]]
- [[Design/Beta Game Bible#Bounded Sundale residential-facade production candidate|Beta Game Bible bounded production candidate]]
- [[Design/Sundale Production Asset Scope#First bounded facade production candidate|Sundale Production Asset Scope first bounded facade candidate]]
- [[Design/Sundale Production Asset Scope#Lightweight review sequence|Sundale Production Asset Scope Unreal in-place proof]]

## Outcome first

The exact Phase 1L.4a candidate `SM_Sundale_ResidentialFacade_A` now has one bounded Unreal in-place proof at the existing Starter Studio presentation seam. The proof imports and cooks only that mesh and its already-contracted asset-local vertex-color material. It replaces only the existing transient `StudioFacade` Engine-cube presentation slot; the other thirty presentation parts remain unchanged.

The in-place candidate uses natural scale `1.0`, location `(0,-156,0) cm`, and rotation `(pitch=0,yaw=180,roll=0)`. It retains exact imported bounds `520 x 410 x 500 cm`, `96` triangles, one UV channel, one material slot, and the four approved vertex colors: warm limestone `#D8C8A9`, muted terracotta `#A65F47`, sand concrete `#B9A783`, and charcoal gray `#4D5051`.

The actor remains transient, local-only, non-replicated, non-colliding, non-overlapping, non-physical, and absent on dedicated servers. Runtime evidence reports the exact candidate identity and transform with `cube_fallback=false`. No second facade, tower, reusable kit, material family, texture, collision body, LOD expansion, authored-map edit, route change, gameplay change, or final-art claim was introduced.

## Exact implementation set

The bounded implementation is limited to:

1. `client/OddsWell/Content/Art/Production/SundaleArchitecture/ResidentialNeighborhoodServices/SM_Sundale_ResidentialFacade_A.uasset`
2. `client/OddsWell/Content/Art/Production/SundaleArchitecture/ResidentialNeighborhoodServices/M_Sundale_ResidentialFacade_VertexColor.uasset`
3. `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp`
4. `client/OddsWell/Config/DefaultGame.ini`

The existing packaging configuration adds only `/Game/Art/Production/SundaleArchitecture/ResidentialNeighborhoodServices` to the cook because the runtime load is string-based. Existing global `*.uasset` Git LFS coverage applies; no `.gitattributes` change is required.

The Phase 1L.4a Blender, FBX, contact-sheet, manifest, provenance, and builder artifacts are unchanged. The source FBX remains `17,068` bytes with SHA-256 `A86658B3D110D85E51DDA411B4D350FB4F362DFDC411B31BDB5671847BF8E238`.

## Verified evidence ledger

Canonical evidence root: `C:\tmp\OddsWellPhase1L4b\Evidence`

The following ledger records the accepted artifacts directly. Every SHA-256 value is the complete 64-hex digest; no abbreviated checksum is used. There is no separate external-manifest completion claim. The combined Python invocation that timed out is rejected; the five individually accepted suite runs below are the canonical `105/105` evidence.

| Artifact | Bytes | SHA-256 | Accepted result |
| --- | ---: | --- | --- |
| `ImportFinal1` | `231,596` | `66E4A2EFB26CEC51F3EA9A10062782DD4F6ECA053E23822E9657C7DBDD4EA31D` | Initial exact FBX import passed |
| `ImportFinal2` | `231,004` | `D00A3B4C83CC123AE60C0EA850A085132ACBB5F812A25566BB255108669CA8BD` | Clean reimport passed with the same semantic asset contract |
| `FocusedFinal` | `266,179` | `DCE60F6162AF35BCEF39A506AD91F6B74E723BC9DA60669612A13CD182B40B6E` | `OddsWell.Character.SundaleResidentialFacadeInPlaceProof` `1/1` |
| `FullNative` | `346,661` | `FAE36760EEA59ECF99FE8DFBFF610990E5E909DF155F26C3DF624E4388735217` | Native automation `73/73` |
| `EditorBuildFinal` | `3,488` | `AF2C76DCA74FD243258935236715CE8DE875FF5277CE9FAA01E7EA4AF6C02F30` | Editor build passed |
| `GameBuildFinal` | `1,880` | `58298B82EEB3565E1DB6FD3C279A7757801BD172FDE31AE0426399FFE3316AA3` | Development game build passed |
| `BCR` | `148,594` | `EECCD3E6CD17CCD34165ED8A30C427EDF3F1322615C37A85EDB85D97673C05E9` | Fresh Bootstrap plus Sundale BuildCookRun passed |
| Python `phase0a` stderr | `3,448` | `39AA742EB575FFCB4607511E3206749930BCDA02CA0B34FA36AE395305B3EEF8` | `9/9` |
| Python `phase0b` stderr | `1,368` | `52AB03C08F6D7EC54E402050D4ED4EAB9BF6E36DC4FE38333F31DCA55F32741C` | `2/2` |
| Python `phase0c` stderr | `3,366` | `603D0D3BEF23332EBA0205B3E39F03061D3C90EE5B3362E28672DF5F4AD0A56F` | `8/8` |
| Python `phase0d` stderr | `15,048` | `C95C676ACBD7F97D20FA51FAF2009BA98D91EBE145FB1E96AAA019C5E70C31F3` | `46/46` |
| Python `phase1h` stderr | `15,288` | `14BE6006FFB2375B40E0B36128C8D14725CD4C5D097DFB549B2DAC0B58EB5B9F` | `40/40` |
| Python stdout, each accepted suite | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | Empty stdout; total `105/105` |
| Brain Admin | `88` | `259EF12021009C4EEDFC9873BBE5C135CA8BE3FF36B0A2D607FFC2480068A26D` | `--check` passed; stderr `0` |
| Route/runtime | `97,460` | `A127CA98F7ADF1C2BE62265A78C759BCF36CD85F7EB377203514D8DBC36F5E21` | Route `11/11`, return/floor checks, and exact facade runtime marker passed |
| Visual pre log | `108,920` | `2E85408A378E46E200AF57807FE953BF3E489EBBF6784ABED23CDFB1D827DA97` | Fixed pre-proof capture process passed |
| Visual post log | `109,811` | `A87CAB70BCD8AE3D627C1A26E5B3F0E48328BCC86DEC654B72BFFC83DEEE39ED` | Fixed post-proof capture process passed |
| Pre prompt PNG | `972,357` | `5D20A59F85895EA8177FA895C6DC860F7FE11E8706EFFFCA82C1AEA72F5E7CA8` | Original `1280x720` placement baseline |
| Pre leave PNG | `1,050,478` | `514C3653E1412FA19AD026AA5959787302B7B5979E442C6547E23F0BE1324309` | Original `1280x720` return baseline |
| Post prompt PNG | `967,649` | `BB6A8BB744F62ADB5358BFF27DB5C55B8EBD42A21D7434A1FB3D406FA46399F0` | Original `1280x720` post-placement evidence |
| Post leave PNG | `1,038,049` | `AC6264DE1E9ED5CC674E34179EB8D2986488FDBCC77AE1FADE1703BE5871B7E1` | Original `1280x720` post-return evidence |
| Pre resource CSV | `1,785` | `100BC7EF9E7284B15515AAD332078961049A9F6E444285A23650372E77FBD4AE` | Forty samples; average working/private bytes `1,649,402,470 / 3,808,128,102` |
| Post resource CSV | `1,796` | `F1631BF9EAF70898215CDE78C9E5B14465FB2E4CCEEFB4D3580C4CCFA87E17D8` | Forty samples; average working/private bytes `1,612,551,885 / 3,761,102,950` |

The four fixed-view images are placement and no-regression evidence only. The facade is distant in those frames; they do not prove close-up material quality, subjective readability, or final appearance.

Import/reimport determinism is semantic only: both runs reproduce the exact geometry, material, placement, and safety contract, while the UAsset bytes changed between imports. No byte-identical UAsset claim is made.

The accepted post-route packaged-runtime inventory snapshot is `57` files / `1,051,975,057` bytes. The canonical package boundary excluding runtime-created `Saved` output is `50` files / `1,051,962,028` bytes. It contains zero Python files and no `.cpp`, `.h`, `.fbx`, or `.blend` source. Exact protected package identities are:

- wrapper: `171,520` bytes, SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`;
- game executable: `341,401,600` bytes, SHA-256 `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A`;
- UFS `.ucas`: `208,199,024` bytes, SHA-256 `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356`.

The exact changed production/source identities are:

- `PlaceholderLocomotion.cpp`: `625,062` bytes, SHA-256 `5F4FFC0DF7B6922A73C4E569F2689D19D0DDA7FC4ADF211C19D173A39B44C93A`;
- `DefaultGame.ini`: `675` bytes, SHA-256 `CE966B4DEF240A9F99712BBF79BD1F9832125D4251FCEFB60498458523F86048`;
- source FBX: `17,068` bytes, SHA-256 `A86658B3D110D85E51DDA411B4D350FB4F362DFDC411B31BDB5671847BF8E238`;
- source manifest: `4,305` bytes, SHA-256 `782642EE609371F3992230FB415AF76C69305C5592782F037B09EC6D1A77D0B0`;
- mesh UAsset: `75,248` bytes, SHA-256 `7DA2F8FED4D9AD697CCE27EC25AFE179104652DC3F22F3D09FE37148358E6F00`;
- material UAsset: `4,583` bytes, SHA-256 `319D99862F0F1DEEEFF50F1EE78E1A5465356848D5D5FF053FFA3D36C6EC6968`.

Both UAssets have the expected Git LFS filter/diff/merge attributes and prospective pointer identities. The protected map remains `83,147` bytes with SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.

Dedicated-server runtime logs are rejected because this workspace has no Server target. Their retained identities are `DedicatedServer.log`, `92,633` bytes, SHA-256 `621E04ACDE8CE976464C636719D727A25D72FD6CBD277C4F9EB94E190A885FA9`; `DedicatedEditorServer.log`, `176,418` bytes, SHA-256 `6BD970142F022AEBFB562BA6859774744C544B5547B6AF08C7FD715AC60D7DAB`; and `DedicatedClient.log`, `86,594` bytes, SHA-256 `F4B8BAB2E772DE02F679F5ECCAE3EA24F39E6BE115FC19ABB1975715CD343B16`. The accepted boundary is the static `NM_DedicatedServer` guard plus the focused native contract; no dedicated-runtime proof is claimed.

The final targeted audit passes exact ten-path scope with staged paths `0`, documentation consistency, Beta Delivery Roadmap canvas JSON `22` nodes / `0` edges / `22` unique IDs, vault-aware Wiki links, `git diff --check`, full-digest ledger integrity, UAsset LFS attributes and prospective pointers, package/source/map identities, zero backup/temp artifacts, target processes `0`, UDP `17777` endpoints `0`, and TCP `1985` listeners `0`. Three unrelated PermitWatchdog processes were preserved.

## Production invariance

The protected authored map remains unchanged:

- `client/OddsWell/Content/Maps/SundaleGraybox.umap`
- SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`

The owner-accepted `2400x1800 m`, six-district, `144`-mass, sixty-tower planning baseline remains review authority only. The production graybox, canonical `800 m` route, required destination anchors, prompt radii, collision, navigation, lighting, city counts, services, business behavior, economy, wagering, saves, networking, brains, simulator, and Phase 1K behavior are unchanged.

Phase 1K remains incomplete at its hold-capable normal-input or observed physical-player evidence boundary. The owner deferred that hands-on route-usability evidence to the MVP playtest; it is not waived and this art proof supplies no Phase 1K credit.

## Truth boundary and owner gate

This phase proves that exactly one accepted residential-facade candidate imports, cooks, loads, faces the current Studio approach, retains its contracted geometry and palette, and survives the unchanged packaged route. It does not prove final architecture, final materials, collision, navigation clearance, LOD quality, occlusion at every angle, accessibility, subjective player response, minimum-PC performance, citywide repetition, beta readiness, or production readiness.

After local documentation, canvas, Coordinator pre-stage approval, exact local commit, and verified Notion closure, stop for the owner's `approve`, `request one bounded revision`, or `reject` decision. Approval would apply only to this one candidate and would not authorize a second facade, tower, reusable family, district expansion, citywide replacement, roadmap Phase 2, Version 1, deployment, or final art.

Cursor suitability is **NO**. The import, material fidelity, runtime presentation seam, package proof, and visual evidence are one coupled authoritative change. Cursor tasks created: `0`.
