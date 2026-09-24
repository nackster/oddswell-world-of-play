# Restrained ankle seat candidate

This editable Blender checkpoint starts from [CottonResettle.blend](../CottonResettleCandidate/CottonResettle.blend), SHA-256 `5A25F314C84DB746BE5AA5E3629D1D048EB5689C41A6C9F1611B917F553BC8E0`. Run `build.py` in Blender 4.5.5 with `--render` to rebuild [AnkleSeat.blend](AnkleSeat.blend), SHA-256 `3E56E25520E7811B52B761D7B4EFA2099135A86B61DEC3481664BEC78DBE4815`, and the native Cycles review views.

An object-ID profile render showed that the anatomical lower leg crossed the shoe upper near the low heel collar. This checkpoint moves only 118 low ankle vertices inward beneath the canvas and carries/refits all 2,600 fine calf-hair strands with the skin; the maximum root correction is 2.03 mm. The separate heel-counter material now matches the main oat canvas tone, leaving its seam and construction geometry editable. No shoe mesh, sole contact, jacket, shorts, face, or street objects were changed.

Review [profile close](Ankle_Seat_Profile_Close.png), [rear close](Ankle_Seat_Rear_Close.png), and [full rear](Ankle_Seat_Full_Rear.png). A stronger ankle contraction created dark lateral collar gaps and was rejected. This restrained version reduces the skin crossover while preserving the rear collar fit. A cold reopen passes `verify_scene.py --draft`, including hair-root attachment and both sole contacts.

The gain is modest. The shoes still have broad, simple uppers and an underdeveloped heel/toe transition; the shorts pattern, jacket drape and face remain short of the owner's photoreal-human target. This remains an offline art checkpoint, not a final human-realism acceptance or runtime integration.
