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
# SPEC_UI_WIDGETS — Widgets, Layout Profiles, and HUD Customization

Status: draft  
Owner: Dominium game layer  
Scope: UI projections only (no authoritative world access).

## Purpose
Defines the data-driven widget and layout system used by the UI. Widgets are
pure projections of capability snapshots and never access world state directly.

## Core invariants
- Widgets consume **capability snapshots only** (`dom_capability_snapshot`).
- Widgets never query authoritative world state or BeliefStores directly.
- Missing or insufficient knowledge yields `UNKNOWN` or hidden widgets.
- Layout changes are non-sim and do not affect determinism or replay.
- Projection modes are explicit and deterministic (no view-driven activation).

## Data sources
Two TOML-like files are consumed:
- `widgets.toml` — widget definitions
- `layouts.toml` — layout profiles + instances

### Widget definitions (`widgets.toml`)
Required fields:
- `id` (string, unique)
- `capability` or `required_capabilities` (capability ids)

Optional fields:
- `label` (string, display label)
- `min_resolution` (numeric or name)
- `allow_uncertainty` (bool)
- `width_px`, `height_px` (ints)
- `draw_panel` (bool)

Capability names map to `dom_capability_kind`:
`time_readout`, `calendar_view`, `map_view`, `position_estimate`,
`health_status`, `inventory_summary`, `economic_account`, `market_quotes`,
`communications`, `command_status`, `environmental_status`, `legal_status`.

### Layout profiles (`layouts.toml`)
Profiles define projection scope and widget instances.

Profile fields:
- `id` (string, unique)
- `projection` (`diegetic` | `hud` | `world_surface` | `debug`)

Instance fields:
- `widget_id` (string, required)
- `projection` (optional override)
- `anchor` (`top_left` | `top_right` | `bottom_left` | `bottom_right` | `center`)
- `x`, `y` (ints)
- `scale` (Q16.16, e.g. `1.0`)
- `opacity` (Q16.16, e.g. `0.85`)
- `enabled` (bool)
- `input_binding` (string, optional)

## Rendering rules
- A widget renders only when `instance.projection == render_pass.projection`.
- If any required capability is missing:
  - `allow_uncertainty = true` → render with `UNKNOWN`.
  - `allow_uncertainty = false` → widget is hidden.
- If `resolution_tier < min_resolution`, treat as unknown.
- Flags are surfaced in UI text:
  - `STALE`, `DEGRADED`, `CONFLICT`.

## Determinism
- Widget definitions are sorted by `id` after load.
- Layout profiles are sorted by `id` after load.
- Instance order is the file order (deterministic).
- All parsing is integer-based; no locale or OS time APIs.

## Example
```toml
[[widget]]
id = "time"
label = "Time"
capability = "time_readout"
min_resolution = 1
allow_uncertainty = true
width_px = 200
height_px = 36
draw_panel = true

[[profile]]
id = "default"
projection = "hud"

[[instance]]
widget_id = "time"
anchor = "top_left"
x = 16
y = 16
scale = 1.0
opacity = 1.0
enabled = true
```

## Testing requirements (non-exhaustive)
- Deterministic parsing of widgets/layouts.
- Unknown gating (hidden vs `UNKNOWN` rendering).
- Projection filtering (diegetic vs HUD).
- Deterministic text outputs for identical snapshots.

## References
- `docs/specs/SPEC_EPISTEMIC_INTERFACE.md`
- `docs/specs/SPEC_UI_CAPABILITIES.md`
- `docs/specs/SPEC_INFORMATION_MODEL.md`