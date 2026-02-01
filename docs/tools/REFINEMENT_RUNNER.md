Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Refinement Runner

Status: canonical.
Scope: offline refinement request materialization.
Authority: canonical. This tool MUST NOT modify objective state.

## Purpose
- Materialize refinement requests as metadata.
- Emit provenance and validation targets for offline runs.
- Store outputs under `build/cache/assets/refinement_runs/`.

## Contract adherence
- The request format MUST match `docs/worldgen/REFINEMENT_CONTRACT.md`.
- Required fields MUST be present, even if marked `unspecified`.
- Failure semantics MUST be explicit (`degrade`, `freeze`, `deny`, `degrade_or_freeze`).

## Output guarantees
- Output MUST be deterministic for identical inputs.
- Output MUST NOT embed pack paths or engine state.
- Output MUST NOT be written into pack directories.