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
Debug UI
--------
- The in-game debug panel is built with the DUI widget toolkit and can be toggled via the “Toggle Debug Panel” button (or `--devmode` to start visible).
- The panel shows current world hash, chunk count/coordinates, a resource sample at the camera focus, structure counts, loaded packs/mods, content registry counts, and determinism mode status.
- Debug widgets respect DUI visibility flags; when hidden they do not participate in layout or rendering.
- Dev mode marks the session as deterministic-by-default and keeps the panel visible to surface engine state during development.