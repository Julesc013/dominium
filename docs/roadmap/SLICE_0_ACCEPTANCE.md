Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SLICE-0 Acceptance

SLICE-0 is complete when all items below are satisfied:

Boot and loading:
- Product boots with zero packs installed.
- Loading screen shows engine/game version, build number, protocol/schema versions,
  determinism status, pack discovery summary, template registry status.

World creation:
- Built-in templates are available with zero packs.
- World creation UI lists templates, edits parameters, and writes a WorldDefinition to save.
- No hardcoded topology, bodies, spawn locations, or camera modes.

Navigation:
- Spawn is defined only by WorldDefinition.
- Navigation modes are policy-driven and auditable.

Save/load/replay:
- Saves embed the full WorldDefinition.
- Unknown fields are preserved on round-trip.
- Replays can be inspected without packs.
- Missing capabilities cause explicit refusal or degraded modes.

UI parity:
- CLI/TUI/GUI share identical commands and refusal semantics.
- Console is unified and non-authoritative.
- HUD/debug are read-only by default.

Tools:
- World inspector, snapshot viewer, replay viewer, and template diff/validation tools
  are accessible and headless-safe.

Tests:
- Product boots with zero packs.
- Built-in templates generate schema-valid WorldDefinitions.
- World creation works via CLI/TUI/GUI.
- Navigation respects policy layers.
- Console parity across UI modes.
- Save/load/replay round-trip determinism.
- Lint/static test ensures no hardcoded identifiers (Earth/Sol/etc).