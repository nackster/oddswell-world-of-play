# Intentional walking head turn

This editable Blender checkpoint starts from [AnkleSeat.blend](../AnkleSeatCandidate/AnkleSeat.blend), SHA-256 `3E56E25520E7811B52B761D7B4EFA2099135A86B61DEC3481664BEC78DBE4815`. Run `build.py` in Blender 4.5.5 with `--render` to rebuild [HeadTurn.blend](HeadTurn.blend), SHA-256 `DBE6D5827267B33A6F6849D34CD8B98D2518B8BD3FFB38F977D085CAAE69AA86`, and the native Cycles [face](Head_Turn_front.png) and [full rear](Head_Turn_full-rear.png) views.

The head turns six degrees toward the basketball setting while the body keeps its walking counter-rotation. The anatomical head, both eyes with irises and pupils, lashes, wet margins, scalp fibers, and brows move as one editable group around the neck base. Facial shape keys remain available. The separate head angle is stored on the scene, and the corneal clearance check follows the actual viewing direction. The saved scene and its parent both pass a cold `verify_scene.py --draft` check.

This makes the pose less centered and mannequin-like at close and full-body scale. It does not resolve the smooth facial expression/skin finish, broad shorts pattern, jacket flatness, or simplified shoe construction. The art remains an offline development checkpoint, not final human-realism acceptance or runtime integration.
