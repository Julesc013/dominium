Status: DERIVED
Last Reviewed: 2026-03-08
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: LOGIC-2 logic element registry baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Logic Elements Baseline

## Constitutional Summary
- Added the binding logic-element doctrine in `docs/logic/LOGIC_ELEMENT_MODEL.md`.
- Frozen logic elements as pack-defined Assemblies over signal-only interfaces, explicit state vectors, behavior models, compute cost declarations, and deterministic timing policy references.
- Preserved LOGIC-0/1 scope boundaries: no network evaluator, no wall-clock timing, no hardcoded gate runtime, and no physics semantics inside logic behavior definitions.
- Preserved process-only mutation and budgeted evaluation seams for later LOGIC-3 and LOGIC-4 execution work.

## Retro-Audit Summary
- Retro consistency audit recorded in `docs/audit/LOGIC2_RETRO_AUDIT.md`.
- Existing state-machine-heavy systems remain in their home domains:
  - MOB interlocks and route-state policies remain mobility truth.
  - SYS safety patterns remain safety/process orchestration contracts.
  - PROC step graphs remain process/capsule execution structures.
- LOGIC-2 did not collapse those systems into a bespoke generic runtime. It introduced a common assembly definition layer they can integrate with later where appropriate.

## Element Definition Model

### Canonical Element Record
- `element_id`
- `description`
- `interface_signature_id`
- `state_vector_definition_id`
- `behavior_model_id`
- `compute_cost_units`
- `timing_policy_id`
- `deterministic_fingerprint`
- `extensions`

### Behavior Model Kinds
- `combinational`
- `sequential`
- `timer`
- `counter`
- `mux`

### State Machine Record
- `sm_id`
- `states`
- `transition_rules`
- `output_rules`
- `deterministic_fingerprint`
- `extensions`

## Pack-Defined Starter Elements
- Starter pack: `packs/core/pack.core.logic_base`
- Baseline element ids:
  - `logic.and`
  - `logic.or`
  - `logic.not`
  - `logic.xor`
  - `logic.relay`
  - `logic.flip_flop`
  - `logic.comparator_scalar`
  - `logic.counter_small`
  - `logic.timer_delay`
- Every starter element resolves to:
  - an Assembly declaration
  - a signal-only interface signature
  - an explicit state vector definition
  - a behavior model entry
  - a non-zero compute cost declaration

## State Vector Rules
- Every logic element must resolve `state_vector_definition_id`, including empty-state combinational elements.
- Sequential and timer-oriented behavior models resolve through explicit state-machine definitions.
- State remains explicit and declarative:
  - `logic.relay` stores `latched_output`
  - `logic.flip_flop` stores `q` and `clock_seen`
  - `logic.counter_small` stores `count`
  - `logic.timer_delay` stores `armed`, `elapsed_ticks`, and `output_state`
- State updates remain future evaluator work and are reserved for canonical `COMMIT`-phase execution in LOGIC-4.

## Validation, Instrumentation, And Compute Hooks

### Validator
- Canonical validator: `src/logic/element/logic_element_validator.py`
- Refusal code: `refusal.logic.invalid_element_definition`
- Validation checks:
  - assembly exists
  - interface exists and is signal-only
  - state vector exists and matches declared id
  - behavior model exists
  - compute cost is greater than zero
  - sequential/timer/counter/mux behavior resolves required state-machine definitions
  - physical quantity tokens are absent from logic behavior/state-machine definitions

### Instrumentation Surfaces
- Default logic-element instrumentation owner:
  - `owner_kind: logic_element`
  - `owner_id: logic.element.default`
- Measurement surfaces:
  - `measure.logic.element.output_port`
  - `measure.logic.element.state_vector`
- Control probe surfaces:
  - `control.logic.probe.attach`
  - `control.logic.probe.detach`
- Forensics surfaces:
  - `forensics.logic.element.loop_detected`
  - `forensics.logic.element.timing_violation`

### Compute Integration
- Canonical compute hook: `src/logic/element/compute_hooks.py`
- Logic evaluation owners use deterministic process ids:
  - `process.logic.evaluate.<element_id>`
  - `process.logic.evaluate.<network_id>.<element_id>`
- Instruction and memory budgeting now resolve through declared quantities and tolerance entries:
  - `quantity.compute.instruction_units`
  - `quantity.compute.memory_units`
  - `quantity.logic.signal_state`
  - `quantity.logic.bus_capture`
  - `quantity.logic.state_vector_capture`
- Over-budget behavior remains policy-driven and explainable; runtime throttle/degrade execution is reserved for LOGIC-4.

## Enforcement Coverage
- RepoX invariants added:
  - `INV-LOGIC-ELEMENT-STATEVEC-DECLARED`
  - `INV-LOGIC-ELEMENT-COMPUTE-COST-DECLARED`
  - `INV-NO-HARDCODED-GATES`
- AuditX promoted smells added:
  - `E312_HARDCODED_LOGIC_BEHAVIOR_SMELL`
  - `E313_MISSING_STATE_VECTOR_SMELL`
- TestX coverage added:
  - `test_logic_element_schema_valid`
  - `test_state_machine_definition_deterministic`
  - `test_compute_cost_required`
  - `test_no_physics_leak_in_logic_behavior`
  - `test_element_registry_hash_stable`

## Topology Integration
- `docs/audit/TOPOLOGY_MAP.json` and `docs/audit/TOPOLOGY_MAP.md` were regenerated after LOGIC-2 schema, pack, validator, analyzer, and test additions.
- Refreshed topology artifact:
  - node_count: `3956`
  - edge_count: `8208`
  - deterministic_fingerprint: `23e300dc40cf8f19e47b6d74cc43fff8db1877eea8afc0111020dae6eafeba78`

## Readiness Checklist

### LOGIC-3 Readiness (LogicNetworkGraph)
- Ready: element identities, interfaces, and state vectors are registry/pack-defined.
- Ready: signal-only interfaces are enforced.
- Ready: behavior-model and state-machine references are deterministic inputs for future graph execution.
- Ready: compute-cost declarations exist for scheduler and budget integration.
- Not implemented yet: network topology, propagation scheduling, coupling evaluation order, or loop execution policy.

### LOGIC-4 Readiness (evaluation engine)
- Ready: explicit state vectors exist for every baseline element.
- Ready: behavior models are pure declarative inputs for future `SENSE -> COMPUTE -> COMMIT -> PROPAGATE` execution.
- Ready: instrumentation and forensics surfaces exist for later loop/timing explain paths.
- Ready: compute metering seam exists for element execution.
- Not implemented yet: authoritative element stepping, compiled collapse path, oscillation handling, or ROI micro timing.

## Contract And Invariant Notes
- Canon/glossary alignment: preserved.
- Contract/schema impact: changed.
- No runtime mode flags introduced.
- No wall-clock dependency introduced.
- No carrier or physics semantics were allowed to alter logic meaning.
- No authoritative mutation path was added outside deterministic Process execution.
