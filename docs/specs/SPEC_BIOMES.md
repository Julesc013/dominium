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
# Biomes

- Types: `BiomeType { id, name, min/max temp, precip, height, humidity }` (TempK/Q16.16). Register via `dbiome_register_type`; defaults include temperate_forest, desert, tundra, and wetland.
- Field: `biome_id` is a registered `dfield` (U8 storage for now) so tile/chunk storage can be shared with other systems.
- Classification: `dbiome_get_at_tile(body, WPosTile)` samples `dclimate` means, folds in local height and nearby water depth from `dhydro`, then calls `dbiome_classify`. Ranges are inclusive; zero ranges are treated as “don’t care”.
- Usage: game/ecs picks flora/fauna/visual sets from the returned `BiomeId`; callers can also fetch types via `dbiome_get_type`.
- Determinism: fixed-point only; no floating-point thresholds. All queries are on-demand—no private biome grids that bypass `dfield`.