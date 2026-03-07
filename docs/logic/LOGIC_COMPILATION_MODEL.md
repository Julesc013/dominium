# LOGIC Compilation Model

Status: authoritative
Scope: LOGIC-6 deterministic compilation, proof, runtime selection, and SYS collapse seams.

## 1. Purpose

LOGIC compilation turns a validated `LogicNetworkGraph` into a compact deterministic representation that preserves LOGIC semantics under a declared validity domain. Compilation is a lawful optimization path, not a semantic fork.

LOGIC compilation exists to:
- reduce `instruction_units` and `memory_units` under `META-COMPUTE`
- preserve replay and proof integrity
- enable SYS collapse into macro capsules without hidden behavior change

## 2. Compilation Targets

### 2.1 `compiled.reduced_graph`
- Deterministically serializes the LOGIC compute relation after:
  - unreachable-node pruning
  - constant-fold recording
  - stable structural deduplication metadata
- Exact target for general validated networks.
- Preserves explicit state vector semantics and current-tick input snapshot semantics.

### 2.2 `compiled.lookup_table`
- Exact table from bounded input vector to output vector.
- Only lawful when:
  - network is purely combinational
  - total enumerated input width is within policy threshold
- Enumeration order is lexicographic over canonical input slot ordering.

### 2.3 `compiled.automaton`
- Exact composed automaton over:
  - bounded explicit state vector domain
  - bounded current-tick input vector
- Only lawful when:
  - storage/sequential behavior exists
  - total explored state space is within policy threshold

## 3. Eligibility Rules

Compilation requires:
- validated `LogicNetworkGraph`
- explicit state vector definitions for all stateful elements
- no policy-forbidden loop classification
- deterministic element ordering and canonical source serialization

Additional target rules:
- `lookup_table` requires bounded combinational input width
- `automaton` requires bounded explored state count
- `reduced_graph` is the default exact fallback target when a more compact exact target is not eligible

## 4. Canonical Source Hash

The compile source hash must include:
- logic network binding
- graph topology
- latest validation hash
- logic policy and network policy references
- element definitions
- behavior model definitions
- state machine definitions
- state vector definitions material to execution
- timing policy references that affect semantics

The same source hash under the same compile policy must produce the same:
- compiled payload hash
- equivalence proof hash
- compiled model id

Identical source hash under identical compile policy must also produce identical:
- compiled payload hash
- equivalence proof hash
- compiled model id

## 5. Equivalence Proof

Compilation is invalid without proof.

### 5.1 Exact Proof
- `reduced_graph`: structural equivalence over canonicalized compute program
- `lookup_table`: exhaustive truth-table proof over bounded input enumeration
- `automaton`: deterministic explored-state and transition-table proof over bounded state/input space

### 5.2 Bounded Proof
- Only lawful if compile policy explicitly allows it.
- Intended only for scalar quantization cases governed by TOL policy.
- Default LOGIC compile policies remain exact-only.

## 6. Validity Domains

Compiled models must declare a validity domain including:
- input slot ranges
- timing constraints
- carrier constraints or assumptions where relevant
- validation-hash anchoring

Compiled execution is only lawful when:
- proof exists and verifies
- source hash still matches
- current validation hash still matches
- current inputs remain within declared ranges

## 7. Runtime Selection

Runtime uses compiled execution when:
- `compiled_model_id` is present on the network binding
- proof exists
- validity checks pass
- no debug-driven forced expand is active

Runtime must not silently change path.

### 7.1 Valid Compiled Path
- compiled compute replaces only L1 `COMPUTE`
- `COMMIT` and `PROPAGATE` remain authoritative and unchanged
- reduced compute consumption must still be metered

### 7.2 Invalid Compiled Path
- emit `explain.logic_compiled_invalid`
- record explicit fallback to L1, or refuse if policy requires compiled-only execution

### 7.3 Debug-Driven Expand
- Debug inspection of compiled internals is instrumentation-gated.
- A lawful debug request requires:
  - `instrument.logic_analyzer`
  - the compiled-summary measurement surface for the target network
  - access-policy approval
- When granted, runtime produces a derived compactable compiled-summary artifact and forces expand to L1 for authoritative inspection.
- When not granted, compiled execution remains opaque and no internal truth is exposed.

## 8. Loop Policy Interaction

- `refuse`: L1 and compiled execution both refuse
- `force_roi`: L1 refuses and requests future L2 handling
- `allow_compiled_only`:
  - lawful only when a valid compiled model and proof are present
  - otherwise refusal is required

## 9. SYS Collapse / Expand

LOGIC controllers may collapse into SYS macro capsules through:
- `template.logic_controller`
- `macro.logic_controller.compiled`

Collapsed execution is lawful only when the compiled model remains within validity domain.

Forced expand triggers include:
- compiled validity-domain violation
- timing or oscillation anomaly
- instrumentation/debug inspection request

Forced expand must be explicit, logged, and auditable.

## 10. Explainability

Required explain/event surfaces for this layer:
- `explain.logic_compiled_invalid`
- existing `explain.logic_loop_detected`
- existing `explain.logic_timing_violation`
- existing `explain.logic_compute_throttle`

Compiled introspection remains limited:
- truth-table excerpts for `compiled.lookup_table`
- transition/state excerpts for `compiled.automaton`
- reduced-program summaries for `compiled.reduced_graph`
- all introspection artifacts are derived and compactable

## 11. Non-Goals

This layer does not add:
- new logic elements
- new network semantics
- wall-clock timing
- silent fallback
- proof bypass
