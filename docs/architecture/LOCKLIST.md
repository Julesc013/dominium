Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Locklist (GOV0)

Status: binding. Scope: mechanical locklist for frozen seams and reserved surfaces.

This file is normative law. Changes to any FROZEN item require an explicit override with
an expiry date recorded in `docs/architecture/LOCKLIST_OVERRIDES.json`. Overrides must
name the invariant ID they relax (matching TestX invariant IDs) and are forbidden on
release branches. Overrides must be visible in CI output.

### FROZEN

- Process-only state mutation (PROC0).
- Determinism model (RNG streams, ordering, deterministic reduction).
- Capability scope boundaries (engine/game/client/launcher/setup/tools/ops).
- Save and replay container invariants.
- Engine ABI and public headers.
- Platform runtime layer (platform/sys/launcher/setup/tools runtime surfaces).
- Renderer layer (all backends; presentational only).
- Authority model and refusal semantics.
- Collapse / expand contract and macro capsule invariants.

### RESERVED

- Incremental saves / WAL.
- Field provider plugins.
- Time policy variants.
- Advanced physics / electronics variants.
- Distributed AI planning.

### EVOLVING

- Data packs and pack taxonomies.
- Schemas marked PARAMETRIC or STRUCTURAL.
- Tools UX and diagnostics surfaces.
- Presentation layers (CLI/TUI/GUI/HUD composition).