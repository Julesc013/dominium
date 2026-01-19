--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `tools/`.

GAME:
- None. This spec is implemented under `tools/`.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.
- No runtime authority or game rules inside tools.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# UI Capability System (Backends + Tiers)

## Scope
- Defines the backend capability model used by `domui_validate_doc`.
- Describes how backends and tiers advertise supported widgets, properties, and events.
- Deterministic, backend-neutral, and declarative.

## Core identifiers
- Backend id: string (e.g., `"win32"`, `"dgfx"`, `"null"`).
- Tier id: string (e.g., `"win32_t0"`, `"win32_t1"`).
- Feature key: string (hierarchical, e.g., `"widget.listview.columns"`).

## Capability records
Each backend declares one or more tier capability records:
- Supported widget types (per tier).
- Supported properties per widget type.
- Supported events per widget type.
- Optional feature flags (emulated vs native).
- Optional limits (key → int).

## Registration
- Registration API: `domui_register_backend_caps(const domui_backend_caps&)`.
- Compiled-in tables are registered in `domui_register_default_backend_caps()`:
  - `win32_t0` (baseline Win95-era common controls)
  - `win32_t1` (NT6+ / Win7+ common controls)
  - `dgfx_basic`
  - `null_basic`

## Validation behavior
- Target set comes from `domui_target_set` or `doc.meta`.
- If no targets are specified, default is `["win32"]` + highest known tier.
- Errors:
  - unsupported widget type
  - unsupported property for widget/tier
  - unsupported event for widget/tier
  - tier mismatch or unknown tier
- Warnings:
  - features marked as emulated for a tier

## Determinism rules
- Diagnostics are sorted by:
  - severity (error before warning)
  - widget id
  - feature key
  - message
- No hashing or random identifiers in capability tables.
