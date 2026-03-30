Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored stop condition registry after final planning

# Stop Conditions and Escalation

## Hard Rule

When a stop condition is hit, convert uncertainty into manual design review. Do not prompt through architectural unknowns.

## Phase A - Governance & Interface Foundations

Stop conditions:
- Stop if AGENTS governance is not mirrored into XStack artifacts.
- Stop if task types are not mapped to validation levels and refusal behavior.
- Stop if architecture graph freeze status is unknown in the fresh snapshot.

Escalation:
- Convert policy ambiguity into manual design review rather than adding ad hoc prompt instructions.
- Freeze further governance automation until validation mapping exists.

## Phase A - SIGMA.agent_automation

Stop conditions:
- Stop implementing agent automation if AGENTS governance is not mirrored into XStack.
- Stop implementing agent automation if the architecture graph is not frozen against the fresh snapshot.
- Stop implementing agent automation if task types are not mapped to validations.

Escalation:
- Convert the gap into governance design review instead of extending prompt authority.

## Phase B - Runtime Component Foundations

Stop conditions:
- Stop if runtime kernel doctrine is not approved in manual review.
- Stop if module loader insertion points cannot be mapped in the fresh snapshot.
- Stop if state externalization or lifecycle semantics break replay assumptions.

Escalation:
- Escalate unresolved service or ABI uncertainty into architecture review with explicit state diagrams.
- Do not prompt through loader or lifecycle unknowns.

## Phase C - Build / Release / Control Plane Foundations

Stop conditions:
- Stop if the build graph lock cannot be generated from the live repo state.
- Stop if release transaction log semantics are missing or ambiguous.
- Stop if downgrade and rollback policy are not inspectable artifacts.

Escalation:
- Escalate unresolved release control semantics into operator policy review.
- Do not automate release workflows without a transaction log and rollback story.

## Phase D - Advanced Replaceability

Stop conditions:
- Stop if lifecycle manager is not frozen.
- Stop if state externalization is incomplete.
- Stop if the module loader is not capability-negotiated.
- Stop if OMEGA baseline gates drift during replacement rehearsals.

Escalation:
- Quarantine the capability and revert to docs and validator work only.
- Require replay and rollback proof before resuming.

## Phase D - hot_swappable_renderers

Stop conditions:
- Stop implementing hot-reload work if lifecycle manager is not frozen.
- Stop implementing hot-reload work if state externalization is incomplete.
- Stop implementing hot-reload work if the module loader is not capability-negotiated.

Escalation:
- Convert the uncertainty into manual design review with a cutover and rollback packet.

## Phase E - Distributed Live Operations

Stop conditions:
- Stop if event log and snapshot sync are not proven equivalent.
- Stop if authority handoff semantics are absent or disputed.
- Stop if proof-anchor quorum verification is absent.
- Stop if deterministic replication is not validated under rehearsal.

Escalation:
- Pause distributed ambitions and return to rehearsal-only design review.
- Do not promote speculative distributed work into implementation until proofs and governance converge.

## Phase E - distributed_shard_relocation

Stop conditions:
- Stop implementing distributed simulation if event log and snapshot sync are not proven.
- Stop implementing distributed simulation if authority handoff model is absent.
- Stop implementing distributed simulation if proof-anchor quorum verification is absent.

Escalation:
- Return to rehearsal-only design review and proof modeling before further implementation.

