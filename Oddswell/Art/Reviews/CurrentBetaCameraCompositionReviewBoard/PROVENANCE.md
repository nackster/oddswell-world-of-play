# Current Beta Camera Composition Review Board Provenance

- Phase: `Phase 1L.3l`.
- Status: source-locked, nonproduction composition review evidence.
- Generator: `build_current_camera_composition.py` using the Python standard library only.
- City authority: `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` at SHA-256 `22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298`.
- City facts: `CITY_THIRD_PERSON_TRAILING`; boom `420`; attachment `+65`; collision `true`; pitch `-65..65`; continuous yaw; FOV literal `ENGINE_DEFAULT_UNSET` because the source does not set a camera FOV.
- Stadium authority: `client/OddsWell/Source/OddsWell/ReplayBenchmarkActor.cpp` at SHA-256 `CE070D7EC2EF7D94093B5CD943C271426BCF8A10B7D31D287BC32235FD8F3116`.
- Stadium facts: `STADIUM_FIXED_BROADCAST`; location `(2400,-3000,1800)`; rotation `(-25,129,0)`; fixed FOV `55`.
- Scenarios: `CITY_AVATAR_CLOTHING_READ`, `CITY_DESTINATION_LANDMARK_READ`, `STADIUM_FULL_COURT_ACTION_READ`, `STADIUM_SCORE_EVENT_SAFE_AREA`.
- Palette: `#2C4250`, `#50B3AD`, `#FAE595`, `#999EA2`, `#FAF8F0` only.
- Geometry: native SVG geometric proxies only; five-percent outer content margin; complete proxy and label containment; zero proxy-label overlap; stadium top eighteen percent reserved as a HUD band.
- Accessibility measurement: text contrast floor `4.5:1`; graphic contrast floor `3.0:1`. These measurements do not claim accessibility readiness.
- External references, images, fonts, textures, brands, scripts, animation, and runtime changes: none.
- Claim flags: `production_claim=false`, `camera_change=false`, `lens_lock=false`, `accessibility_ready=false`, `gameplay_change=false`.
