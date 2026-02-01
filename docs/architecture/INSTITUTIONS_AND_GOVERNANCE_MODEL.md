Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Institutions and Governance Model (GOV0)

Status: binding.  
Scope: institutions, jurisdictions, law constraints, enforcement, and governance collapse/expand.

## Core invariant
**Institutions are persistent agents that issue rules, enforce them imperfectly,
and derive authority from legitimacy, resources, and compliance — not magic.**

Institutions are not:
- omnipotent
- monolithic
- globally consistent
- always obeyed

## Primitives (authoritative)
Institutional governance is represented via:
- **Institution entities** (`schema/institution.entity.schema`)  
  Authority types, enforcement capacity, resource budgets, legitimacy references.
- **Jurisdiction scopes** (`schema/institution.scope.schema`)  
  Spatial domain bindings, subject domains, and overlap resolution policies.
- **Institution capabilities** (`schema/institution.capability.schema`)  
  Capability-to-process bindings, capacity limits, and licensing requirements.
- **Law rules** (`schema/law/*` and governance specs)  
  Rules that constrain process families and produce explicit refusals.

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Law as process constraints
Law is expressed as constraints on process families:
- rules may be **allowed**, **forbidden**, **conditional**, or **permitted with license**
- rules are data-defined, inspectable, and auditable
- refusals must cite the rule and violation reason

No law bypass exists outside meta-law and explicit overrides.

## Enforcement & compliance
Enforcement is process-driven and capacity-bounded:
- `process.law.inspect`
- `process.law.enforce`
- `process.law.penalize`
- `process.law.license`

Enforcement effectiveness depends on:
- legitimacy (T17)
- enforcement capacity and resource budgets
- local compliance rates

Low legitimacy reduces compliance and increases disputes.

## Multi-jurisdiction & conflict
Overlapping jurisdictions are supported:
- conflicts are resolved via **overlap_resolution_policy**
- resolution is fallible and data-defined
- gaps and forum shopping are expected behaviors

## Standards & regulation
Institutions may define standards and certifications:
- standards influence trust (T17) and risk (T16)
- certifications can be revoked
- no implicit global standard authority exists

## Corruption, capture & reform
Corruption is modeled as processes and information flows:
- bribery, selective enforcement, and regulatory capture are allowed
- reforms shift legitimacy and compliance
- no scripted moral outcomes

## Process-only mutation
Institutional state changes only via Process execution; there is no per-tick
global governance simulation.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- institution counts per domain (invariant)
- compliance/enforcement distributions (sufficient statistics)
- RNG cursor continuity if configured

Expand reconstructs deterministic microstate consistent with capsule stats.

## Non-goals (GOV0)
- No global omnipotent law.
- No hardcoded factions or ideologies.
- No economy or trade mechanics at this layer.

## See also
- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`