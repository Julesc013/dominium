Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: docs/architecture/CAPABILITY_ONLY_CANON.md

# CAPABILITY_STAGES (Historical Planning Vocabulary)

This document is retained for planning vocabulary only.
It is non-normative for runtime behavior.
All runtime gating authority is defined in `docs/architecture/CAPABILITY_ONLY_CANON.md`.

## Canonical Runtime Authority

- Runtime command, pack, and UI gating MUST use capabilities and entitlements only.
- Runtime schemas and manifests MUST NOT encode stage/progression fields.
- Runtime refusal behavior for gating is capability-based, not stage-based.

## Test Authority

- Capability gating validation is defined by:
  - `tests/testx/CAPABILITY_MATRIX.yaml`
  - `tests/testx/capability_suite_runner.py`
  - `tests/testx/capability_regression/`

## Planning Note

- Historical stage labels may be used in planning discussions only.
- Stage labels are not runtime identifiers and confer no execution authority.
