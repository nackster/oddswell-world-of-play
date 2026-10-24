# Adult chest and fitted fabric checkpoint

`ChestContour.blend` continues the reviewed `TorsoSilhouetteCandidate` scene. Two editable keys introduce paired pectoral planes, a shallow lower-chest transition, sternum relief and collarbone contours in the body and jacket. A copied jacket material retains the licensed packed weave and existing physical panel UVs, with stronger weave bump and restrained rest-UV yarn variation. The original slate/teal design and walk remain.

Rebuild offline with Blender 4.5.5 by running `build.py`, then `material.py`. `audit.py` compares original custody and the complete jacket shell at render subdivision across 49 authored frames. `render.py` produces matched worn views; `--body` temporarily exposes clay anatomy without saving those diagnostic changes. `render-walk.py -- --preview` produces the 24 frames used for the 12 fps preview. Scripts resolve the repository root through `.git`; their immediate source and audit helpers must remain available.

This is an intermediate native art checkpoint. It does not close the requested very realistic human, authorize an engine handoff, or advance the separate starter-outfit acceptance, physical first-hour, Phase 1L or beta gates.
