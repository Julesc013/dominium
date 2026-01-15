# SIM/PROP (Propagators)

Incremental propagators and representation updates under per-tick budgets.

## Responsibilities
- Deterministic dirty marking and incremental rebuild interfaces.
- Bounded per-tick propagation with carryover semantics.

## Non-responsibilities / prohibited
- No unbounded scans; no pointer-ordered or hash-ordered iteration.

## Spec
See `docs/SPEC_DOMAINS_FRAMES_PROP.md`, `docs/SPEC_GRAPH_TOOLKIT.md`, and `docs/SPEC_DETERMINISM.md`.

