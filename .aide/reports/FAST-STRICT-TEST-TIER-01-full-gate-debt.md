Status: DERIVED
Last Reviewed: 2026-05-20
Task: FAST-STRICT-TEST-TIER-01

# Full Gate Debt

Full CTest is not the normal development gate and is not green.

Recorded historical full CTest evidence from the task context:

- `440/503` tests passed.
- `63` tests failed.
- elapsed real time: about `3227.41` seconds.

This task did not rerun full CTest. The historical result is carried as debt
context, not as new proof.

## Known Debt Categories

- stale tool routes
- docs/contracts gaps
- FAB/package validation
- process/capability invariants
- distribution/setup/launcher/ops tests
- portability/workspace checks
- full CTest wall-time
- public-header consumer checks

## Policy

- Full CTest remains T4 full/release proof.
- Full CTest is not removed.
- Full CTest is not marked green.
- Full CTest is not required for the normal `fast_strict` gate.
- T4 failures remain real blockers for full certification.

Follow-up: `FULL-GATE-DEBT-01`.
