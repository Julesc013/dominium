Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Pollution Dispersion Model (POLL-1)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL
Last Updated: 2026-03-05
Scope: Deterministic P1 coarse-grid dispersion, model-driven decay/deposition, and process-mediated field mutation.

## 1) Spatial Representation

- Concentration is represented as FieldLayer grids, one layer per pollutant:
  - `field.pollution.<type>_concentration`
- Cells represent coarse environmental partitions (`cell_id` / spatial node).
- Concentration fields are derived authoritative state and must be updated through process pathways only.

## 2) Dispersion Rule (Deterministic Proxy)

Per pollutant, per canonical tick, per cell (sorted deterministic order):

`new_concentration = current + injection + diffusion - decay - deposition`

Where:
- `injection`: emitted mass mapped into target cell from canonical `pollution_source_event`.
- `diffusion`: local neighbor exchange term from deterministic neighbor ordering.
- `decay`: constitutive model output from pollutant decay model.
- `deposition`: constitutive transfer from concentration to deposited mass ledger.

Constraints:
- Fixed `dt` = 1 canonical tick.
- No adaptive step size.
- No CFD / Navier-Stokes solve.
- Concentration clamped at `>= 0`.

## 3) Wind/Advection Stub

- If `field.wind` exists and policy enables wind modifier, a bounded directional bias is applied to diffusion.
- Wind coupling is deterministic and integer-quantized.
- Missing wind field implies zero advection bias (deterministic no-op).

## 4) Decay and Deposition Models

- Decay and deposition are explicit constitutive transforms selected by pollutant profile:
  - `model.poll_decay_none`
  - `model.poll_decay_half_life_stub`
  - `model.poll_deposition_stub`
- Deposition transfers mass from concentration to deposited ledger rows.
- All decay/deposition outputs must be recorded with deterministic fingerprints and hash-chain participation.

## 5) Shard Boundary Discipline

- Cross-shard transport is represented by boundary artifacts only.
- Shard-local dispersion never directly mutates foreign-shard cells.
- Boundary exchange artifacts are deterministic inputs for downstream shard updates.

## 6) Budget and Degrade Policy

- Dispersion cost is budgeted per cell update.
- If budget is exceeded, deterministic subset scheduling applies (bucketed cell partition).
- Degrade events are explicit records; no silent truncation is allowed.

## 7) Process & API Discipline

- No direct concentration writes outside process/model discipline.
- Runtime mutation path:
  1. compute deterministic dispersion deltas
  2. apply through field update process pathway
  3. persist and hash-chain resulting field and pollution artifacts

## 8) Explainability Requirements

Each dispersion/decay output must remain explainable by:
- source event chain
- field policy ID and rule ID
- pollutant decay/deposition model IDs
- budget/degrade outcome (if any)
