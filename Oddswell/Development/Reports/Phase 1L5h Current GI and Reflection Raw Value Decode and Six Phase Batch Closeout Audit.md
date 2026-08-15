# Phase 1L.5h Current GI and Reflection Raw-Value Decode and Six-Phase Batch Closeout Audit

- Date: 2026-08-14
- Branch: `agent/phase-0d`
- Baseline commit: `18d5b1d96a30a70a9c55b706f05431eb04ccec7f`
- Status: **COMPLETE LOCALLY — EXACT TWO CURRENT-CONFIG MAPPINGS EVIDENCED; SIX-PHASE BATCH CLOSEOUT PENDING COMMIT**
- Batch position: final Phase `6/6`, pending local documentation commit
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

This read-only audit authoritatively decodes exactly two current project-config raw values by using the installed Unreal Engine 5.8 source. Both rows are `MAPPING_EVIDENCED_CURRENT_CONFIG_ONLY`. Neither mapping selects future owner policy, proves an active visible rendering path, measures performance, validates candidate B, approves a minimum PC, or grants compatibility or readiness credit.

## Evidence custody

| Input | Bytes | SHA-256 | Relevant lines |
|---|---:|---|---|
| `client/OddsWell/Config/DefaultEngine.ini` | `2,755` | `1442E7ADF71B4028993465D95A92C12C9FB8E39D0DA4AC77229C6B920E38F6D1` | `14`, `16` |
| `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Engine\Classes\Engine\EngineTypes.h` | `164,419` | `0C18D1FACB72983298762C752D90FDB761D35084583C8B50E5427B6CD66D9538` | `450-468`, `470-485` |
| `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Engine\Classes\Engine\RendererSettings.h` | `100,365` | `A036AB5E245439BFED962FDF9A6EA510DE2E1DAA3704976593A150DCFC45F8DF` | `597-605` |
| `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Engine\Private\SceneView.cpp` | `130,957` | `8EE3DE0DED7B6454FC814E5F7357D48D989116B79AC2EF61972585A4BD1D9FD0` | `2121-2127` |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Evidence/route.log` | `96,908` | `4576B02AAD4D51A6E0F8F416ACB4181CF61AED38412FCE0BD1A4F4E851647347` | `482`, `526` corroborative only |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Evidence/manifest.tsv` | `2,179` | `9655738B19C35EB7635A20DD725869960D32CFCC9149F97E6846A845A933EC01` | retained manifest custody |
| [[Development/Reports/Phase 1L5e Direct Packaged Game Process Fixed Machine Resource Baseline]] | `4,768` | `EC84FD9FDAB8AF48D6062CE54C8D67E86D929128AE5F945A0FD3272F4CFAEE3C` | current-machine boundary |
| [[Development/Reports/Phase 1L5g Current Packaged Rendering API and Feature Evidence Inventory]] | `12,126` | `0362271E3CE7AD2F0C1F62A5C798F742A4A3C108959D952B4A8EAF13895B37A3` | rows `8-9` prior raw inventory |

No web source was needed. The installed UE5.8 source identities and cited lines were read directly; no engine, project, package, or evidence file changed.

## Exact two-row mapping inventory

| # | Surface | Exact current raw value | Status | Authoritative mapping evidence | Bounded result | Remaining owner policy and proof |
|---:|---|---|---|---|---|---|
| 1 | Dynamic GI method / raw mapping | `r.DynamicGlobalIlluminationMethod=1` | `MAPPING_EVIDENCED_CURRENT_CONFIG_ONLY` | `EngineTypes.h:450-468` says the enum must match this CVar and declares `enum Type : int` with `None` first and `Lumen` second, yielding implicit values `0` and `1`. `RendererSettings.h:597-600` binds the CVar to `EDynamicGlobalIlluminationMethod::Type`; `SceneView.cpp:2121-2122` reads the integer CVar and casts it to that enum. | Current project config raw `1` maps to `Lumen`. Retained `route.log:482` `r.Lumen.DiffuseIndirect.Allow:1` is corroborative only. | DEC-027 item `GI method/raw mapping` remains unresolved as an owner-policy/evidence item. Later owner selection and visible representative-B proof remain required. |
| 2 | Reflection method / raw mapping | `r.ReflectionMethod=1` | `MAPPING_EVIDENCED_CURRENT_CONFIG_ONLY` | `EngineTypes.h:470-485` says the enum must match this CVar and declares `enum Type : int` with `None` first and `Lumen` second, yielding implicit values `0` and `1`. `RendererSettings.h:602-605` binds the CVar to `EReflectionMethod::Type`; `SceneView.cpp:2126-2127` reads the integer CVar and casts it to that enum. | Current project config raw `1` maps to `Lumen`. Retained `route.log:526` `r.Lumen.Reflections.Allow:1` is corroborative only. | DEC-027 item `reflection method/raw mapping` remains unresolved as an owner-policy/evidence item. Later owner selection and visible representative-B proof remain required. |

Status totals are `MAPPING_EVIDENCED_CURRENT_CONFIG_ONLY` `2`, `MAPPING_UNRESOLVED` `0`, total `2`. No other status is used.

## Mapping is not owner policy or validation

This audit corrects only the documentary decode of the two current-config raw values from Phase 1L.5g. It does not select the future GI or reflection policy. The two retained `Allow:1` log markers corroborate Lumen-named current-machine settings only; they do not prove that a visible scene rendered with Lumen, establish effective post-process overrides, or supply performance evidence.

[[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]] remains unchanged. Its six selected terms remain `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`. Its eight unresolved items remain exactly, and in order:

1. `GI method/raw mapping`
2. `reflection method/raw mapping`
3. `AA method`
4. `upscaler`
5. `screen percentage`
6. `exact visible Medium scalability CVars`
7. `VSync`
8. `frame cap`

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; its historical evidence status remains `CANDIDATE_NOT_APPROVED`. Policy selection remains `1`; tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Six-phase closeout ledger

| Phase | Scope | Local commit | Notion custody | Bounded result |
|---:|---|---|---|---|
| `1/6` | Phase 1L.5e direct packaged-game current-machine resource baseline | `388537de84eb2f9dceb7e82aa56bb89f15c6acb2` | verified two upserts | `CURRENT_MACHINE_ONLY`; no minimum-PC inference |
| `2/6` | Phase 1L.5f candidate minimum-PC specification decision packet | `5e821a3adf8ab07a33131ec011639d1d071fcc50` | verified two upserts | three candidates; all historically `CANDIDATE_NOT_APPROVED` |
| `3/6` | Phase 1L.5f.1 Balanced 1080p60 owner-selection closure | `c9cba81dfcd6f315c9e436e14698fd13c0bf0651` | verified two upserts | B `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; validation incomplete |
| `4/6` | Phase 1L.5g current packaged rendering API/feature evidence inventory | `ca32072e92fe699304c6fe3dece4f432d7bc196c` | verified two upserts | exact `16` current config/runtime evidence rows; no B validation |
| `5/6` | Phase 1L.5g.1 compatibility-first Direct3D policy closure | `18d5b1d96a30a70a9c55b706f05431eb04ccec7f` | verified exactly two upserts | six policy terms selected; unresolved items remain `8`; tests and validation `0` |
| `6/6` | Phase 1L.5h exact two-row current raw-value decode and batch closeout | `PENDING_LOCAL_COMMIT` | not performed or authorized | current config mapping only; no policy, performance, compatibility, minimum-PC, or readiness result |

The commit chain for completed Phases `1-5` is exact and ordered: `388537de84eb2f9dceb7e82aa56bb89f15c6acb2` → `5e821a3adf8ab07a33131ec011639d1d071fcc50` → `c9cba81dfcd6f315c9e436e14698fd13c0bf0651` → `ca32072e92fe699304c6fe3dece4f432d7bc196c` → `18d5b1d96a30a70a9c55b706f05431eb04ccec7f`.

## Final boundary

No runtime launch, test, source or config change, package or map operation, DEC change, representative-system proof, performance measurement, procurement, product work, Notion work, or readiness work occurred. Phase 1K remains incomplete and not waived. Hands-on/input/accessibility evidence remains deferred until the end and is NOT WAIVED. Brain maturity remains frozen as truthful maturity inventory only; no training, learning, retraining, or readiness claim follows. Music and Phase 1L exit remain incomplete. Phase 1M, roadmap Phase 2, Version 1, minimum-PC approval, beta readiness, production readiness, and release remain unauthorized.

**NO SEVENTH PHASE — BATCH STOPPED**
