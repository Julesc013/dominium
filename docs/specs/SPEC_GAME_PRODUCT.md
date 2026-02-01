Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Dominium Game Product (C++98)

## GameConfig
- `dominium_home`: overrides `DOMINIUM_HOME`; defaults to working dir/env.
- `instance_id`: defaults to `default`.
- `universe_id`: optional logical universe selector within the instance.
- `mode`: `gui` (default), `tui`, or `headless`.
- `server_mode`: `off` (default), `listen`, or `dedicated`.
- `demo_mode`: gate demo-only flows; default off.
- `platform_backend` / `gfx_backend`: optional backend hints passed to Domino `dsys` / `dgfx`.
- `tick_rate_hz`: fixed-step rate; 0 uses the built-in default (60 Hz).

## Initialization Flow
- Resolve paths via `resolve_paths` using `dominium_home` or `DOMINIUM_HOME`.
- Load instance metadata; if missing, build a deterministic default (seed/size/versions) and attempt to save.
- Evaluate compatibility (`ProductInfo{product="game", role_detail="client"/"server"}`); abort on incompatible, flag limited/readonly for later save guards.
- Initialize `DomSession` with platform/gfx hints and mode-derived `headless`/`tui` flags.
- Create the main `d_view`, initialize DUI context, and build a root UI shell.
- Enter state machine at `BOOT`, then `MAIN_MENU → LOADING → RUNNING`.

## Universe selection (instance-scoped)
- Universe selection is resolved within the active instance.
- Launcher handshake may supply `universe_id`; mismatches must refuse by
  default (`docs/specs/SPEC_LAUNCH_HANDSHAKE_GAME.md`).
- Universe bundles are loaded via the portable container defined in
  `docs/specs/SPEC_UNIVERSE_BUNDLE.md` and must satisfy identity binding rules.

## Main Loop
- Fixed-timestep tick via `d_sim_step(sim, 1)`.
- Net/replay integration must produce a deterministic command stream per tick;
  the sim must never read platform input directly (see `docs/specs/SPEC_ACTIONS.md` and
  `docs/specs/SPEC_DETERMINISM.md`).
- Rendering (GUI/TUI): gather the shared `dgfx_cmd_buffer`, call `d_view_render`, layout/render DUI, then `dgfx_execute` + `dgfx_end_frame`.
- Headless mode skips rendering but still advances simulation.

## Save/Load Wrappers
- `game_save_world(world, path)`: wraps `d_serialize_save_instance_all` and `d_serialize_save_chunk_all` over all loaded chunks into a simple TLV file (instance tag + per-chunk tags).
- `game_load_world(world, path)`: reads the TLV container, applies instance data, and recreates chunks via `d_world_get_or_create_chunk` before calling `d_serialize_load_chunk_all`.
- Storage is engine-only; no Dominium-specific metadata is injected.

## Universe bundle I/O (high-level)
- Import/export of universe bundles uses relative paths resolved via the
  filesystem contract (`docs/specs/SPEC_FS_CONTRACT.md`).
- The game does not scan or infer install layouts.

## UI Shell
- DUI-based root with a simple main menu (`Dominium` title, New/Load/Import/Export Universe, Exit buttons) and a stub in-game HUD bar.
- Rendering and layout stay inside DUI/DVIEW/DGFX; no platform-native drawing.