Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Risk and Liability Model (RISK0)

Status: binding.  
Scope: risk quantification, liability attribution, insurance contracts, and audits.

## Core invariant
**Risk is quantified uncertainty about future loss, derived from hazards,
exposure, and system fragility, and is never eliminated—only transferred or
mitigated.**

Risk is not:
- a hit chance
- a hidden dice roll
- a global difficulty scalar

## Primitives (authoritative)
Risk and accountability are represented via these data primitives:
- **Risk fields** (`schema/risk.field.schema`)  
  Derived exposure rates, impact distributions, and uncertainty envelopes.
- **Risk exposures** (`schema/risk.exposure.schema`)  
  Accumulated exposure records for subjects and regions.
- **Risk profiles** (`schema/risk.profile.schema`)  
  Aggregated risk views for actors/assets/domains.
- **Liability events** (`schema/liability.event.schema`)  
  Loss events tied to hazards and exposure.
- **Liability attribution** (`schema/liability.attribution.schema`)  
  Deterministic responsibility splits with causality and compliance.
- **Insurance policies** (`schema/insurance.policy.schema`)  
  Contracts defining covered risks, exclusions, and limits.
- **Insurance claims** (`schema/insurance.claim.schema`)  
  Claims referencing events with auditable outcomes.

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Risk state changes are **only** allowed via Process execution:
- `process.audit.inspect`
- `process.audit.report`
- `process.audit.enforce`

Derived risk fields and liability/claim outcomes are produced by explicit
processes and never by per-tick background solvers.

## Risk derivation
Risk is derived from hazards and exposure:
- hazard fields inform exposure rates
- exposure and fragility shape impact distributions
- uncertainty is propagated, never erased

Risk is deterministic and replayable for identical inputs and ordering.

## Liability attribution
Attribution must consider:
- ownership and control
- negligence or policy violations
- standards compliance
- causality chain (process provenance)

Attribution is deterministic and explainable; disputes are recorded for later
resolution (not adjudicated here).

## Insurance contracts
Insurance contracts are data-defined and process-admitted:
- covered risks and exclusions
- premiums and payout limits
- audit requirements
- claim verification via replay/logs

No scripted outcomes or hidden dice rolls are permitted.

## Audits & compliance
Audits are explicit processes that:
- generate information artifacts
- adjust risk profiles and premiums
- influence later trust/legitimacy layers

Audit effects are deterministic, scoped, and logged.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- total exposure per domain (invariant)
- risk distributions by type (sufficient statistics)
- RNG cursor continuity if configured

Expand reconstructs deterministic microstate consistent with capsule stats.

## Law & refusal semantics
Risk and insurance processes must obey law/meta-law. Refusals must clearly
state violations, missing audits, or insufficient coverage.

Refusal semantics are governed by `docs/architecture/REFUSAL_SEMANTICS.md`.

## Non-goals (RISK0)
- No scripted consequences or narrative events.
- No continuous stochastic solvers.
- No combat mechanics.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`