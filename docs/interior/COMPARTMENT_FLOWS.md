Status: CANONICAL
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: INT-2 compartment-level interior flows over FlowSystem.
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/interior/INTERIOR_VOLUME_MODEL.md`, and `docs/architecture/FLOWSYSTEM_STANDARD.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Compartment Flows

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic macro/meso compartment environment behavior (air, pressure, smoke, flooding) over `InteriorVolumeGraph` using `FlowSystem`, without CFD.

## A) Compartment Flow Philosophy
- Compartments are graph nodes; portals/vents are graph edges.
- Interior environment updates are coarse deterministic transfers over FlowChannels.
- No global micro CFD. Future micro fluid/air simulation is optional and ROI-bounded only.
- Process-only mutation applies: compartment state changes must come from deterministic process execution.

## B) Quantities Tracked (Macro/Meso)
- `air_mass` (`material.air` represented as fixed-point mass in compartment state).
- `derived_pressure` (deterministic coarse derivation from air mass and compartment volume).
- `oxygen_fraction` (fixed-point scalar `0..1` as a stub composition channel).
- `smoke_density` (fixed-point contaminant scalar).
- `water_volume` (fixed-point flooding quantity; volume channel for compartment flooding).

## C) Portal Conductance
- Each portal has flow parameters for air/water/smoke conductance.
- Portal state machine modifies effective conductance deterministically:
  - open: baseline conductance scaled by open multiplier.
  - closed/locked: conductance reduced by sealing coefficient.
  - vented/permeable: low but non-zero conductance.
  - damaged: sealing degradation increases effective conductance.
- Conductance is data-driven from registry templates + optional per-portal overrides.

## D) Failure and Hazard Integration
- Leaks are hazards that create or increase conductance to an outside boundary node.
- Leak/flood consequences are event-sourced and process-driven; no silent edits.
- Flooding state can generate movement/access constraint hooks through `ConstraintComponent`.
- Low-pressure exposure is tracked as deterministic fields for later health/survival systems.

## E) Epistemics
- Interior environment truth is not directly exposed by default.
- Diegetic users receive coarse instrument states (`OK/WARN/DANGER`) and alarms.
- Detailed numeric values are available only when law/entitlements permit.
- Inspection and overlays are derived artifacts and must respect ED-4 epistemic invariance.

## Determinism and Time Warp
- Updates are tick-based with deterministic ordering by `(graph_id, volume_id, portal_id, channel_id)`.
- Large `Δt_sim` is integrated via deterministic bounded sub-steps.
- Budget pressure degrades fidelity/update frequency deterministically, never correctness invariants.

## Conservation and Boundary Accounting
- Compartment flows must use FlowSystem and ledger-aware quantity handling.
- Boundary leaks use explicit boundary model accounting:
  - transfer to outside reservoir, or
  - declared `exception.boundary_flux` when profile allows.
- No unaccounted creation/destruction in compartment transfer paths.
