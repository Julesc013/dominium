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
# Game Content API

- Header: `include/dominium/game_content_api.h`; implementation in `source/dominium/common/game_content_api.c`.
- Purpose: thin Dominium-facing wrappers over Domino registries so game code/mods can register content without touching internal registries directly.
- Functions:
  - `dom_game_register_machine_type(const MachineType*)`
  - `dom_game_register_recipe(const Recipe*)`
  - `dom_game_register_tech(const Tech*)`
  - Blueprint helpers: `dom_game_create_blueprint(name, capacity)`, `dom_game_blueprint_add_elem`, `dom_game_blueprint_generate_jobs`
- Behaviour: deterministic, direct pass-through to Domino registries; IDs are sequential/stable for a session/build.