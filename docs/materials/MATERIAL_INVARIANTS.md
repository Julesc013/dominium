Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Material Invariants

## Purpose
List explicit invariants that all MAT implementations must preserve across macro, meso, and micro tiers.

## Core Invariants

### MAT-INV-01 Conservation Continuity
- `sum(material.mass_energy_total)` is preserved across collapse/expand operations, consistent with RS-2 contract set behavior and exception-ledger rules.

### MAT-INV-02 Batch Lineage Acyclicity
- Batch lineage graph is acyclic and fully traceable from any output batch to source process roots.

### MAT-INV-03 Round-Trip Stability
- `Expand -> Collapse -> Expand` preserves:
  - total stock quantities
  - quality/defect distributions within declared tolerance envelopes

### MAT-INV-04 Provenance Traceability
- Every authoritative material delta has an auditable link to process event + batch lineage context.

### MAT-INV-05 Commitment Antecedence
- Macro material state changes require antecedent commitment execution or explicit exception-ledger entry.

### MAT-INV-06 No Silent Mutation
- Material truth is never mutated by renderer, tools, or ad hoc direct writes outside process commit boundaries.

### MAT-INV-07 No Epistemic Gain Via Refinement
- Tier refinement must not reveal information unavailable under current lens/law/authority context.

### MAT-INV-08 Deterministic Identity Expansion
- Expand-assigned part IDs and batch-instance linkages are deterministic functions of canonical inputs.

## Cross-Contract Links
- RS-2 conservation contracts: `docs/reality/CONSERVATION_AND_EXCEPTIONS.md`
- RS-4 tier transitions: `docs/reality/TIER_TAXONOMY_AND_TRANSITIONS.md`
- ED-4 epistemic invariance: `docs/epistemics/LOD_EPISTEMIC_INVARIANCE.md`

## Enforcement Intent
These invariants are constitutional requirements for MAT-1..MAT-10 implementation, replay validation, and guardrail enforcement.
