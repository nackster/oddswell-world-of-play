"""Let the MetaHuman body skeleton play the standard UE5 mannequin locomotion (ABP_Unarmed and its
animations) by marking the two skeletons compatible in both directions."""
import unreal

log = lambda message: unreal.log(f"ODDSWELL_MH_SETUP|{message}")
library = unreal.EditorAssetLibrary
metahuman = library.load_asset("/Game/OddsWell/Characters/MetaHumans/Common/Female/Medium/NormalWeight/Body/metahuman_base_skel")
mannequin = library.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
log(f"metahuman_skeleton={metahuman is not None}|mannequin_skeleton={mannequin is not None}")
for skeleton, other in ((metahuman, mannequin), (mannequin, metahuman)):
    compatible = list(skeleton.get_editor_property("compatible_skeletons"))
    if other not in compatible:
        compatible.append(other)
        skeleton.set_editor_property("compatible_skeletons", compatible)
        library.save_loaded_asset(skeleton, only_if_is_dirty=False)
    log(f"skeleton={skeleton.get_name()}|compatible={[s.get_name() for s in skeleton.get_editor_property('compatible_skeletons')]}")
log("done")
