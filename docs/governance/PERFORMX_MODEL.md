Status: CANONICAL
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# PerformX Model

PerformX is the deterministic performance envelope system for Dominium governance.

## Core Concepts

- **Envelope**: declarative workload policy with metrics and tolerances.
- **Profile**: coarse hardware normalization class.
- **Canonical results**: deterministic, hash-stable semantic outputs.
- **Run metadata**: non-canonical diagnostics (timestamps, host details).

## Determinism Contract

- Canonical outputs must have stable ordering and no run-time fields.
- Determinism checks compare canonical artifacts only.
- Hardware normalization influences interpreted metrics, not identity invariants.

## Regression Policy

- Regressions are detected against an explicit baseline artifact.
- Severity defaults to `warn`; `fail` is only for explicitly critical envelopes.
- Raw hardware variance alone does not constitute a failure.

## Integration

- TestX verify lane runs critical performance envelopes.
- TestX dist lane runs the full performance envelope set.
- ControlX and automation route through `scripts/dev/gate.py` only.

