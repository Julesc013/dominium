Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Instrumentation Surface Standard

Status: CANONICAL (META-INSTR-0)  
Last Reviewed: 2026-03-07  
Version: 1.0.0

## Purpose

Define a uniform, deterministic instrumentation contract for all System/Process owners:

- control surfaces (actuation)
- measurement surfaces (observation)
- forensics surfaces (explain/report endpoints)

This standard is data-driven, epistemically gated, replayable, and does not mutate truth directly.

## A) Control Surface

A control surface is a deterministic set of actuable control points.

Each `control_point` MUST declare:

- `control_point_id`
- `action_template_id` (META-ACTION mapped)
- `required_access_policy_id`
- `safety_interlock_refs` (may be empty)

Representative controls:

- breaker reset/toggle
- valve open/isolate/bleed
- throttle/setpoint classes
- process start/stop
- policy-gated request-expand controls

Control execution is lawful only when:

- authority and entitlements satisfy `required_access_policy_id`
- physical access policy is satisfied where required
- referenced safety interlocks do not refuse actuation

## B) Measurement Surface

A measurement surface is a deterministic set of measurable owner quantities.

Each `measurement_point` MUST declare:

- `measurement_point_id`
- `quantity_id`
- `instrument_type_id`
- `measurement_model_id`
- `destructive` (bool)
- `redaction_policy_id`

Measurement semantics:

- no readout without instrument + authority + access policy
- uncertainty/accuracy behavior is provided via `measurement_model_id`
- destructive measurements may consume time/material and must be policy-gated
- temporal validity must be interpreted through declared temporal domain/process context

Representative measurements:

- ELEC: voltage/current/power-factor
- THERM: temperature
- FLUID: pressure/head/flow
- POLL: concentration
- PROC: yield/defect/QC metrics

## C) Forensics Surface

A forensics surface is a deterministic set of explain/report endpoints.

Each `forensics_point` MUST declare:

- `forensics_point_id`
- `explain_contract_id`
- `redaction_policy_id`

Forensics routing requirements:

- endpoint MUST resolve through explain contracts/engine
- required inputs are contract-bound
- returned explain artifacts are redacted by requester policy and authority
- artifacts are derived/cached; canonical records remain the truth source

Representative endpoints:

- `explain.elec.trip`
- `explain.therm.overheat`
- `explain.fluid.leak`
- `explain.qc_failure`
- `explain.drift_detected`
- `explain.system_forced_expand`
- `explain.system_failure`

## D) Epistemics and Access

Instrumentation visibility/control is not omniscient by default.

Minimum requirements:

- lawful `AuthorityContext`
- matching access policy (`required_access_policy_id`)
- required instrument type for measurement
- physical access proof where policy requires it

Aggregated dashboards and summaries:

- MUST be derived views
- MUST be redaction-policy gated
- MUST NOT bypass truth/renderer separation

## Integration Contracts

- Action Grammar:
  - control points MUST map to declared `action_template_id`.
- Info Grammar:
  - measurement outputs are `OBSERVATION` (policy may promote to canonical record where contract declares).
  - forensics outputs route through explain artifacts/contracts.
- Certification/Drift:
  - instrumentation surfaces may be used as certification/drift inputs but cannot bypass certification/drift process rules.
- Replay/Determinism:
  - owner/surface lookups and output ordering MUST be deterministic.

## Non-Goals

- no new physics/process solvers
- no wall-clock coupling
- no default mandatory instrument packs at boot
