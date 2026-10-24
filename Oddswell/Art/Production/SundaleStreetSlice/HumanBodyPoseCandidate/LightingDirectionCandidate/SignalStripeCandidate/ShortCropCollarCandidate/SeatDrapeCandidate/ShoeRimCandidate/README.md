# Fitted shoe collar candidate

This editable Blender checkpoint starts from [ShoulderSlope.blend](../ShoulderSlopeCandidate/ShoulderSlope.blend), SHA-256 `001A7AC72CBB8B81228489DE0858ED4F9E85408930B21F459E2C6B0373171C32`. Run `build.py` in Blender 4.5.5 with `--render` to reproduce [ShoeRim.blend](ShoeRim.blend), SHA-256 `271C0FCD4AFF680541094C6B2FEFF39B5AE059AD086B3AED6F9D29F3A27C7C43`, and the native Cycles review images.

The former shoelace-collar curves projected beyond the ankle in profile. They are removed. A bound canvas trim now follows each shoe's actual curved opening: the left and right continuous loops contain 160 and 135 edges respectively. The upper, sole, laces, stance contact, leg anatomy, jacket and shorts remain editable. Review the [rear](Shoe_Rim_Rear_Close.png), [profile](Shoe_Rim_Profile_Close.png), and [full-body rear](Shoe_Rim_Full_Rear.png) views. A cold reopen passes `verify_scene.py --draft` for the complete scene.

This is a modest construction improvement. The upper still reads too smooth and the heel/sole proportions still need work to meet the realistic-human target. The shorts, jacket cloth, face, and walking weight also need visual review before the character is complete. Architecture, retail detail, and planting follow the character work. This is offline native art and makes no runtime integration claim.
