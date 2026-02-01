Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Anti-Cheat and Integrity (OMNI2)

Status: binding.
Scope: integrity signals, refusal semantics, and enforcement actions.

## Purpose
Define anti-cheat as law + capability + integrity signals, not ad-hoc detection
or hidden punishments. The same machinery applies to competitive, anarchy, and
omnipotent contexts.

## Integrity Model
- Integrity signals are derived and non-authoritative.
- Signals inform law evaluation but never mutate state directly.
- Refusals and enforcement actions are explicit, audited outcomes.

## Anti-Cheat as Law
Anti-cheat is expressed via:
- capability law that denies tool and privileged actions,
- policy law that constrains rates and malformed intents,
- integrity law targets that gate enforcement actions.

No cheat logic exists outside law evaluation.

## Determinism and Replay
- Refusals and enforcement actions are deterministic and replay-safe.
- Integrity signals are recorded in dispute bundles and witness verification.

## Cross-References
- Integrity schema: `schema/integrity/README.md`
- Integrity law targets: `schema/law/SPEC_INTEGRITY_LAW_TARGETS.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`