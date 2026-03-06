# QC Sampling Model

Status: AUTHORITATIVE
Last Updated: 2026-03-06
Scope: PROC-3 deterministic QC sampling and inspection discipline.

## 1) QC Policy

Each ProcessDefinition may reference `qc_policy_id`.

A QC policy declares:

- `sampling_rate`
- `sampling_strategy_id`
- `test_procedure_refs`
- `fail_action`

Supported fail actions:

- `reject_batch`
- `rework_batch`
- `accept_with_warning`
- `quarantine`

QC remains policy-controlled:

- `qc.none` disables sampling
- processes are not forced to use QC globally

## 2) Deterministic Sampling Strategies

Sampling decision is deterministic for a given truth state.

Supported strategies:

- `sample.hash_based`
  - uses deterministic hash of `(run_id, batch_id, qc_policy_id)`
  - compares against policy threshold from `sampling_rate`
- `sample.every_n`
  - deterministic item order by `batch_id`
  - samples every Nth item (policy-controlled)
- `sample.risk_weighted`
  - deterministic base decision + deterministic risk uplift from batch/process quality severity
  - no hidden randomness

Ordering guarantees:

- batches sorted by `batch_id`
- test procedures sorted by `test_id`

## 3) Measurement Discipline

Measurement for QC is modeled as deterministic observation production.

- QC sampling emits measurement OBSERVATION rows for sampled batches.
- Measurement rows may include:
  - `instrument_id`
  - `calibration_cert_id`
  - measured quantity values
- If measurement noise is ever allowed, it must use named RNG and be proof-logged.

No omniscience:

- unsampled items produce no sampled measurement evidence
- QC visibility is governed by epistemic policy context

## 4) QC Outcomes

QC outcomes are canonical via `qc_result_record`.

Per evaluated batch:

- `sampled` (bool)
- `passed` (bool)
- `fail_reason` (optional)
- `action_taken` (`reject|rework|accept_warning|none`)
- deterministic fingerprint and traceability fields

Deterministic fail-action mapping:

- fail + `reject_batch` -> `action_taken=reject`
- fail + `rework_batch` -> `action_taken=rework`
- fail + `accept_with_warning` -> `action_taken=accept_warning`
- fail + `quarantine` -> `action_taken=reject` with quarantine tag

## 5) Integration Contracts

QC output feeds:

- process stabilization hooks (pass-rate and severity summaries)
- drift escalation hooks (threshold policy)
- certification hooks (failed QC can request invalidation)

All hooks are deterministic and event-sourced.

## 6) Explainability and Epistemics

Required explain contracts:

- `explain.qc_failure`
- `explain.qc_sampling_decision`

QC summaries expose only sampled evidence unless requester policy authorizes broader visibility.

## 7) Non-Goals

PROC-3 does not implement:

- full statistical process control dashboarding
- adaptive/ML QC policies
- process capsule abstraction (PROC-5)
