Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# FIELD Layer Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL
Last Updated: 2026-03-01
Scope: FIELD-1 deterministic global field substrate.

## 1) FieldLayer

`FieldLayer` is a deterministic, process-driven substrate for spatially distributed values.

- Scalar fields:
  - `field.temperature`
  - `field.moisture`
  - `field.friction`
  - `field.radiation`
  - `field.visibility`
- Vector fields:
  - `field.wind`

Each layer is bound to a `spatial_scope_id` and a deterministic cell grid.

## 2) Resolution Tiers

- `macro`: canonical persisted cells updated on tick.
- `meso`: derived interpolation from macro cells (on-demand query only).
- `micro`: ROI sampling/visualization overlays (derived, budget-gated).

Truth mutation is process-only; interpolation/sampling is derived.

## 3) Update Modes

`field_update_policy` declares update sources:

- `field.static`: no automatic change.
- `field.scheduled`: deterministic tick schedule updates.
- `field.flow_linked`: deterministic updates from FlowSystem summaries.
- `field.hazard_linked`: deterministic updates from HazardModel states.

No wall-clock timers. No background nondeterministic drift.

## 4) Determinism Contract

- Field evaluation order:
  1. `field_id` sort
  2. `cell_id` sort
- Update execution only at process ticks (`process.field_tick` and approved process integrations).
- Budget degradation is deterministic and explicit: skip non-critical fields first.
- All field rows include deterministic fingerprints.

## 5) Epistemics

- Admin/observer contexts may access precise numeric values (policy-gated).
- Default diegetic contexts receive coarse bands via instruments/channels.
- Field values are surfaced through `diegetic_instruments` and channel filtering rules.

## 6) Integration Surfaces

- CTRL Effects:
  - field conditions may emit temporary effects (e.g., visibility reduction, traction reduction, icing-style reduction).
- ABS Hazard/Flow:
  - flow/hazard policies can drive field update policies.
- INT interior exchange:
  - portal/compartment boundary conditions sampled from exterior field cells.
- MECH:
  - temperature and moisture affect capacity/corrosion through deterministic modifiers/effects.
- MOB hooks:
  - traction/wind/visibility modifiers sourced via field queries.

## 7) Non-Goals (FIELD-1)

- No CFD/PDE climate simulation.
- No heavy continuous solvers.
- No direct truth mutation from render/UI/domain bypass paths.
