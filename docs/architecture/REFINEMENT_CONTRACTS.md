# Refinement Contracts (EXIST1)

Status: draft.
Scope: deterministic refinement and collapse contracts.

## Purpose
Define how LATENT/REFINABLE subjects are realized into micro state, and how
REALIZED subjects collapse back to LATENT without breaking truth.

## Contract Guarantees
Refinement and collapse must preserve:
- Conservation (population, ledger, inventories, scheduled events).
- Provenance (no fabrication; summary hashes retained).
- Observed history (no contradictions; pinned entities preserved).
- Law compliance (existence, capability, policy).
- Determinism (bit-identical given identical inputs).

## Refinement Contract Summary
Each contract specifies:
- subject_type and allowed existence states.
- deterministic seed sources and invariants.
- required inputs and generated outputs.
- denial/deferral semantics.
- collapse mapping (inverse contract).

## Collapse Contract Summary
Each contract specifies:
- deterministic aggregation rules.
- conservation checks and carryover scheduling.
- provenance summary hashing.
- pinned entity handling.

## Pipeline Overview
1) Refinement Request (intent).
2) Contract Selection (explicit > type default).
3) Law Gate (existence, capability, policy).
4) Budget Gate (defer, degrade, refuse).
5) Realization (deterministic micro creation).
6) Pinning Rules (visible entities preserved).

## References
- `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
- `schema/existence/SPEC_COLLAPSE_CONTRACTS.md`
- `schema/existence/SPEC_REFINEMENT_DENIAL.md`
- `docs/architecture/VISITABILITY_AND_REFINEMENT.md`
