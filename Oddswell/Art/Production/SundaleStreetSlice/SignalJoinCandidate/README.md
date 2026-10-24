# Signal-band armhole checkpoint

`SignalJoin.blend` starts from the exact [narrower-gait scene](../NarrowGaitCandidate/README.md) (SHA-256 `A07CE243DEEFD7A667D161AEA746FCBA0D267F4184838214E9D9B4CED54E3692`). The only art change is in the editable slate-jacket material: its rear teal mask now extends to X = −0.535 m (formerly −0.573 m), and its upper height limit rises to 1.347 m (formerly 1.3437 m). Saved scene SHA-256: `440A054D60821E8978AEFC6BB863624766C3FDE0A73CB30D691DD79DDAA4C8C8`.

The previous rear close-up showed a dark 23-pixel break at the right armhole around image row 275. The [new close-up](Signal_Join_Rear.png) has one connected teal run through that row. [Full rear](Signal_Join_Full_Rear.png) and [gameplay](Signal_Join_Gameplay.png) native Cycles renders confirm that the jacket signal reads continuously at character scale. The front remains slate apart from the existing upper-sleeve accents. The underlying jacket geometry, yoke objects, packed maps, and source licenses are unchanged.

The cold `verify_scene.py --draft` check passes on the saved Blend: one open jacket shell with neck, waist, and cuff boundaries; three shorts openings; fitted skin, hands, face, shoes, and 31 packed texture maps. This is editable offline Blender art, not a runtime character or animation rig.

The broader human-realism goal remains active. The shorts seat/crotch still reads too smooth and bulbous, the jacket drape remains stiff in places, and the face and body remain visibly CG compared with the original photographic concept. Rebuilding the upper shorts around the posed pelvis and rechecking the full-body silhouette are the next character steps before architectural, retail, and planting polish.
