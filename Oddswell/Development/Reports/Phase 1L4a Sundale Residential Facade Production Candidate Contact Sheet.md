# Phase 1L.4a - Sundale Residential Facade Production Candidate Contact Sheet

Date: 2026-08-11
Branch: `agent/phase-0d`
Status: **COMPLETE LOCALLY - ONE PRODUCTION CANDIDATE, NOT IMPORTED OR INTEGRATED**
Cost: `$0.00`

## Scope authority

- [[Development/Beta Delivery Roadmap#Phase 1L.4a Sundale residential-facade production candidate contact sheet|Beta Delivery Roadmap Phase 1L.4a]]
- [[Design/Beta Game Bible#Bounded Sundale residential-facade production candidate|Beta Game Bible bounded production-candidate contract]]
- [[Design/Sundale Production Asset Scope#First bounded facade production candidate|Sundale Production Asset Scope first bounded facade candidate]]

## Outcome first

The owner accepted the six-district facade/tower architectural direction, allowed later bounded tweaks, and explicitly authorized the first build. Exactly one accepted review sample, `FACADE_SAMPLE__RESIDENTIAL_NEIGHBORHOOD_SERVICES`, is promoted into the original candidate `SM_Sundale_ResidentialFacade_A`. No second facade, tower, kit, or reusable family was started.

The Blender-native asset is exactly `5.2 x 4.1 x 5.0 m`, `96` triangles, `64` vertices, one UV channel, and one vertex-color material slot. It contains one mass, three opaque bays, one parapet accent, two shallow balconies, and one stoop. Its four-color subset is warm limestone `#D8C8A9`, muted terracotta `#A65F47`, sand concrete `#B9A783`, and charcoal gray `#4D5051`.

This is fresh owner-authorized production batch Phase `1/6`. Cursor delegation suitability is **NO** because the bounded work is the authoritative production source asset itself; Cursor tasks created: `0`.

Status remains `PRODUCTION_CANDIDATE_NOT_INTEGRATED`. This phase does not import or place the candidate in Unreal, change the production map or route, establish collision or LODs, expand the family, claim final art, or change gameplay.

## Exact artifact set

Repository root: `Oddswell/Art/Production/SundaleArchitecture/ResidentialNeighborhoodServices`

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `build_residential_facade_candidate.py` | `16,474` | `A09D95189999C97D1BD555E2F35514ABD00DEC9DED3577ED4610ED11E19975E6` |
| `SM_Sundale_ResidentialFacade_A.blend` | `424,061` | `F2CA073FA370BC345C91A83F76D15473086BC7FE6A3B85173E5076BF31BB8E58` |
| `SM_Sundale_ResidentialFacade_A.fbx` | `17,068` | `A86658B3D110D85E51DDA411B4D350FB4F362DFDC411B31BDB5671847BF8E238` |
| `manifest.json` | `4,305` | `782642EE609371F3992230FB415AF76C69305C5592782F037B09EC6D1A77D0B0` |
| `PROVENANCE.md` | `939` | `931B51303EAB64A0A0D7E001E0568CCC13461688360747EE4413DBB49342412A` |
| `renders/SM_Sundale_ResidentialFacade_A_ContactSheet.png` | `6,087,899` | `3123F2B86EAC1887C8B3C8C645C595240A58816B03403C9C573A8ACF17EB8D98` |

The root contains exactly these six files. The Blend and FBX are covered by existing Git LFS rules. Their generated LFS identities are respectively `f2ca073fa370bc345c91a83f76d15473086bc7fe6a3b85173e5076bf31bb8e58` / `424061` bytes and `a86658b3d110d85e51dda411b4d350fb4f362dfdc411b31bdb5671847bf8e238` / `17068` bytes. A corrective storage-only gate adds one exact path-specific `.gitattributes` rule for the accepted contact-sheet PNG; it does not introduce a global PNG rule, migrate prior art, or change/rerender the image.

`git lfs pointer --file` prospectively represents that unchanged PNG as exactly:

    version https://git-lfs.github.com/spec/v1
    oid sha256:3123f2b86eac1887c8b3c8c645c595240a58816b03403c9c573a8acf17eb8d98
    size 6087899

## Geometry, material, and provenance contract

| Contract | Accepted evidence |
| --- | --- |
| Identity | `SM_Sundale_ResidentialFacade_A` |
| Source review sample | `FACADE_SAMPLE__RESIDENTIAL_NEIGHBORHOOD_SERVICES` |
| Bounds | `5.2 x 4.1 x 5.0 m` |
| Geometry | `64` vertices / `96` triangles |
| Roles | mass `1`; opaque bay `3`; parapet accent `1`; shallow balcony `2`; stoop `1` |
| UVs | exactly `1` channel, `UVMap` |
| Material | exactly `1` slot, `M_Sundale_ResidentialFacade_VertexColor` |
| Vertex colors | `PaletteColor` |
| Palette | warm limestone, muted terracotta, sand concrete, charcoal gray only |
| External references | `0` |
| Status | `PRODUCTION_CANDIDATE_NOT_INTEGRATED` |

The builder uses only Blender, Python standard-library modules, and locally authored boxes. No external model, mesh, image, texture, font, brand, catalog, reference, framework, download, paid service, or third-party source was used.

## Build, export, reopen, and contact-sheet evidence

- Python `3.13` syntax compilation passed before the accepted build.
- Blender `4.5.5 LTS` headless build passed from factory startup.
- The saved Blend hash remained identical across the build/export sequence: `F2CA073F...8E58` twice.
- Blender FBX timestamps were normalized to a fixed value because the native exporter writes current milliseconds; two consecutive normalized exports were byte-identical at `A86658B3...E238`.
- Saved-Blend reopen validation reproduced the exact identity, bounds, `96` triangles, one UV, one slot, `PaletteColor`, and all role counts.
- A clean factory-startup FBX reimport reproduced one exact mesh, bounds `5.2 x 4.1 x 5.0 m`, `96` triangles, one UV, one material slot, and `PaletteColor`.
- The accepted original `3200x1800` contact sheet shows complete front, rear, left, right, top, and perspective views. Exact dimensions, triangle count, UV/material contract, palette, native provenance, source sample, and status are readable and frame-safe.

Canonical temporary validation ran from `C:\tmp\OddsWellPhase1L4a\CanonicalMirror`; its retained evidence is under `C:\tmp\OddsWellPhase1L4a\Evidence`. The mirror holds exact builder/provenance copies and keeps the repository artifact set untouched. Blender and FBX embed path-bearing metadata, and Eevee output may vary at the byte level between roots, so mirror-generated binary/render hashes are diagnostic rather than replacements for the six accepted repository identities above. Repository rehash after all three checks proves those six identities remained exact.

| Check | Exit | Stdout bytes / SHA-256 | Stderr bytes / SHA-256 | Accepted marker |
| --- | ---: | --- | --- | --- |
| Headless build/export/render | `0` | `Build.stdout.log`; `2,362`; `A0C8A3F4719961DC20C9C2F287294F6D8A76C4C4699878B2F3AC39901EB4BAD4` | `Build.stderr.log`; `0`; `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | JSON `status=PASS`; exact ID/bounds/roles/triangles/UV/material; two FBX exports |
| Saved-Blend reopen | `0` | `Reopen.stdout.log`; `968`; `6315F81871C143A4834B0248368A663B0F66586D8E6D19BFD777034937A2CED7` | `Reopen.stderr.log`; `0`; `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | JSON `status=PASS`; exact saved source contract |
| Focused clean FBX reimport | `0` | `Focused.stdout.log`; `580`; `7C02F8FAF71EFBB3507FDB892E17975D5CC5BB901F63D6A5D022B95DAF061BD3` | `Focused.stderr.log`; `0`; `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | JSON `status=PASS`; FBX `7400`, exact geometry/UV/material/color contract |

Two visual diagnostics are rejected. The first board was washed gray, clipped its title, and hid the views because copied objects inherited the source render-hidden flag. The first repair revealed a horizontal orthographic sensor-fit mismatch and low-contrast/shadowed labels. The accepted replacement fixes visibility, board framing, camera scale, and emissive label contrast without changing geometry, identity, counts, roles, palette, Blend, or FBX contract.

## Frozen regression and production boundaries

This art-only phase changes zero client, Unreal, runtime, map, config, test, gameplay, or package paths. No no-op engine, test, Brain Admin, cook, package, or packaged-route rerun was performed. The retained frozen evidence remains:

- native Unreal automation `72/72` PASS;
- Python `105/105` PASS;
- Brain Admin `--check` PASS;
- package `50` files / `1,050,423,644` bytes / zero Python;
- wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`;
- game executable SHA-256 `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`;
- UFS SHA-256 `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

The exact reused Python ledger is:

| Suite | Result | Retained log | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| `phase0a` | `9/9` PASS | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log` | `882` | `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` |
| `phase0b` | `2/2` PASS | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log` | `854` | `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` |
| `phase0c` | `8/8` PASS | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log` | `880` | `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` |
| `phase0d` | `46/46` PASS | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log` | `1,010` | `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` |
| `phase1h` | `40/40` PASS | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log` | `1,008` | `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` |

These five frozen results total `9 + 2 + 8 + 46 + 40 = 105/105`.

The protected `client/OddsWell/Content/Maps/SundaleGraybox.umap` remains SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`; production client diff is zero. No OddsWell, Unreal, Blender, or test process or gameplay port remained after verification. Two running Python processes belong to the separate PermitWatchdog workspace and were preserved.

## Truth boundary and next gate

The contact sheet proves one bounded source/export candidate and six readable review angles. It does not prove Unreal import, in-place appearance, collision, navigation, occlusion, LODs, final materials, runtime performance, accessibility, subjective player response, final architecture, final art, beta readiness, or production readiness.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. After Coordinator approval, local commit, and verified Notion closure, return to the Scope Director for exactly one fresh production batch Phase `2/6` gate. Do not import, integrate, expand the facade/tower family, start roadmap Phase 2, or schedule Version 1 without a separate gate.
