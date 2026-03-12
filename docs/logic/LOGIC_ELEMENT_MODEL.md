Status: AUTHORITATIVE
Last Reviewed: 2026-03-08
Version: 1.0.0
Scope: LOGIC-2 element declarations for pack-defined logic assemblies.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Logic Element Model

## 1. Purpose
LOGIC elements are pack-defined, deterministic control assemblies. LOGIC-2 defines their declaration model only. It does not introduce a logic network executor or hardcoded runtime gate objects.

## 2. Logic Element
A logic element is an Assembly with:
- `interface_signature_id`
- `state_vector_definition_id`
- `behavior_model_id`
- `compute_cost_units`
- `timing_policy_id`
- optional safety pattern references

Canonical requirements:
- ports are signal-typed only
- authoritative mutable memory is declared entirely in the state vector
- behavior declarations are data-defined and moddable
- compute cost is explicit and non-zero

## 3. Behavior Types

### 3.1 Combinational
- Pure function of input signals.
- No persistent memory beyond an explicitly empty state vector.

### 3.2 Sequential
- Next state is a pure function of `(inputs, prior_state)`.
- State commits only during future LOGIC commit/evaluation phases.

### 3.3 Timer-Based
- Uses declared timing or delay policy.
- No wall-clock dependence.
- Temporal semantics are derived from canonical tick and TEMP mappings.

### 3.4 Threshold
- Compares scalar input against declared threshold rules.
- Output remains deterministic and policy-declared.

### 3.5 Counter
- Uses bounded integer state inside the explicit state vector.
- Saturation or wrap behavior must be declared in the behavior model.

### 3.6 Multiplexer / Demultiplexer
- Routes typed signals or buses according to deterministic selector inputs.

### 3.7 Bus Driver
- Emits or reshapes typed bus payloads without changing bus semantics.

## 4. Determinism
- Behavior models must be pure and deterministic.
- All state affecting outputs must appear in the declared state vector.
- Hidden caches, implicit memory, and ad hoc mutable flags are forbidden.
- Future LOGIC execution phases must obey:
  - Sense
  - Compute
  - Commit
  - Propagate
- LOGIC-2 only declares the data needed for that future execution model.

## 5. Assembly And Interface Rules
- Every logic element is represented as an Assembly.
- Interfaces reuse the generic system interface-signature contract.
- Logic-element ports must use signal payload kinds only.
- Physical carrier semantics remain outside the logic element:
  - carriers constrain transport
  - transducers bridge carriers to signals
  - element semantics operate on typed signals only

## 6. State Vector Rules
- Every logic element must declare a `state_vector_definition_id`.
- Empty state vectors are valid for zero-memory combinational elements.
- Sequential, timer, latch, counter, and bus-driver elements must explicitly declare every output-affecting field.
- Future compiled or collapsed logic controllers must preserve equivalence to these declared state vectors.

## 7. Behavior Model Rules
- `behavior_model_id` resolves to a declared logic behavior model.
- Behavior models may reference:
  - a constitutive-model style declarative function description
  - a logic-domain state-machine definition
  - a deterministic threshold or routing description
- Behavior models must not reference physical units or electrical quantities as semantic inputs.

## 8. Compute Budgeting
- Each logic element declares `compute_cost_units`.
- Future evaluation must request compute budget before element execution.
- Over-budget handling must remain deterministic and explainable:
  - throttle
  - degrade
  - refuse
- `explain.logic_compute_throttle` remains the canonical logic explain surface for budget pressure.

## 9. Timing Policy
- `timing_policy_id` references deterministic delay/timing policy declarations.
- LOGIC-2 does not introduce a global clock subsystem.
- Timing remains derived from canonical tick, TEMP mappings, and delay policy rows.

## 10. Instrumentation And Epistemics
- Logic elements are passive by default; they expose no default control surfaces.
- Output ports may be measured through logic probes.
- State vectors require a stronger debug-capable logic instrument.
- Trace and explain artifacts remain derived and access-gated.

## 11. Modding Contract
- New logic elements are defined in packs.
- New gates, latches, counters, or timers should not require engine code changes.
- Engine/runtime code may validate declarations, but must not hardcode element truth tables or element-specific runtime branches.

## 12. Non-Goals Of LOGIC-2
- No full network evaluation engine.
- No propagation scheduler.
- No hardcoded runtime gate implementations.
- No wall-clock timing model.
- No direct physical-carrier execution.

## 13. Readiness
LOGIC-2 establishes the declaration layer needed for:
- LOGIC-3 network graph definitions
- LOGIC-4 deterministic element evaluation
- future COMPILE/SYS collapse paths for compiled controller capsules
