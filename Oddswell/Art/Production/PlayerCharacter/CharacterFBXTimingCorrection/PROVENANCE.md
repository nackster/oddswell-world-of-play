# Corrected character FBX handoff

Date: 2026-09-12. Cost: $0. Blender: existing 4.5.5 LTS.

`build_timed_exports.py` reuses the existing FBX writer against the frozen `LandingActionCandidate` source. It preserves the earlier `CharacterFBXExport` directory and does not save or alter the Blender source.

The new handoff fixes three export details: the authored 28/44/30/30 fps Action rates, the standard `Armature` object wrapper recognized by Unreal, and outward float32-safe animation intervals that preserve the final integer frame. Geometry, skin weights, twelve source bones, and the four authored Actions remain unchanged. The wrapper is an object, not an additional bone.

The manifest records binary hashes and sidecars for the eight outputs, exact source identities, measured FBX intervals, and historical intervals. Two scene-reopen exports and an independent Blender invocation must reproduce the same files. The binary parser checks the actual exported time intervals, not just the writer's settings.

Run the existing Blender executable with `--background --factory-startup --python-exit-code 1 --python` followed by this builder's absolute path, with `PYTHONHASHSEED=0`. Treat a missing `ODDSWELL_TIMED_EXPORT_PASS` marker as a failure even if a process exits zero.

These remain character candidates. The imported assets are validated by `../UnrealImport/import_character.py`; no runtime wiring or final-art claim follows from these FBXs.
