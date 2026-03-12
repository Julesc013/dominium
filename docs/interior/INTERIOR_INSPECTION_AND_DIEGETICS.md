Status: CANONICAL
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: INT-3 interior inspection and diegetic instrumentation integration.
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/interior/INTERIOR_VOLUME_MODEL.md`, `docs/interior/COMPARTMENT_FLOWS.md`, and `docs/materials/INSPECTION_SYSTEM.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Interior Inspection and Diegetics

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Visibility Contract
- Default diegetic visibility:
  - local portal state indicators (`open|closed|locked|damaged`) when observed through legal channels.
  - coarse alarms (`OK|WARN|DANGER`) for smoke/flood/pressure hazards.
- Instrument-required visibility:
  - numeric pressure.
  - numeric oxygen fraction.
  - numeric smoke density.
  - numeric flood level.
- Admin/lab-only visibility:
  - full compartment state vectors.
  - flow channel internals and per-channel transfer details.

## Inspection Levels
- `diegetic glance`:
  - no cached inspection snapshot required.
  - panel/gauge/alarm indicators only.
- `instrument readout`:
  - low-cost derived outputs from `Perceived.now`/memory channels.
  - quantized by epistemic policy.
- `inspection snapshot`:
  - derived artifact only.
  - cached and budgeted by RS-5.
  - fidelity degrades deterministically under load.

## Epistemic Safety Rules
- Instruments and overlays must not read TruthModel directly.
- Interior detail is exposed only through policy-gated channels and sections.
- Numeric precision is quantized by visibility level:
  - diegetic players receive coarse bands by default.
  - observer/lab/admin can receive finer values when entitled.
- Inspection must never mutate canonical interior truth.

## Budget and Arbitration
- Instrument updates are low-cost and deterministic.
- Inspection snapshots consume bounded cost units and are cached by:
  - `truth_hash_anchor`
  - `interior_graph_id` (or equivalent target id)
  - fidelity + epistemic policy inputs
- Under contention:
  - degrade to coarse alarm-only outputs first.
  - refuse detailed requests only when policy/strict budget requires.
  - apply deterministic fair-share arbitration across peers.

## Interaction Surface Integration
- Portals and interior panels expose `ActionSurface` metadata.
- Surface interaction emits process intents only; no direct truth mutation.
- Required refusal semantics are explicit:
  - `refusal.interior.door_jammed`
  - `refusal.interior.not_reachable`
  - `refusal.interior.flow.forbidden_by_law`

## Determinism Rules
- Stable ordering for interior sections, overlays, and marker ids.
- No wall-clock dependency in interior inspection or diegetic channels.
- Alarm transitions are threshold-driven and deterministic for identical state/history.
