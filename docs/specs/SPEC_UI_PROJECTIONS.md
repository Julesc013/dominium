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
# SPEC_UI_PROJECTIONS

Status: draft  
Version: 1

## Purpose
Define projection modules that render widget outputs in diegetic and non-diegetic modes
without changing knowledge, causality, or determinism.

## Scope
This spec covers:
- Projection modes and their invariants
- Device binding and gating rules
- Pivot policy between diegetic and HUD modes
- Input routing rules for UI actions
- Performance and no-modal-loading constraints

This spec does not define capabilities, widgets, or rendering backends.

## Architecture
Projection modules are pure projections of widget outputs.

```
[ Capability Snapshot ]
        ↓
[ Widget Instances ]
        ↓
[ Projection Module ]
        ↓
[ Renderer / Input ]
```

Projection modules MUST consume only widget render outputs and capability metadata.  
Projection modules MUST NOT query authoritative world state.

## Definitions
- Projection: A pure mapping from widget output to a render target and interaction zones.
- Diegetic projection: Widgets anchored to in-world devices or surfaces.
- HUD projection: Screen-space widgets, same data and uncertainty as diegetic.
- World surface projection: Widgets rendered onto an in-world surface (table, console).
- Pivot policy: A deterministic rule for switching between projection modes.

## Projection modes
Projection modules MUST implement, at minimum:

1) HUD overlay
- Screen-space widgets.
- Uses the same capabilities as diegetic views.

2) Diegetic device projection
- Widgets anchored to devices.
- Device presence and capability provenance gate visibility.

3) World surface projection
- Widgets rendered onto a world surface.
- Uses device anchors with world-surface projection type.

4) Spectator projection (optional, privileged)
- Uses explicit privileged capability sets.
- Must be auditable.

## Device binding and gating
Device binding is driven by capability provenance and widget device tags.

Rules:
- A widget with a device tag MUST only render on anchors that match the tag.
- If a capability has source provenance, the projection MUST only use anchors
  with matching provenance when specified.
- If device presence is required and no device is available, projection MUST
  show UNKNOWN or omit the widget.

## Proximity and connection gating
Projection modules MUST enforce gating based on capability metadata:
- Proximity-limited capabilities MUST only render when in range.
- Network-dependent capabilities MUST degrade or disappear when link is down.
- Degradation MUST be visible (uncertainty widening, staleness markers).

Projection modules MUST NOT create new information when gating fails.

## Pivot policy
Projection mode switching MUST be instantaneous and purely visual.

Modes:
- DIEGETIC_ONLY
- HUD_ONLY
- HYBRID
- DEBUG (privileged)

Switching modes MUST NOT:
- change capability data
- change simulation
- change ordering of capabilities

## Input and interaction
Input routing rules:
- Widget interactions MUST map to Command Intents (CMD0) when allowed.
- Diegetic interactions require physical access (already encoded in capabilities).
- HUD interactions require capability permissions.
- No UI action may bypass communication latency or authority.

## Determinism and equivalence
Projection must be deterministic and replay-safe.

Equivalence requirements:
- The same capability snapshot MUST produce semantically equivalent widget content
  across all projection modes.
- Projection changes MUST NOT affect simulation state.

## Performance and no-modal-loading
Projection modules:
- MUST NOT perform IO.
- MUST NOT block the render thread.
- MUST use derived job system for any optional assets.
- MUST degrade gracefully when assets are missing.

## Prohibitions
Projection modules MUST NOT:
- query authoritative world state
- invent capabilities or data
- hide uncertainty or latency
- hard-code device knowledge
- create UI-only logic branches

## Examples
1) Pure diegetic
- Player uses a wristwatch device. Time widget appears on the watch display.
- Removing the watch removes the widget. HUD remains empty.

2) Pure HUD
- Player disables diegetic mode. The same time widget appears on HUD.
- Uncertainty and staleness are identical to diegetic view.

3) Hybrid
- Time widget appears both on the watch and in the HUD.
- Device loss removes diegetic view but HUD still shows UNKNOWN if capability
  is no longer available.

## Tests and validation requirements
Future tests MUST include:
- Projection semantic equivalence across modes.
- Device removal gating (diegetic disappears).
- HUD UNKNOWN on missing device capability.
- No-modal-loading checks (no IO calls).
- Replay equivalence (projection changes do not affect sim).

## Related specs
- `docs/specs/SPEC_EPISTEMIC_INTERFACE.md`
- `docs/specs/SPEC_UI_CAPABILITIES.md`
- `docs/specs/SPEC_UI_WIDGETS.md`
- `docs/specs/SPEC_INFORMATION_MODEL.md`
- `docs/specs/SPEC_EFFECT_FIELDS.md`