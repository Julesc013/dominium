# SPEC_COLLAPSE_CONTRACTS (EXIST1)

Schema ID: COLLAPSE_CONTRACTS
Schema Version: 1.0.0
Status: binding.
Scope: deterministic collapse contracts for micro → macro aggregation.

## Purpose
Define the inverse mapping from REALIZED to LATENT that preserves invariants
and provenance. Collapse is never deletion; it is deterministic aggregation.

## Contract Definition (Required Fields)
- contract_id: stable identifier.
- subject_type: domain | region | cohort | city | institution | system | world | archive | other.
- allowed_from_states: REALIZED.
- target_state: LATENT.
- aggregation_rules: deterministic summarization of micro state.
- conservation_checks: explicit checks for population, ledger, inventories.
- provenance_summary: hashing inputs and method.
- schedule_carryover_rules: deterministic carryover of due events.
- pinned_entity_rules: how visible/interactive entities are preserved.

## Invariants (Absolute)
Every collapse must preserve:
1) Conservation (population, ledger, inventories, scheduled events).
2) Provenance (summary hash and links to micro provenance).
3) Observed history (pinned/visible entities are preserved).
4) Law compliance (collapse is law-gated).
5) Determinism (bit-identical given same inputs).

## Pinned Entities
Pinned or visible entities cannot be collapsed. Contracts must:
- Define pin criteria.
- Ensure pinned entities persist across collapse.

## Work IR Integration
Collapse is an authoritative effect:
- Tasks performing collapse MUST declare law_targets.
- Outputs must be auditable and deterministic.

## References
- `schema/existence/SPEC_EXISTENCE_STATES.md`
- `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
