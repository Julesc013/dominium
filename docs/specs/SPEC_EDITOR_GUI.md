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
- None. Game consumes engine primitives where applicable.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# Dominium Editor GUI

A unified GUI host for editor backends. Uses the same dsys/dgfx stack as the launcher and drives the existing `_edit` APIs, so future CLI/TUI/GUI front-ends all share the same logic.

## Modes and backends

- **World Editor** → `dom_world_edit_api`: open a world, view chunks, toggle tiles, save changes.
- **Game Data Editor** → `dom_game_edit_api`: browse kinds (`recipe`, `item`, `machine`), inspect/edit JSON blobs, save.
- **Launcher Editor** → `dom_launcher_edit_api`: list tabs, reorder/add/remove, save config.
- **Save Editor** (minimal) → `dom_save_edit_api`: list sections/keys, edit values, save.

## Application flow

1. Initialize `dsys`, create a window, and (later) a dgfx device for rendering.
2. Enter a single event loop:
   - Poll `dsys_event`s (quit/keys).
   - Build GUI for the active mode (menu bar + mode panels).
   - Render via dgfx (stubbed initially; extend with dom_ui/dgfx widgets).
3. Map keyboard shortcuts:
   - `Ctrl+O` to open content for the active mode.
   - `Ctrl+S` to save.
   - `Ctrl+Tab` to switch modes.
   - `Esc` to quit.

## Entry points

- Executable: `dominium-editor` (see `source/dominium/tools/editor_gui/editor_gui.c`).
- CLI args for bootstrapping paths:
  - `--world <path>`
  - `--save <path>`
  - `--defs <path>`
  - `--launcher <path>`

## Extensibility

- Mod/pack editors can build on `game_edit_api` and mod APIs and be added as another mode.
- UI layer is intentionally thin; factor shared widgets with the launcher GUI to avoid duplication.