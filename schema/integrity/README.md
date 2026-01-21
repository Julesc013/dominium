--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses integrity schema for signals, refusals, and enforcement actions.
SCHEMA:
- Canonical integrity signal, refusal, and escalation formats.
TOOLS:
- Audit and dispute tooling consumes integrity records.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Integrity Schema (OMNI2)

This folder defines deterministic integrity signals, refusal semantics, and
enforcement actions for anti-cheat and policy enforcement.

Specs:
- `SPEC_INTEGRITY_SIGNALS.md`
- `SPEC_REFUSAL_CODES.md`
- `SPEC_ENFORCEMENT_ACTIONS.md`
- `SPEC_ESCALATION_POLICIES.md`

Related:
- Integrity law targets: `schema/law/SPEC_INTEGRITY_LAW_TARGETS.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
