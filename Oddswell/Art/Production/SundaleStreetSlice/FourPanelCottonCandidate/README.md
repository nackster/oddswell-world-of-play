# Four-panel cotton shorts over the torso/hip stance

This editable native checkpoint continues [BodyFlowCandidate](../BodyFlowCandidate/README.md), SHA-256 `13B5DE6E9BA2471F2A19F538B806FB05C052B35E0CC50D56CD65E5178E82B18A`. It replaces the previous annular upper shorts and paired narrow bridge with four newly drafted front/rear panels. Their welded side, rise and inseam edges form one surface with an open waist and two hems. The existing hem/facing registration fades into the new pattern. The slate/teal jacket, adult anatomy, torso/hip counter-rotation and OddsWell street setting remain the starting design.

[build.py](build.py) retains 5,279 controls and 5,120 faces, a four-island cloth UV layout and the [panel layout](panel-layout.json). It fits a broad displacement field against the posed pelvic and leg supports, settles the cotton for 35 native cloth frames, restores exposed-thigh clearance and rounds the sharp front crotch transition. A constrained 1 mm inner fabric shell replaces the previous 1.5 mm offset. Original drafted, collision-fitted and gravity-output positions remain separate point attributes. Back pockets and their stitches follow the rear surface while preserving their original offsets; hem stitches are refitted.

The native `Body flow | stance blend` control still drives 244 character parts. The new shorts have their own inverse-warped previous-stance shape and retained coordinates; zero restores that new pattern's prior stance, **not** the superseded shorts mesh. The original BodyFlow scene remains separately available. Original CC0 anatomy and licensed photographic maps are retained; there are 31 packed maps and no newly adopted external clothing assets.

Native review views:

- [Full rear](FourPanelCotton_Rear.png)
- [Full front](FourPanelCotton_Front.png)
- [Side profile](FourPanelCotton_Profile.png)
- [Rear shorts close-up](FourPanelCotton_ShortsRear.png)
- [Gameplay scene](FourPanelCotton_Gameplay.png)

[audit.py](audit.py) cold-opens the saved scene and checks the three garment openings, closed evaluated fabric volume, stance control and complete cloth overlap screen. At the retained pose, the BVH screen finds zero nonadjacent overlap pairs on both the whole midsurface and thick shell. World-space checks over 21,180 evaluated exposed-thigh cloth points and 47,089 pelvic-region points give minimum midsurface clearances of 5.438 mm and 4.192 mm. The artificial leg top closure is excluded from the lateral skin check. These checks establish static fit; animation and production rig compatibility remain later work. [FourPanelCotton-audit.json](FourPanelCotton-audit.json), [cold-check.json](cold-check.json) and [Delivery-manifest.json](Delivery-manifest.json) retain the evidence and exact artifact hashes.

Pocket stitches are checked against their actual pocket surfaces, within 0.452 mm; the hem stitches remain within 1.061 mm of the shorts. The complete visible character evaluates to 3,462,436 viewport triangles across 313 objects and 35 materials. The new shorts account for 330,240 triangles versus 455,008 in BodyFlow; this is a pattern replacement rather than runtime optimization. Scalp fibers still account for 1,728,000 triangles. These planning measurements keep hair/detail baking, a rigged derivative and measured LODs in the later engine handoff requirements.

The human-realism goal remains active. The new pattern removes the old narrow slit construction, but the figure still has smooth cloth, a generic face and artificial jacket shoulder/collar transitions. Continue torso/shoulder/sleeve drape and individual facial presentation, then judge the complete figure against the original concept. Architectural/retail variety, selective planting and controlled Unreal handoff remain in the established dependency order. This scene is an offline art checkpoint; export/import preparation remains stopped pending the existing visual acceptance gates.
