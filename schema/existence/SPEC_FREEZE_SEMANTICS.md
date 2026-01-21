# SPEC_FREEZE_SEMANTICS (EXIST2)

Schema ID: FREEZE_SEMANTICS
Schema Version: 1.0.0
Status: binding.
Scope: freezing rules for subjects and worlds.

## Purpose
Define freezing as an explicit, law-gated effect that preserves truth and
prevents mutation without erasing history.

## Freeze Effect
- Operation: OP_FREEZE_SUBJECT
- Required inputs:
  - subject_id
  - authority_id
  - law_target
  - cause_id

Freeze requires explicit authority capability and law approval.

## While Frozen
- No state mutation is allowed.
- No scheduled events fire.
- Local time does not advance.
- Observation is allowed only if permitted by epistemic laws.

## Freeze Invariants (Absolute)
- Freezing must not drop scheduled events.
- Freezing must not corrupt provenance.
- Freezing must not alter causal history.
- Freeze transitions are explicit and auditable.

## Thawing
Unfreezing (if allowed) must be an explicit effect with law gating. No implicit
thawing is permitted.

## Work IR Integration
Freeze is an authoritative effect:
- Tasks performing freeze MUST declare law_targets.
- Audit records must include subject_id, cause_id, and law decision.

## References
- `schema/existence/SPEC_ARCHIVAL_STATES.md`
