# SPEC_REFINEMENT_CONTRACTS (EXIST1)

Schema ID: REFINEMENT_CONTRACTS
Schema Version: 1.0.0
Status: binding.
Scope: deterministic refinement contracts for macro ↔ micro realization.

## Purpose
Define a data-defined, code-enforced contract that governs deterministic
expansion from LATENT/REFINABLE to REALIZED without fabricating history or
breaking conservation.

## Contract Definition (Required Fields)
- contract_id: stable identifier.
- subject_type: domain | region | cohort | city | institution | system | world | archive | other.
- allowed_from_states: LATENT | REFINABLE.
- target_state: REALIZED.
- deterministic_seed_sources: list of inputs (see `SPEC_REFINEMENT_SEEDS.md`).
- invariants: list of invariant categories to preserve.
- required_inputs: explicit inputs required to refine (provenance, ledger, schedules).
- generated_outputs: micro entities, component sets, and schedules produced.
- refusal_and_deferral: mapping to denial outcomes (see `SPEC_REFINEMENT_DENIAL.md`).
- collapse_contract_id: required inverse mapping (see `SPEC_COLLAPSE_CONTRACTS.md`).

## Invariants (Absolute)
Every refinement must preserve:
1) Conservation (population, ledger, inventories, scheduled events).
2) Provenance (no creation without causal chain).
3) Observed history (no contradictions).
4) Law compliance (existence + capability + policy).
5) Determinism (bit-identical given same inputs).

## Selection Rules
Deterministic selection order:
1) Explicit contract bound to subject instance.
2) Subject-type default contract.
3) Refuse (SUBJECT_NOT_REFINABLE).

## Law and Budget Gates
Refinement requires:
- Existence law gate (allowed to refine here).
- Capability law gate (who may force refine).
- Policy constraints (budget limits).

Failure of any gate must yield a deterministic denial outcome.

## Work IR Integration
Refinement is an authoritative effect emitted via Work IR:
- Tasks performing refinement MUST declare law_targets.
- All outputs must be auditable and deterministic.
- No runtime benchmarking or wall-clock is permitted.

## Domain Integration
Refinement respects domain volumes and ownership:
- Contracts must declare domain scope.
- Cross-domain refinement requires explicit contract coverage.

## References
- `schema/existence/SPEC_EXISTENCE_STATES.md`
- `schema/existence/SPEC_REFINEMENT_SEEDS.md`
- `schema/existence/SPEC_REFINEMENT_DENIAL.md`
- `schema/existence/SPEC_COLLAPSE_CONTRACTS.md`
