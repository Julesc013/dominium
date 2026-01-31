# Trust, Reputation, and Legitimacy Model (TRUST0)

Status: binding.  
Scope: trust formation/decay, reputation profiles, legitimacy constraints, and fraud handling.

## Core invariant
**Trust is a belief about reliability derived from evidence, experience, and
institutions, and decays unless actively maintained.**

Trust is not:
- a hidden stat
- a binary flag
- permanent
- globally agreed upon

## Primitives (authoritative)
Trust, reputation, and legitimacy are represented via these data primitives:
- **Trust fields** (`schema/trust.field.schema`)  
  Evidence-derived trust levels scoped by subject and context.
- **Reputation profiles** (`schema/reputation.profile.schema`)  
  Historical performance, audits, incidents, endorsements, and disputes.
- **Legitimacy fields** (`schema/legitimacy.field.schema`)  
  Authority scope and compliance/challenge/symbolic support measures.

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Trust state changes are **only** allowed via Process execution:
- `process.trust.increase`
- `process.trust.decrease`
- `process.trust.decay`
- `process.trust.transfer`

There is no per-tick social simulation. Trust evolves only when processes run.

## Trust formation & decay
Trust changes are event-driven and deterministic:
- Increases from successful outcomes, audits, and certifications.
- Decreases from incidents, disputes, and policy violations.
- Decays over time if not reinforced.
- Transfers via endorsements, with uncertainty propagated.

Trust loss accelerates after incidents; decay is bounded and rate-limited.

## Reputation profiles
Reputation profiles aggregate evidence:
- historical performance
- audit results
- incident history
- endorsements
- disputes

Profiles are inspectable, deterministic, and uncertain. They do not imply
global agreement or hidden scoring.

## Legitimacy & authority
Legitimacy gates enforcement:
- institutions require legitimacy to enforce law
- low legitimacy reduces compliance
- legitimacy loss increases refusals and disputes

Legitimacy is affected by:
- enforcement fairness
- corruption signals
- outcomes vs promises

Legitimacy is data-defined and never bypasses law/meta-law.

## Fraud, deception & misinformation
Fraud and misinformation are supported as data and processes:
- false claims
- forged certifications
- misreported audits
- propaganda signals

Detection relies on measurement (M0-LITE), audits (T16), and trust networks.
There is no omniscient truth source.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- average trust per institution (invariant)
- trust distributions and dispute rates (sufficient statistics)
- RNG cursor continuity if configured

Expand reconstructs deterministic microstate consistent with capsule stats.

## Law & refusal semantics
Trust and legitimacy processes must obey law/meta-law. Refusals must clearly
state missing evidence, failed audits, or legitimacy constraints.

Refusal semantics are governed by `docs/architecture/REFUSAL_SEMANTICS.md`.

## Non-goals (TRUST0)
- No RPG alignment systems or hidden meters.
- No per-tick social simulation.
- No scripted social outcomes.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`
