Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Trust and Reputation Baseline (TRUST0)

Status: binding for T17 baseline.  
Scope: trust fields, reputation profiles, and legitimacy constraints.

## What exists
**Trust fields**
- Evidence-derived trust levels per subject/context.
- Explicit uncertainty envelopes.
- Deterministic, inspectable, and process-driven.

**Reputation profiles**
- Historical performance, audits, incidents, endorsements, disputes.
- Aggregated, uncertain, and inspectable.

**Legitimacy fields**
- Authority scope, compliance rate, challenge rate, symbolic support.
- Used to gate law enforcement and dispute rates.

**Fraud and misinformation**
- False claims and forged certifications are data-defined.
- Detection relies on measurement and audits.

All values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What is NOT included yet
- No alignment meters or RPG reputation bars.
- No per-tick social simulation.
- No scripted social outcomes.
- No automated dispute adjudication.

## Collapse/expand compatibility
Trust collapse stores:
- average trust per institution (invariant)
- trust distributions and dispute rates (sufficient statistics)

Expand reconstructs consistent microstate deterministically.

## Inspection and tooling
Inspection exposes:
- trust relationships and contexts
- reputation profiles and uncertainty
- legitimacy levels and authority scope
- evidence sources, audits, and disputes

Visualization is symbolic and never authoritative.

## Maturity labels
- Trust fields: **BOUNDED** (deterministic, auditable).
- Reputation profiles: **BOUNDED** (evidence-driven, inspectable).
- Legitimacy fields: **BOUNDED** (law-gated, replayable).

## See also
- `docs/architecture/TRUST_AND_LEGITIMACY_MODEL.md`
- `docs/architecture/RISK_AND_LIABILITY_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`