# Safety Pattern Library and Interlock Framework

Status: CANONICAL
Last Updated: 2026-03-03
Scope: SAFETY-0

## 1) Objective

The Safety Pattern Library (SPL) defines a universal, data-driven safety contract so protective logic is reusable across domains and never implemented as ad-hoc branch code.

SAFETY-0 introduces pattern templates and deterministic evaluation hooks only. It does not introduce new ontology primitives and does not change existing domain semantics.

## 2) Allowed Substrates

Safety patterns must compose only these existing substrates:

- ABS `StateMachineComponent`
- ABS `ConstraintComponent`
- ABS `HazardModel`
- ABS `ScheduleComponent`
- CTRL effect application and decision logging
- SPEC compliance constraints and thresholds
- META-ACTION action/process declaration and validation

## 3) Canonical Pattern Types

All safety logic must map to one of the following pattern types.

### A) INTERLOCK

- Triggering conditions:
  - conflicting state/action predicates are true
  - examples: occupied block + switch throw request, incompatible mode transition request
- Enforced actions:
  - deny transition
  - lock constraint path
  - apply explicit refusal code
- Hazards/effects:
  - optional warning effect
  - optional blocked-operation hazard marker
- Logging requirements:
  - required conflict predicate snapshot
  - required blocked action/process id
  - required deterministic instance and tick

### B) FAIL-SAFE DEFAULT

- Triggering conditions:
  - explicit fault, invalid control state, or declared control/power loss predicate
- Enforced actions:
  - transition to declared safe default state
  - apply protective cap effect if needed
- Hazards/effects:
  - fault hazard or incident marker
  - safe-default effect row
- Logging requirements:
  - fault source
  - resulting safe state
  - transition cause

### C) RELIEF / LIMIT PROTECTION

- Triggering conditions:
  - threshold exceeds configured safe bound
- Enforced actions:
  - open relief path or cap load/pressure/temperature
- Hazards/effects:
  - over-limit hazard marker
  - relief-open effect marker
- Logging requirements:
  - threshold id/value
  - measured value
  - enforced relief action

### D) BREAKER / TRIP

- Triggering conditions:
  - load/capacity predicate exceeds trip threshold
- Enforced actions:
  - disconnect declared flow/channel/path
  - transition breaker state machine to tripped
- Hazards/effects:
  - trip event marker
  - flow-disconnect effect
- Logging requirements:
  - trip threshold
  - observed load
  - disconnected target ids

### E) REDUNDANCY

- Triggering conditions:
  - primary path/component unavailable or unhealthy
- Enforced actions:
  - switch to fallback component/path using deterministic priority or quorum
- Hazards/effects:
  - degraded-capacity effect
  - redundancy-fallback marker
- Logging requirements:
  - active path before/after
  - fallback policy id
  - reason predicate

### F) DEADMAN / WATCHDOG

- Triggering conditions:
  - `current_tick - last_heartbeat_tick >= timeout_ticks`
- Enforced actions:
  - forced stop/shutdown/cap
  - optional lock until reset
- Hazards/effects:
  - watchdog-timeout hazard marker
  - stop/cap effect
- Logging requirements:
  - timeout threshold
  - last heartbeat tick
  - auto action applied

### G) LOCKOUT / TAGOUT (LOTO)

- Triggering conditions:
  - maintenance lock exists and controlled operation is requested
- Enforced actions:
  - refuse operation
  - preserve lock/tag state
- Hazards/effects:
  - maintenance lock hazard marker
  - optional panel warning effect
- Logging requirements:
  - lock owner/tag id
  - blocked operation
  - maintenance context ref

### H) GRACEFUL DEGRADATION

- Triggering conditions:
  - risk enters declared degrade band without hard-fail trigger
- Enforced actions:
  - apply deterministic reduced-capacity profile
- Hazards/effects:
  - degradation hazard marker
  - speed/throughput/quality cap effects
- Logging requirements:
  - degrade band
  - profile id
  - resulting cap values

## 4) Thermal Pattern Hooks (THERM-0 Prep)

Registered thermal templates extend canonical types and do not add new safety families:

- `safety.overtemp_trip` (FAIL-SAFE DEFAULT)
  - trigger: overtemperature hazard threshold crossed
  - enforced action: deterministic shutdown/trip effect on target subsystem
  - logging: target id, observed temperature, threshold, policy id

- `safety.thermal_runaway` (GRACEFUL DEGRADATION hook)
  - trigger: runaway-risk predicate enters configured band
  - enforced action: warning + deterministic degradation effect
  - logging: target id, runaway risk metric, policy id

## 5) Safety Pattern Contract

Each safety pattern template must declare:

- `pattern_type`
- deterministic `triggering_conditions`
- deterministic `enforced_actions`
- `required_substrates`
- produced hazards/effects
- required event/log payload fields

Each safety instance must declare:

- `pattern_id`
- target ids
- active flag
- creation tick
- deterministic fingerprint

## 6) Determinism, Budget, and Replay

- Evaluation order is stable by `instance_id`.
- No wall-clock dependency is permitted.
- Named RNG usage is forbidden unless an explicit policy row declares it (none in SAFETY-0 baseline).
- Budget degradation is deterministic:
  - lower-sorted instances execute first
  - deferred instances are explicit and logged
- Every trigger and enforced action emits a deterministic safety event record for replay/proof.

## 7) Governance Rules

- Protective logic in runtime code must be represented by registered safety patterns.
- Complex domain behavior must compose patterns; it must not create new hardcoded safety families.
- Domain docs may provide examples, but semantics must remain SPL-driven.

## 8) Non-Goals

- no domain-specific solver implementations
- no semantic changes to mobility/signals/mechanics process behavior
- no new ontology primitives
