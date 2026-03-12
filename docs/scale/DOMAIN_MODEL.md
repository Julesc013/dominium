Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0 and `docs/canon/glossary_v1.md` v1.0.0.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Domain Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define the canonical structural meaning of a Domain for scale governance.

## Scope
- Structural and governance only.
- No solver math or simulation semantics are defined here.

## Domain Definition
A Domain is a taxonomy over:
- Assemblies (what is grouped)
- Fields (what is observed/mutated)
- Processes (what mutation families are lawful)

Domains:
- do not introduce new primitives
- are registry-defined, not hardcoded
- are optional via pack/capability gating
- may bind to one or more solver records
- use stable IDs that are never reused

## Invariants
- `INV-DOMAIN-REGISTRY-VALID`: all domain rows must validate against declared schema.
- `INV-NO-HARDCODED-DOMAIN-TOKENS`: runtime/tool code must not hardcode `dom.domain.*` literals outside governance registries/docs.
- `INV-SOLVER-DOMAIN-BINDING`: solver rows must bind to explicit `domain_ids` and `contract_ids`.

## Canon Alignment
- Constitution A4/A9: no mode-flag branching, pack/registry-driven integration.
- Constitution A10: explicit refusal/degrade behavior when bindings are invalid.

## Compatibility Notes
- Domain IDs are append-only in practice.
- Deletions/renames require compat documentation and versioned migration policy.

## Example Domain ID Set
- `dom.domain.gravity.macro`
- `dom.domain.orbital.mechanics`
- `dom.domain.geology.terrain`

## TODO
- Add machine-readable registry diff policy for release checks.
- Add explicit deprecation lifecycle state machine for domain IDs.

## Cross-References
- `docs/scale/DOMAIN_REGISTRY.md`
- `docs/scale/CONTRACTS_AND_CONSERVATION.md`
- `docs/scale/SOLVER_DOMAIN_BINDINGS.md`
- `schema/scale/domain_registry.schema`
