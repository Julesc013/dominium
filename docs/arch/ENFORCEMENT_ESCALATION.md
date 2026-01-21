# Enforcement and Escalation (OMNI2)

Status: binding.
Scope: enforcement actions, escalation policies, and admin overrides.

## Purpose
Define deterministic enforcement and escalation paths that are explicit,
scoped, and auditable.

## Enforcement Actions
- Enforcement is performed only via explicit effects.
- Actions are capability-gated and law-gated.
- Actions are scoped by domain, jurisdiction, and session.

## Escalation Policies
- Policies are data-defined and deterministic.
- Threshold rules use ACT windows and signal weighting.
- Steps are ordered and reference explicit enforcement actions.
- Decay rules are deterministic and auditable.

## Admin and Omnipotent Overrides
- Overrides require explicit capability and law targets.
- Overrides emit audit records.
- History-affecting overrides require a fork when applicable.

## Cross-References
- Enforcement actions: `schema/integrity/SPEC_ENFORCEMENT_ACTIONS.md`
- Escalation policies: `schema/integrity/SPEC_ESCALATION_POLICIES.md`
- Integrity law targets: `schema/law/SPEC_INTEGRITY_LAW_TARGETS.md`
