Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Protection And Fault Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL
Last Updated: 2026-03-03
Scope: ELEC-2 deterministic fault/protection/grounding framework.

## 1) Purpose

ELEC-2 formalizes electrical faults and protective behavior as deterministic, auditable, process-mediated state transitions.

No bespoke trip/fault mutation is allowed outside:

- `StateMachine` + `SafetyPattern` enforcement
- electrical fault/protection engines
- control-plane process dispatch

## 2) Fault Kinds

Canonical fault kinds:

- `fault.overcurrent`
- `fault.short_circuit`
- `fault.ground_fault`
- `fault.open_circuit`
- `fault.insulation_breakdown` (hook)
- `fault.undervoltage` / `fault.overvoltage` (hook)

Faults are represented as deterministic `fault_state` rows with severity and lifecycle status.

## 3) Protection Devices

Device classes:

- breaker
- fuse (one-shot)
- relay
- gfci/rcd
- isolator

All devices are modeled as:

- `protection_device` rows
- linked `state_machine_id`
- SAFETY pattern trigger/effect path

Direct device toggles without process/state machine are invalid.

## 4) Coordination (Selectivity)

Trip resolution is deterministic and policy-driven:

- devices grouped by `coordination_group_id`
- group policy from registry (`coord.*`)
- strict ordering:
  1. policy priority bucket
  2. device kind priority
  3. `device_id` lexical tie-break

Default behavior for `coord.downstream_first`:

- downstream device trips first when eligible
- upstream trips only when downstream is unavailable, locked out, or already failed

## 5) Grounding Policy

Grounding is meso policy, not waveform/EM simulation:

- `grounded`
- `floating`
- `bonded_neutral` (policy extension)

Ground-fault detection uses deterministic imbalance/threshold proxies tied to policy.

## 6) LOTO

Lockout/tagout is process + state-machine mediated:

- `process.elec_apply_loto`
- `process.elec_remove_loto`

LOTO effects:

- prevent re-energize/reclose actions while active
- emit refusal and event logs
- maintain deterministic role/policy gating (ranked rules may restrict operators)

## 7) Logging, Proof, Reenactment

Every fault/trip path must emit:

- `safety_event` RECORD rows
- fault/protection OBSERVATION surfaces for inspection
- decision log entries for downgrades/refusals
- proof hashes:
  - `fault_state_hash_chain`
  - `trip_event_hash_chain`

Reenactment descriptors must be able to replay trip cascade ordering.

## 8) Budgeting & Determinism

Evaluation order:

1. network `graph_id`
2. edge/node/device id
3. fault kind id

Budget degradation:

- deterministic first-N evaluation
- deferred work logged with explicit budget outcome
- no silent skip

No wall-clock dependence is permitted.
