# SPEC_INTEGRITY_SIGNALS (OMNI2)

Schema ID: INTEGRITY_SIGNALS
Schema Version: 1.0.0
Status: binding.
Scope: deterministic integrity signals for law evaluation.

## Purpose
Define integrity signals as derived, non-authoritative indicators that inform
law decisions without mutating authoritative state.

## Integrity Signal Definition
An Integrity Signal is a deterministic record with:
- signal_id (stable token)
- source_ref (client, server, tool, witness)
- scope (domain, jurisdiction, session)
- act_tick (ACT timestamp)
- subject_ref (optional actor/session/subject)
- evidence_ref (hash or audit pointer)
- parameters (deterministic, bounded)

Signals MUST be auditable and replay-safe.

## Signal Rules
- Signals never mutate authoritative state directly.
- Signals never cause punishment alone.
- Signals are inputs to law evaluation and escalation policies.
- Signal generation MUST be deterministic and derived-only.

## Canonical Signals (Initial)
- CLIENT_MODIFIED
- CLIENT_DESYNC
- INVALID_COMMAND_SHAPE
- PROTOCOL_VIOLATION
- RATE_LIMIT_EXCEEDED
- REPLAY_MISMATCH
- WITNESS_HASH_MISMATCH

## Cross-References
- Refusals: `schema/integrity/SPEC_REFUSAL_CODES.md`
- Enforcement actions: `schema/integrity/SPEC_ENFORCEMENT_ACTIONS.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
