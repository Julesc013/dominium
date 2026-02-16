Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0 and `docs/canon/glossary_v1.md` v1.0.0.

# Contracts And Conservation

## Purpose
Define contract records used to declare invariants that domain and solver rows must preserve.

## Contract Definition
A Contract is a structural declaration of invariants and transition requirements.  
Contracts are not optional comments; they are binding inputs to validation and refusal behavior.

## Required Contract Semantics
Every contract row declares:
- conservation tags
- invariant notes
- refusal codes on violation
- transition requirements

## Baseline Contract Examples
- `dom.contract.mass_conservation`
- `dom.contract.energy_conservation`
- `dom.contract.ledger_balance`
- `dom.contract.epistemic_non_omniscience`
- `dom.contract.deterministic_transition`
- `dom.contract.no_penetration`
- `dom.contract.deterministic_contact_resolution`

## Refusal Semantics
When a requested transition cannot satisfy the declared contract set:
- refuse deterministically
- emit stable reason code (`refusal.contract_violation`)
- include remediation hint and relevant IDs

## Invariants
- Contracts are immutable identifiers once released.
- Violations are explicit; no silent fallback.
- Transition requirements apply to both collapse and expand paths.

## TODO
- Add formal mapping from each contract ID to canonical test coverage IDs.
- Add machine-readable severity classes for contract violations.

## Cross-References
- `docs/contracts/refusal_contract.md`
- `docs/scale/SOLVER_DOMAIN_BINDINGS.md`
- `schema/scale/domain_contract.schema`
