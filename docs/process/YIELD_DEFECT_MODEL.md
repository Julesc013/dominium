Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Yield and Defect Model (PROC-2)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose

PROC-2 defines deterministic quality outcomes for ProcessRun outputs and formalizes optional named-RNG quality variation under explicit policy.

## A) Yield

- `yield_factor` is normalized to permille `[0, 1000]` (`[0,1]` semantic range).
- Default behavior is deterministic:
  - `yield = f(environment, tools, entropy, input_quality, spec_compliance)`
- Optional stochastic behavior is policy-gated:
  - enabled only when `yield_model.stochastic_allowed=true`
  - named RNG stream only (`rng_stream_name`)
  - RNG usage must be logged in run artifacts/proof payloads

## B) Defects

Defect flags are canonical quality outcomes:

- `contamination`
- `out_of_spec`
- `incomplete`
- `overprocessed`
- `software_bug`

Rules:

- Deterministic by default.
- Optional stochastic defect selection only when `defect_model.stochastic_allowed=true` and named RNG is declared.
- Defect outcomes must be traceable to run inputs and context.

## C) Quality Grade

- `quality_grade` is derived deterministically from:
  - `yield_factor`
  - defect severity / defect flags
- Thresholds are stable and profile-independent unless explicitly declared by model parameters.

## D) Traceability

Every output batch quality row produced by a process run must carry traceability metadata:

- `process_id`
- `process_version`
- `run_id`
- `input_batch_ids`
- `tool_ids`
- `environment_snapshot_hash`

Traceability metadata is authoritative for replay/audit and is required for later QC sampling (PROC-3) and drift analysis (PROC-6).
