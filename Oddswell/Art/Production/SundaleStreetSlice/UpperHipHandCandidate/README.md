# Upper hip and relaxed hand development

An intermediate offline human study continuing `BodyBalanceCandidate`. The native file is `UpperDrape.blend`. The source torso, pelvic support, skin, clothing, OddsWell slate/teal palette and Sundale scene remain editable.

The visible hip change is deliberately modest: 978 graded front controls move at most 2.089 mm. A new Basis-relative key adds a smoothed portion of the native physical rest study while preserving waist boundaries and lower hems. This is an authored rest shape with native rig deformation, not dynamic cloth during the walk.

The separate `Native walk with relaxed resting fingers` action opens the four non-thumb digits of each hand by 6, 10 and 5 degrees at their three joints. The original action remains saved with a retention flag. This softens the hooked resting pose while preserving the body walk.

`rebuild.py` reconstructs the new key from the declared offsets in `build-report.json` and translates the specified finger curves directly. It keeps original animation, old shape keys, cloth modifiers and source UVs. `physical-study.py` records the larger diagnostic experiment that informed the offsets; its full free-drape result was rejected. Its solver tunings are art parameters and have no calibrated cotton-material claim.

`cold-audit.json` covers cold source custody and exact declared changes. `probe.json` covers eleven selected authored poses using actual render-resolution triangles. Neither report closes inherited contacts, subframes, complete body contact or runtime acceptance. `render-provenance.json` records the reviewed images and walking preview.

Visual acceptance remains open. The hip gain is barely visible, the torso and upper thighs still read too smoothly, and the collar, face and clothing finish need stronger work. See `WholeFigureReview.md` for the next body and scene steps. This checkpoint does not change the separate starter-outfit or engine-handoff gates.
