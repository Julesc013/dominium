# SPEC_ENFORCEMENT_ACTIONS (OMNI2)

Schema ID: ENFORCEMENT_ACTIONS
Schema Version: 1.0.0
Status: binding.
Scope: explicit enforcement actions and effect requirements.

## Purpose
Define enforcement as explicit, law-gated effects rather than hidden side
effects or ad-hoc punishments.

## Enforcement Action Definition
An enforcement action is an explicit effect with:
- action_id (stable token)
- scope (domain, jurisdiction, session)
- subject_ref (actor, client, account, or session)
- act_tick (ACT timestamp)
- parameters (deterministic, bounded)
- explanation_classification (PUBLIC, PRIVATE, ADMIN)

Enforcement actions MUST be auditable and replay-safe.

## Enforcement Rules
- No enforcement without an explicit action effect.
- Actions MUST be capability-gated and law-gated.
- Actions MUST be scoped and reversible where policy allows.

## Canonical Enforcement Actions (Initial)
- OP_DISCONNECT_CLIENT
- OP_THROTTLE_COMMANDS
- OP_REVOKE_CAPABILITY
- OP_QUARANTINE_SESSION
- OP_FREEZE_ACCOUNT
- OP_REQUIRE_REAUTH

## Cross-References
- Refusals: `schema/integrity/SPEC_REFUSAL_CODES.md`
- Escalation policies: `schema/integrity/SPEC_ESCALATION_POLICIES.md`
- Law targets: `schema/law/SPEC_INTEGRITY_LAW_TARGETS.md`
