# SPEC_REFUSAL_CODES (OMNI2)

Schema ID: REFUSAL_CODES
Schema Version: 1.0.0
Status: binding.
Scope: canonical refusal codes and refusal payload requirements.

## Purpose
Define refusal outcomes as first-class, deterministic objects for all command
and task admissions.

## Refusal Object (Required Fields)
- refusal_code (stable token from this registry)
- violated_law_ids (ordered list)
- violated_capability_ids (ordered list)
- integrity_signals (ordered list of signal_id)
- scope (domain, jurisdiction, session)
- explanation_classification (PUBLIC, PRIVATE, ADMIN)
- act_tick (ACT timestamp)
- context_refs (deterministic pointers to audit data)

Refusals MUST be auditable and replay-safe.

## Refusal Rules
- Refusals MUST NOT mutate authoritative state.
- Refusals MUST NOT be silent.
- Refusals MUST NOT fabricate outcomes.
- Refusals MUST be emitted for any illegal or forbidden action.

## Canonical Refusal Codes (Initial)
- REFUSE_INVALID_INTENT
- REFUSE_LAW_FORBIDDEN
- REFUSE_CAPABILITY_MISSING
- REFUSE_DOMAIN_FORBIDDEN
- REFUSE_INTEGRITY_VIOLATION
- REFUSE_RATE_LIMIT
- REFUSE_BUDGET_EXCEEDED
- REFUSE_ACTIVE_DOMAIN_LIMIT
- REFUSE_REFINEMENT_BUDGET
- REFUSE_MACRO_EVENT_BUDGET
- REFUSE_AGENT_PLANNING_BUDGET
- REFUSE_SNAPSHOT_BUDGET
- REFUSE_COLLAPSE_BUDGET
- REFUSE_DEFER_QUEUE_LIMIT

## Explanation Classification
- PUBLIC: safe to show any observer.
- PRIVATE: shown only to the affected actor.
- ADMIN: visible only to authorized authorities.

## Cross-References
- Integrity signals: `schema/integrity/SPEC_INTEGRITY_SIGNALS.md`
- Law effects: `schema/law/SPEC_LAW_EFFECTS.md`
