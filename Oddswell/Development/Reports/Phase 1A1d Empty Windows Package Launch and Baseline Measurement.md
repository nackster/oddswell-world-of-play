---
tags:
  - development
  - phase-1a1d
  - unreal-engine
  - packaging
  - benchmark
status: complete
date: 2026-07-19
---

# Phase 1A.1d: Empty Windows Package, Launch, and Baseline Measurement

## Outcome

**EMPTY PACKAGE PASSED.** Unreal Engine 5.8 cooked, staged, packaged, archived, launched, and normally closed the unchanged Blueprint-only OddsWell bootstrap project as a local Windows Development build. The executable loaded `/Game/Maps/Bootstrap`, the six portable project inputs remained byte-identical, all generated output stayed ignored, and the frozen simulator and Admin checks remained green.

This proves only that the empty project can become a standalone local Windows executable on this workstation. It is not a representative city, gameplay, minimum-PC, release, scalability, or permanent-engine-adoption benchmark. No C++, Blueprint graph, gameplay, asset, replay adapter, network service, backend, economy, wagering, deployment, model work, plugin, or tracked Unreal input was added. Cost was **$0.00**.

## Frozen input proof

The same six hashes were recorded before packaging and after normal runtime exit:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `client/OddsWell/OddsWell.uproject` | 91 | `647D8775736EF90E3590EB7D98F5A301458948C2804AF2CFD68A272F9B5BB6D8` |
| `client/OddsWell/Config/DefaultEditor.ini` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `client/OddsWell/Config/DefaultEngine.ini` | 2,684 | `A3572A2B40D00436686E523150B8796F36C44EF40584F63B25A26BDBACC4BB8A` |
| `client/OddsWell/Config/DefaultGame.ini` | 357 | `728B0C6F53C5112F7715C5E26B901D9735C6D3FFA9CA83DE317CDBEA1CF727FB` |
| `client/OddsWell/Config/DefaultInput.ini` | 9,022 | `967BDF33123519D5270F44B2A686BE523DE7326CD2C038623B1D1C31FE7B49EA` |
| `client/OddsWell/Content/Maps/Bootstrap.umap` | 8,422 | `44FC5E531591672E10E3740A780EAFB34326C2EADC7D85A37CFA352541932C16` |

## Packaging method

The installed engine's bundled .NET 10 runtime ran its native `AutomationTool.dll` directly. This avoided adding a wrapper script or dependency and avoided the `RunUAT.bat` wrapper's inability to rotate its AppData log in the current process context. The Blueprint-only project used the installed engine binaries, so no speculative C++ target or `-build` step was introduced.

Clean package command:

`dotnet.exe AutomationTool.dll BuildCookRun -project=C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject -nop4 -utf8output -unattended -platform=Win64 -clientconfig=Development -cook -map=/Game/Maps/Bootstrap -stage -pak -package -archive -archivedirectory=C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Builds\Phase1A1d-Windows -clean -NoSign`

The unchanged incremental command used the same arguments, replaced `-clean` with `-cookincremental`, and reused the same controlled archive path.

| Measurement | Result |
| --- | ---: |
| Clean wall time | `191.420s` |
| Clean UAT BuildCookRun time | `190.65s` |
| Incremental wall time | `69.497s` |
| Incremental UAT BuildCookRun time | `68.73s` |
| Clean archive | 48 files; 968,405,621 bytes (`0.902 GiB`) |
| Incremental archive before launch | 48 files; 968,411,765 bytes (`0.902 GiB`) |
| Archive after runtime-created local settings | 51 files; 968,413,407 bytes (`0.902 GiB`) |

Both runs exited `0` with `BUILD SUCCESSFUL`. UAT validated Windows SDK `10.0.22621.0`, targeted only `/Game/Maps/Bootstrap`, staged, packaged, and archived without a cook, stage, package, fatal, or signing failure. The incremental log explicitly retained valid prior cook state and cooked only modified packages.

The packaged launchers remained generated and ignored:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `Windows/OddsWell.exe` | 171,520 | `4942BD6E3AC25544DA12A3CF6B42E830A06E49602F5AC19BF152710FFE714F8F` |
| `Windows/Engine/Binaries/Win64/UnrealGame.exe` | 339,665,336 | `BB9160CFF67D2A7A7D552CAD96AF8BFCB31D3186CEA83692B3743B2BD570D62C` |

## Standalone launch proof

The generated `OddsWell.exe` was launched once with transient `-windowed -ResX=1280 -ResY=720 -NoSplash -log` flags and `stat unit`. No portable config changed.

- The visible game window appeared `0.656s` after process launch. This is window-detection time, not full readiness.
- The runtime log reached `Game Engine Initialized` approximately `3.478s` after process start and completed engine initialization approximately `3.613s` after process start.
- The log browsed and loaded `/Game/Maps/Bootstrap?Name=Player` and measured the map load at `0.086006s`.
- The visible title was `OddsWell (64-bit Development PCD3D_SM6)` at `1280x720` and the empty map remained responsive.
- The final runtime-log scan found zero fatal error, critical error, unhandled exception, assertion, or prerequisite match.

## Preliminary empty-map performance

Three warm `stat unit` screen readings were captured ten seconds apart after the owner cleared the Windows Firewall prompt. These values describe an empty Development build on this workstation only.

| Reading | Frame | Game | Draw | RHI thread | GPU | Displayed memory | VRAM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 4.38 ms | 2.39 ms | 4.40 ms | 1.66 ms | 3.60 ms | 1.31 GB | 1.18 / 7.01 GB |
| 2 | 4.35 ms | 1.62 ms | 4.33 ms | 1.41 ms | 3.63 ms | 1.30 GB | 1.18 / 7.01 GB |
| 3 | 4.33 ms | 1.74 ms | 4.35 ms | 1.46 ms | 3.61 ms | 1.31 GB | 1.18 / 7.01 GB |
| Mean | **4.35 ms** | **1.92 ms** | **4.36 ms** | **1.51 ms** | **3.61 ms** | **1.31 GB** | **1.18 / 7.01 GB** |

Three process samples two seconds apart averaged `1,403,288,235` working-set bytes (`1.307 GiB`) and `2,538,172,416` private bytes (`2.364 GiB`). The large private reservation is recorded as observed Development-build behavior, not claimed as committed physical memory or a player requirement.

## Network and security boundary

- The packaged process owned no established TCP connection and no UDP endpoint.
- It owned one TCP listener on `0.0.0.0:1985`. The runtime log identifies this exactly as Unreal Trace's `Control listening on port 1985`; installed UE 5.8 source confirms `1985` is the Development trace-control default. This was an explained engine-development listener, not an OddsWell server or external connection.
- Windows displayed its firewall access prompt for the Epic-signed Unreal executable. Automation did not act on the security prompt. The owner manually selected **Cancel**, so the phase did not grant network access or weaken Windows security.
- Cook-time Zen discovery mentioned loopback, this workstation's Wi-Fi address, and its Tailscale address before using local `[::1]:8558`; those are local cache endpoints on this machine, not a project service or external API.

## Exit, disk, and repository hygiene

- A normal `Alt+F4` close produced `BeginTearingDown`, `CleanupWorld`, `Game engine shut down`, object-subsystem close, and `Exiting` in the runtime log.
- After close, no OddsWell, UnrealGame, UnrealEditor, ShaderCompileWorker, CrashReportClient, UnrealTraceServer, or Zen process remained.
- The controlled archive, `Intermediate`, and `Saved` trees remained ignored and unstaged. Their final observed sizes were `0.902 GiB`, `0.116 GiB`, and `1.360 GiB`; total generated project output was `2.378 GiB`.
- `C:` free space changed from 3,253,238,132,736 to 3,249,798,967,296 bytes, a whole-drive decrease of `3.203 GiB`. This is not a claim that every changed byte belongs to OddsWell or Unreal.
- Git remained clean before documentation. No executable, cooked asset, cache, log, local settings file, or generated package entered source control.

## Validation

- Frozen regression suite: **65/65 passed** in `275.662s`.
- Brain Admin self-check: **passed**.
- Six portable project hashes: **exact before and after**.
- Runtime map/fatal scan, normal-close evidence, process cleanup, generated-file ignores, package hashes, and no-external-connection inspection: **passed**.

## Next gate

Phase 1A.2a may add one noncanonical primitive-geometry street block and basketball court to a separate benchmark map and record one representative asset-iteration measurement. It must preserve the empty-package baseline and still must not choose the city identity, camera, avatar, multiplayer, final art, or permanent Unreal adoption. Recorded-replay rendering remains a later subphase.
