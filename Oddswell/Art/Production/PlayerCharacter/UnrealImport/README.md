# Character import and cold validation

This editor-only script imports the corrected eight-file handoff into one skeleton, four skeletal meshes, and four animation sequences. It refuses preexisting destination assets, verifies hashes before importing, and checks all asset paths, skeleton references, bone hierarchies, stature, animation timing, finite sampled poses, changing rotations, and zero root translation before accepting the result.

Use the already-installed UnrealEditor-Cmd.exe with the OddsWell project, `-unattended -nop4 -NullRHI -NoSplash -NoSound -EnablePlugins=PythonScriptPlugin` and `-ExecutePythonScript=` followed by this script's absolute path. Set `ODDSWELL_CHARACTER_REPORT` to a new absolute JSON path and `ODDSWELL_CHARACTER_MODE` to `import`. The installed Python plugin is enabled for that editor invocation only; the project configuration is unchanged.

After import, start a separate editor process with mode `verify` and a fresh report path. Require process exit zero, JSON status `PASS`, the explicit `ODDSWELL_CHARACTER_IMPORT_PASS` log marker, exactly nine UAssets, and unchanged asset hashes across the cold verification. Unreal can exit zero after a Python exception, so process exit alone is insufficient.

The initial skeleton rename can save a skeleton before the entire candidate passes. After a failed import, preserve the attempt's logs, exit status, and failure JSON; inspect its exact new files before removing or moving only that attempt's partial candidate. Never overwrite an existing accepted set or broadly clean the Content directory. The script does not wire assets to the runtime pawn, create materials, save a map, or modify movement or game authority.

Validated evidence is in `character_import_evidence.json`. Detailed phase results and remaining scope are in the linked Obsidian phase report.
