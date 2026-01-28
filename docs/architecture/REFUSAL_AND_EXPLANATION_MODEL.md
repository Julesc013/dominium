# Refusal and Explanation Model (OMNI2)

Status: binding.
Scope: refusal semantics, explanation levels, and audit requirements.

## Purpose
Make refusals first-class, deterministic, and explainable outcomes for any
illegal or forbidden action.

## Refusal Semantics
- Refusals are explicit objects emitted by law evaluation.
- Refusals MUST include refusal codes, violated laws, and scope.
- Refusals MUST NOT mutate authoritative state.
- Refusals MUST be auditable and replay-safe.

## Explanation Levels
Every refusal declares an explanation classification:
- PUBLIC: safe to show any observer.
- PRIVATE: shown only to the affected actor.
- ADMIN: shown only to authorized authorities.

## Integrity Signals
Integrity signals may be attached to refusals as inputs to law evaluation.
Signals do not cause punishment alone.

## Cross-References
- Refusal codes: `schema/integrity/SPEC_REFUSAL_CODES.md`
- Integrity signals: `schema/integrity/SPEC_INTEGRITY_SIGNALS.md`
- Law effects: `schema/law/SPEC_LAW_EFFECTS.md`
- `docs/arch/REALITY_FLOW.md`
