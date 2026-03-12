Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Exposure And Compliance Model

Status: Authoritative POLL-2 doctrine  
Date: 2026-03-05

## A) Exposure Accumulation
- Exposure is deterministic and process-driven.
- Canonical increment per subject/pollutant per tick:
  - `exposure_increment = concentration * exposure_factor_permille / 1000`
- `exposure_factor_permille` may include susceptibility stubs from subject extensions.
- Exposure state is stored as:
  - `subject_id`
  - `pollutant_id`
  - `accumulated_exposure`
  - `last_update_tick`

## B) Health Risk Stub
- Exposure thresholds are registry-driven per pollutant.
- Threshold crossings emit canonical `health_risk_event` rows.
- Supported threshold levels:
  - `warning`
  - `critical`
- Health coupling remains stub-only via `hazard.health_risk_stub` accumulation/update events.
- POLL-2 does not implement disease, mortality, or epidemiology.

## C) Measurement
- Pollution sensors produce deterministic OBSERVATION artifacts:
  - measured concentration
  - pollutant id
  - spatial scope
  - optional instrument/calibration references
- Diegetic scope:
  - measurement only reveals local sampled values in instrument scope.
  - no full-map truth exposure from single local reading.
- Institutional/inspector scope:
  - aggregate statistics can be computed by dedicated reporting process under policy.

## D) Compliance Hooks
- Compliance reports are REPORT artifacts (`artifact_family_id=REPORT`).
- Reports compare observed concentration statistics against threshold baselines.
- Output statuses:
  - `ok`
  - `warning`
  - `violation`
- Violation status emits explainable event hooks; no penalties/economy consequences in POLL-2.
- Reports are dispatched through SIG pathways and can yield knowledge receipts.

## E) Determinism, Tiering, and Budgets
- POLL-2 executes on top of P1 dispersion fields.
- Ordering constraints:
  - subjects sorted by `subject_id`
  - pollutants sorted by `pollutant_id`
  - reports sorted by `(region_id, pollutant_id)`
- Budget pressure must degrade deterministically with explicit decision logs.
- No wall-clock, no nondeterministic shortcuts.

## F) Proof and Replay Surface
POLL-2 extends proof chains with:
- `pollution_exposure_hash_chain`
- `pollution_measurement_hash_chain`
- `pollution_compliance_report_hash_chain`

Replay tools must be able to recompute these chains from canonical state/event rows.
