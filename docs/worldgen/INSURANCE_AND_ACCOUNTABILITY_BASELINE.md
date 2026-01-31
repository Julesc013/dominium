# Insurance and Accountability Baseline (RISK0)

Status: binding for T16 baseline.  
Scope: risk fields, liability attribution, insurance contracts, and audits.

## What exists
**Risk fields**
- Derived exposure rates and impact distributions.
- Explicit uncertainty envelopes.
- Deterministic and inspectable.

**Risk exposures**
- Accumulated exposure per risk type.
- Deterministic accumulation; no per-tick solvers.

**Risk profiles**
- Aggregated risk views for subjects and regions.
- Used for premiums and compliance checks.

**Liability**
- Events tie hazards and exposure to loss.
- Attribution is deterministic and explainable.

**Insurance**
- Policies define coverage, exclusions, premiums, and limits.
- Claims reference events and are verifiable via replay.

**Audits**
- Audit processes emit reports and adjust risk profiles and premiums.
- Audits influence behavior without scripted outcomes.

All values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What is NOT included yet
- No courtroom dispute resolution or trial mechanics.
- No economy or pricing markets.
- No per-tick stochastic solvers.

## Collapse/expand compatibility
Risk collapse stores:
- total exposure per domain (invariant)
- risk distributions by type (sufficient statistics)

Expand reconstructs consistent microstate deterministically.

## Inspection and tooling
Inspection exposes:
- risk profile values
- coverage and exclusions
- liability chain attribution
- claim histories

Visualization is symbolic and never authoritative.

## Maturity labels
- Risk fields: **BOUNDED** (deterministic, auditable).
- Liability attribution: **BOUNDED** (explainable, replayable).
- Insurance contracts: **BOUNDED** (data-defined).

## See also
- `docs/architecture/RISK_AND_LIABILITY_MODEL.md`
- `docs/architecture/HAZARDS_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
