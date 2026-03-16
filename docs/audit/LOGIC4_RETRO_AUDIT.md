Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC4 Retro Audit

Status: complete
Scope: LOGIC-4 deterministic evaluation engine integration
Source Prompt: LOGIC-4

## Reviewed Existing Tick And Evaluation Loops

### LOGIC signal mutation path
- `src/logic/signal/signal_store.py`
- `tools/xstack/sessionx/process_runtime.py`
- Existing signal mutation is already constrained to:
  - `process.signal_set`
  - `process.signal_emit_pulse`
- Conclusion: LOGIC-4 must schedule propagation through these process APIs or equivalent canonical helpers, not through direct signal-row writes.

### LOGIC network topology and validation
- `src/logic/network/logic_network_engine.py`
- `src/logic/network/logic_network_validator.py`
- LOGIC-3 already supplies:
  - deterministic graph ordering
  - validation records
  - loop classification
  - explain artifacts for loop findings
- Conclusion: LOGIC-4 should consume validated network bindings and refuse evaluation when validation is stale or policy-blocked.

### LOGIC element declarations
- `src/logic/element/logic_element_validator.py`
- `src/logic/element/compute_hooks.py`
- `packs/core/pack.core.logic_base/data/*.json`
- LOGIC-2 already defines:
  - explicit state vectors
  - behavior model ids
  - compute_cost_units
  - timing policy ids
- Conclusion: LOGIC-4 should evaluate these data-defined models directly and must not introduce engine-owned special gate objects.

### Core state-vector infrastructure
- `src/system/statevec/statevec_engine.py`
- `tools/xstack/sessionx/process_runtime.py`
- STATEVEC already provides deterministic definition/snapshot normalization and anchor hashing.
- Conclusion: LOGIC-4 commit behavior should reuse STATEVEC serialization and preserve canonical snapshot/hash-chain refresh.

### Existing per-tick evaluators with budgeted phases
- `src/process/process_run_engine.py`
- `src/system/macro/macro_capsule_engine.py`
- `src/process/software/pipeline_engine.py`
- Existing runtime precedent is:
  - deterministic ordering
  - compute request before execution
  - explicit derived and canonical rows
  - replay-facing hash chains refreshed in `process_runtime`
- Conclusion: LOGIC-4 should follow the same pattern rather than adding an ad hoc evaluator loop.

## Direct Mutation Audit

Reviewed:
- `src/logic/`
- `tools/xstack/sessionx/process_runtime.py`
- existing AuditX analyzer `E310_DIRECT_SIGNAL_MUTATION_SMELL`

Findings:
- No existing direct signal mutation bypass was found outside the already approved signal-store/runtime integration paths.
- No existing logic evaluation engine was found that mutates logic state outside explicit process/runtime flows.

Conclusion:
- LOGIC-4 can preserve A2 by introducing:
  - a canonical logic evaluation process
  - a canonical state-vector update helper/process seam
  - propagation through canonical signal process helpers

## Compute Budget Integration Audit

Reviewed:
- `src/meta/compute/compute_budget_engine.py`
- `src/logic/element/compute_hooks.py`
- `src/logic/network/logic_network_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

Findings:
- META-COMPUTE is already available and deterministic.
- LOGIC-1 and LOGIC-3 already request compute units for signal and topology operations.
- LOGIC-2 already includes element-scoped compute-owner helpers.

Conclusion:
- LOGIC-4 should meter:
  - per-element execution
  - per-network evaluation orchestration
  - propagation scheduling
- Any budget refusal/defer/throttle outcome must be carried into canonical throttle events and explain artifacts.

## Integration Points

### Process runtime
- LOGIC-4 belongs in `tools/xstack/sessionx/process_runtime.py` dispatch.
- It should persist:
  - logic eval runtime state
  - eval records
  - throttle events
  - trace artifacts
  - refreshed state-vector and signal-store projections

### Proof and replay
- Existing proof infrastructure already consumes deterministic hash-chain markers.
- LOGIC-4 should add logic-specific hash chains for:
  - throttle events
  - state updates
  - signal outputs

### Instrumentation
- Existing logic probe and logic analyzer surfaces already exist in META-INSTR registries.
- LOGIC-4 should bind derived traces to those surfaces without exposing omniscient truth.

### COUPLE relevance
- LOGIC-1 already emits `logic_signal_coupling_change_rows`.
- LOGIC-4 should treat propagation-driven signal changes as the canonical relevance input surface.

## Risks And Constraints

- Per-instance state vectors are not predeclared in pack data; LOGIC-4 must derive instance-scoped snapshot ownership deterministically from element definitions without weakening STATEVEC rules.
- Network graphs can contain junctions and merges; propagation traversal must therefore be graph-based and deterministic, not slot-local only.
- Mixed-loop policies already exist in validation; LOGIC-4 must refuse L1 execution when policy requires ROI or compiled proof.

## Conclusions

- No existing authoritative logic evaluator conflicts with LOGIC-4.
- Required seams already exist for:
  - validated network topology
  - signal mutation
  - state-vector serialization
  - compute budgeting
  - instrumentation and explainability
- LOGIC-4 should be implemented as:
  - deterministic SENSE/COMPUTE/COMMIT/PROPAGATE helpers
  - a process-mediated orchestration layer
  - replay/proof hash-chain integration in runtime state
