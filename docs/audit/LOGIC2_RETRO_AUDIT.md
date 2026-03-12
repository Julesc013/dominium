Status: DERIVED
Last Reviewed: 2026-03-08
Version: 1.0.0
Scope: LOGIC-2 retro-consistency audit for pack-defined logic elements.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# LOGIC-2 Retro Audit

## Purpose
- Audit existing state-machine and interlock patterns before introducing a logic element registry.
- Confirm that LOGIC-2 defines reusable element declarations without absorbing existing domain runtimes into a bespoke logic engine.

## Existing Patterns Reviewed

### MOB Signals And Interlocking
- Reviewed `src/mobility/signals/signal_engine.py`.
- Existing MOB signaling remains domain-specific:
  - rail/road/air signal types
  - interlocking and reservation policies
  - switch-lock and aspect transitions
- MOB state-machine rows and interlocking rules are already deterministic and process-routed.
- LOGIC-2 impact:
  - these behaviors can inform future logic-element compositions
  - they do not become canonical LOGIC elements in this phase
  - MOB keeps authority over route reservation, switch locks, and aspect law

### SAFETY Patterns
- Reviewed `src/safety/safety_engine.py` and `data/registries/safety_pattern_registry.json`.
- Existing SAFETY patterns remain substrate and hazard governance:
  - interlock
  - breaker
  - relief
  - deadman
  - graceful degradation
- SAFETY actions already route through declared processes and pattern rows.
- LOGIC-2 impact:
  - logic elements may reference safety pattern ids
  - SAFETY remains separate from LOGIC behavior execution
  - logic elements are allowed to declare safety references, not inline safety semantics

### PROC Step Graphs And Pipelines
- Reviewed `src/process/software/pipeline_engine.py` and process/QC integration paths.
- PROC already models deterministic staged behavior, compute metering, and quality gates.
- PROC step graphs are not generic logic elements:
  - they operate on process-run semantics
  - they emit run records, QC rows, and software artifacts
  - they depend on process definitions rather than signal ports
- LOGIC-2 impact:
  - timer, counter, and latch concepts may later drive PROC triggers
  - PROC pipelines remain separate runtime/process law, not logic-element instances

## Implicit Logic Behavior Already Present
- MOB signal aspect transitions and switch locks are domain-owned logic-like behavior.
- SAFETY interlocks encode deterministic guard/action relationships.
- CORE state-machine helpers already provide deterministic transition ordering.
- PROC software pipelines encode staged sequential behavior and compute consumption.

## Separation Decision
- LOGIC-2 will not migrate existing MOB, SAFETY, or PROC behavior into LOGIC.
- LOGIC-2 defines a reusable declaration layer for future pack-defined logic assemblies.
- Existing domain behavior stays authoritative in-place until later LOGIC series work explicitly integrates it through declared adapters and processes.

## Integration Seams For LOGIC-2
- Signal ports and carriers:
  - provided by LOGIC-1 signal/bus abstractions
- Interface signatures:
  - reuse `schema/system/interface_signature.schema`
  - restrict logic-element ports to signal payload kinds
- State vectors:
  - reuse `schema/system/state_vector_definition.schema`
  - require explicit owner rows for every logic element, including empty-memory combinational elements
- Safety references:
  - reference `data/registries/safety_pattern_registry.json`
- Compute budgeting:
  - reference `data/registries/compute_budget_profile_registry.json`
  - use existing `request_compute(...)` contract for later evaluation phases
- Instrumentation:
  - extend `domain.logic` surfaces for element outputs and state-vector inspection

## Naming Conflicts And Reserved Vocabulary
- `element` is already occupied by chemistry/material usage via `data/registries/element_registry.json`.
- LOGIC-2 therefore uses namespaced identifiers and files:
  - `logic_element_definition`
  - `logic_behavior_model`
  - `logic_state_machine`
- `state_machine` already exists as a generic deterministic core construct.
- LOGIC-2 keeps `state_machine_definition` as a logic-domain declaration wrapper and does not redefine the core term.

## Conclusion
- No existing domain already hardcodes a generic LOGIC runtime that conflicts with LOGIC-2.
- The repo already contains the right substrate:
  - deterministic state machines
  - process-routed mutation
  - explicit state vectors
  - instrumentation surfaces
  - compute metering
- LOGIC-2 can proceed as a registry/validation layer without semantic redesign.
