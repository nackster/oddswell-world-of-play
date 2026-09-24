# Source-derived facial expression candidate

This editable Blender checkpoint starts from [HeadTurn.blend](../HeadTurnCandidate/HeadTurn.blend), SHA-256 `DBE6D5827267B33A6F6849D34CD8B98D2518B8BD3FFB38F977D085CAAE69AA86`. Run `build.py` in Blender 4.5.5 with `--render` to rebuild [FaceExpression.blend](FaceExpression.blend), SHA-256 `BB40C6B55EA5FF69B22E93C98F92B33ACA5823F0700146EA1E3D9018DD6E64E8`, and its native Cycles review views.

The builder maps four source-vertex targets from the unmodified [MakeHuman Faceunits 01 CC0 archive](../../../../../../source-assets/README.md) onto separate shape keys. Left/right mouth smile values are 0.30/0.22 and cheek response values are 0.16/0.12. The pose remains restrained and asymmetric rather than a broad grin. Wet eyelid margins, eyelash roots and brow roots are refitted to the evaluated head; their maximum correction is 0.223 mm. The original hm08 mesh, skin, torso, hands, garments, shoes and landscape are unchanged.

Review the [front close](Face_Expression_Front.png), [three-quarter close](Face_Expression_Three_Quarter.png) and [full rear](Face_Expression_Full_Rear.png) views. The scene passes a cold `verify_scene.py --draft` check, including optical clearance, shape-key bounds, attached eyelid and brow detail, and the existing body/cloth/shoe checks.

The expression helps the face read as a person at close range but does not establish photographic realism. Skin response, eye life, shorts construction, jacket drape and footwear remain open. This is offline art, not runtime integration.
