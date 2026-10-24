"""List every MetaHuman Creator preset with its skin tone coordinates and body settings."""
import unreal

log = lambda message: unreal.log(f"ODDSWELL_MH_PRESET|{message}")
library = unreal.EditorAssetLibrary
first = True
for path in sorted(library.list_assets("/MetaHumanCharacter/Optional/Presets", recursive=False, include_folder=False)):
    character = library.load_asset(path)
    if not isinstance(character, unreal.MetaHumanCharacter):
        continue
    skin = character.get_editor_property("skin_settings").skin
    fields = [f"name={character.get_name()}", f"skin_u={skin.u:.3f}", f"skin_v={skin.v:.3f}"]
    for prop in ("body_type", "fixed_body_type", "b_fixed_body_type"):
        try:
            fields.append(f"{prop}={character.get_editor_property(prop)}")
        except Exception:
            pass
    if first:
        first = False
        names = [name for name in dir(character) if not name.startswith("_")]
        log("attributes=" + ",".join(name for name in names if any(key in name for key in ("body", "skin", "groom", "hair", "type", "gender"))))
    log("|".join(fields))
log("done")
