Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: tests/testx/CAPABILITY_MATRIX.yaml

# TESTX_STAGE_MATRIX (Historical)

This document is retained for historical traceability only.
It is non-normative for current TestX gating.
The canonical TestX gating matrix is capability-based.

## Canonical TestX Sources

- `tests/testx/CAPABILITY_MATRIX.yaml`
- `tests/testx/capability_suite_runner.py`
- `tests/testx/capability_regression/`

## Canonical Governance

- Runtime and test gating authority is defined in:
  - `docs/architecture/CAPABILITY_ONLY_CANON.md`
- Stage/progression identifiers are not valid runtime controls.
- Capability and entitlement checks are the only accepted gating mechanism.

## Historical Note

- Historical stage-based test descriptions are archived context only.
- Current CI/TestX enforcement is capability matrix driven and deterministic.
