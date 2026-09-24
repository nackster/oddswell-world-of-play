# Constructed canvas shoe candidate

This editable Blender checkpoint starts from [SeatRelax.blend](../SeatRelaxCandidate/SeatRelax.blend), SHA-256 `9BC408AB8BEBCECD30EB6131C6C6C538B759515C30E81E907728B9A57D762A25`. Run `build.py` in Blender 4.5.5 with `--render` to rebuild [ShoeCanvas.blend](ShoeCanvas.blend), SHA-256 `D2E19CB5416D9FF22B43291D1F7BAE1A704C1279513A0DC63EC986D15A723A33`, and its native Cycles close/full views. Run `render_gameplay.py` for the gameplay-camera view.

The existing low canvas shoes had editable toe, collar and reinforced heel material regions but read as a uniform gray cone from behind. This checkpoint shifts those canvas materials toward the reference's warmer off-white and adds short stitched runs exactly along each heel reinforcement boundary: 118 left and 111 right. The stitches follow a closed loop of shoe mesh edges; they are editable native curves. The soles, laces, ankle seating, anatomy, garments and landscape are unchanged.

Review [rear close](Shoe_Canvas_Rear_Close.png), [profile close](Shoe_Canvas_Profile_Close.png), [full rear](Shoe_Canvas_Full_Rear.png) and [gameplay](Shoe_Canvas_Gameplay.png). A cold `verify_scene.py --draft` pass retains the shoe and body checks. `verify_heel_seams.py` independently checks every new stitch endpoint against the evaluated upper; maximum surface distance is 0.308 mm.

The brighter fabric and constructed heel are a small improvement. The shoe silhouette remains plain and the ankle opening has a dark gap in close view. The shorts' upper pattern, jacket drape and skin/eye finish still need substantial work before human realism or the later architectural/planting roadmap can be accepted. This is offline art, not runtime integration.
