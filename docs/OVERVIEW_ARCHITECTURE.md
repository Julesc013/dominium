# Dominium Architecture Overview

- **Domino**: C89 deterministic engine exposing systems (world, sim, gfx, ui, content). No RTTI/exceptions; ABI kept stable via POD structs and TLV blobs.
- **Dominium**: C++98 product layer (game, launcher, setup, tools) built on top of the Dominium Common Layer. Products never reach into backend/platform details directly.
- **Repository layout** rooted at `DOMINIUM_HOME`:
  - `repo/products/<product>/<version>/bin/` – packaged executables.
  - `repo/packs/<id>/<version>/pack.tlv` – content packs.
  - `repo/mods/<id>/<version>/mod.tlv` – mods/blueprints.
  - `instances/<id>/` – per-instance metadata and saves.
  - `temp/` – scratch space for setup/tools.
- **Common Layer** (dom_paths/instance/packset/session/compat): resolves paths, loads instance metadata, picks packs/mods, boots the engine, and evaluates compatibility without touching platform APIs.
- **Product flow**: Launcher discovers products/instances → compatibility check → spawns chosen product with `DomSession` wiring packs/mods → DSIM drives world; DVIEW + DUI render UI; replay/net subsystems bolt on through the engine.
- **Extensibility**: Tools and setup reuse the same path/instance/compat helpers; future GUI/TUI shells stay inside DVIEW/DUI while respecting deterministic ordering for content resolution.
