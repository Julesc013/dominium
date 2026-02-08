Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# DOC_CANON_ALIGNMENT_REPORT

## Scope

- Reconciles derived documentation with capability-only canonical runtime gating.
- Confirms canonical authority remains in `docs/architecture/CAPABILITY_ONLY_CANON.md`.

## Changes Applied

- Updated `docs/CAPABILITY_STAGES.md`:
  - Marked as historical planning vocabulary only.
  - Declared non-normative for runtime.
  - Added explicit superseded-by reference to `docs/architecture/CAPABILITY_ONLY_CANON.md`.
- Updated `docs/TESTX_STAGE_MATRIX.md`:
  - Marked as historical/non-normative.
  - Declared canonical TestX sources:
    - `tests/testx/CAPABILITY_MATRIX.yaml`
    - `tests/testx/capability_suite_runner.py`
    - `tests/testx/capability_regression/`

## Authority Verification

- `docs/architecture/CANON_INDEX.md` lists:
  - `docs/architecture/CAPABILITY_ONLY_CANON.md` as CANONICAL.
  - `docs/CAPABILITY_STAGES.md` and `docs/TESTX_STAGE_MATRIX.md` as DERIVED.
- Derived documents no longer prescribe runtime stage semantics.

## Result

- Canon contradiction between capability-only runtime law and derived stage-based guidance is removed.
