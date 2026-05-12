# SPEC_ESCALATION_POLICIES (OMNI2)

Schema ID: ESCALATION_POLICIES
Schema Version: 1.0.0
Status: binding.
Scope: deterministic escalation policy format.

## Purpose
Define escalation policies as data so enforcement is predictable, auditable,
and replay-safe.

## Escalation Policy Definition
An escalation policy contains:
- policy_id (stable token)
- scope (domain, jurisdiction, session)
- thresholds (counts within ACT windows)
- signal_weights (deterministic weighting table)
- steps (ordered escalation actions)
- decay_rules (forgiveness over ACT windows)
- explanation_classification (PUBLIC, PRIVATE, ADMIN)

## Threshold Rules
Thresholds are defined as:
- window_act (ACT tick range)
- trigger_count
- required_signals (optional list)
- refusal_codes (optional list)

## Escalation Steps
Steps are ordered, deterministic, and reference enforcement actions:
- WARN (notification only)
- THROTTLE (rate limits)
- DISCONNECT
- REVOKE_CAPABILITY
- QUARANTINE

Steps MUST reference explicit enforcement action tokens when applicable.

## Decay Rules
Decay is deterministic and ACT-based:
- decay_window_act
- decay_amount
- floor (minimum score)

## Cross-References
- Enforcement actions: `schema/integrity/SPEC_ENFORCEMENT_ACTIONS.md`
- Integrity signals: `schema/integrity/SPEC_INTEGRITY_SIGNALS.md`
