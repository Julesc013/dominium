Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META-CONTRACT-0 Retro Consistency Audit

Status: AUDIT
Last Updated: 2026-03-04
Scope: Mandatory tier/coupling/explain declaration coverage across existing substrate domains.

## 1) Tier Contract Coverage (Current State)

Observed:

- Tier taxonomy exists in `data/registries/tier_taxonomy_registry.json`.
- Domain-level tier behavior exists in code/docs for ELEC/THERM/MOB/SIG/PHYS.
- Deterministic downgrade pathways are implemented in runtime and control/performance lanes.

Gap:

- No single mandatory registry declaring per-subsystem:
  - `supported_tiers`
  - deterministic downgrade order
  - explicit cost model id
  - micro ROI constraints
  - shard safety declaration

Migration note:

- Introduce `tier_contract_registry.json` and bind current behavior as declarations without changing execution semantics.

## 2) Coupling Contract Coverage (Current State)

Observed:

- Coupling mechanisms already exist:
  - constitutive model registry
  - energy transformation registry
  - field update policies
  - signal/trust policies
- Cross-domain direct mutation checks already exist in RepoX/AuditX.

Gap:

- No mandatory coupling declaration registry linking domain pair + coupling class + mechanism id.
- Existing couplings are inferable from implementation but not centrally declared as a governance contract.

Migration note:

- Introduce `coupling_contract_registry.json` for declared cross-domain mechanisms.

## 3) Explainability Coverage (Current State)

Observed:

- Explain-like artifacts exist for some paths (for example electrical trip explanations).
- Decision logs, safety events, hazard records, and proof artifacts exist.
- Inspection output already exposes domain-specific diagnostics.

Gap:

- No mandatory explain contract per event kind defining required cause-chain and remediation keys.
- No general explain artifact schema that is domain-neutral and policy-redactable.

Migration note:

- Introduce explain contract/artifact schemas + registry entries for elec/therm/mob/sig/mech baseline failures.

## 4) Existing Domain Snapshot

- ELEC:
  - tier behavior present, coupling present, explain path present (`process.elec.explain_trip`), not centrally contract-declared.
- THERM:
  - tier and coupling behavior present, overheat explanations are implicit via hazard/state records, no explicit explain contract row.
- MOB:
  - tier behavior present and deterministic, derailment causes exist in hazard/decision paths, no mandatory explain contract row.
- SIG:
  - info coupling and trust acceptance behavior present, delivery loss explain path is implicit, no explicit explain contract row.
- PHYS:
  - tier policy and cross-domain couplings present via PHYS-0..4 registries, but no dedicated tier/coupling contract registry rows.

## 5) Minimal Patch Plan

1. Add canonical docs for mandatory Tier/Coupling/Explain contracts.
2. Add strict schemas for:
   - tier contract
   - coupling contract
   - explain contract
   - explain artifact
3. Add registries covering ELEC/THERM/MOB/SIG/PHYS baseline declarations.
4. Add derived explain engine helper module (deterministic + redaction + cache key).
5. Add RepoX strict invariants for declaration presence and undeclared coupling guard.
6. Add AuditX smells for missing declaration classes.
7. Add TestX coverage for registry/schema + deterministic explain behavior.
8. Integrate topology + semantic impact for contract nodes and coupling-change suite selection.
