Status: ACTIVE
Version: 1.0.0
Owner: Core Engineering
Last Updated: 2026-03-08

# LOGIC0 Retro Audit

## Scope
- Prompt: `LOGIC-0 — Cybernetic Logic Constitution (Substrate-Agnostic Control, Typed Signals, Deterministic Evaluation, Compilation Path)`
- Audit target: existing logic-adjacent deterministic control/signal/state-machine behavior that must remain distributed across canonical substrates rather than hardening into a bespoke `logic system`.
- Relevant invariants:
- `INV-PROCESS-ONLY-MUTATION`
- `INV-NO-MODE-FLAGS`
- `INV-NO-WALLCLOCK-IN-PERFORMANCE`
- `INV-NO-TRUTH-READOUT-WITHOUT-INSTRUMENT`
- `INV-ALL-EXECUTION-BUDGETED`
- `INV-TIER-CONTRACT-REQUIRED`
- `INV-COUPLING-CONTRACT-REQUIRED`
- `INV-EXPLAIN-CONTRACT-REQUIRED`

## Findings

### 1) Existing logic-like behavior is present, but not as a hardcoded LOGIC runtime
- Evidence:
  - `src/mobility/signals/signal_engine.py` centralizes deterministic MOB-8 signaling/interlocking with stable IDs, state-machine bindings, and refusal codes.
  - `src/electric/protection/protection_engine.py` centralizes breaker/fuse/relay coordination under ELEC protection helpers.
  - `src/net/policies/policy_server_authoritative.py` centralizes SIG receipt/trust/transport decisions under server-authoritative policy.
  - `src/process/software/pipeline_engine.py` centralizes PROC-8 step-graph pipeline behavior with deterministic compile/test/deploy stages.
- Impact:
  - The repo already expresses cybernetic behavior through multiple canonical substrates.
  - LOGIC-0 must define shared constitutional semantics for those patterns without collapsing them into a single bespoke domain engine.
- Migration:
  - Freeze LOGIC as a substrate-agnostic constitutional layer over typed signals, discrete state, delay/schedule policy, and process-mediated actuation.

### 2) MOB already provides a concrete state-machine + signaling integration point
- Evidence:
  - `src/mobility/signals/signal_engine.py` imports `normalize_state_machine` from `src/core/state/state_machine_engine.py`.
  - MOB signal helpers bind `signal_type_id`, `state_machine_id`, and `rule_policy_id` rather than embedding free-form branching.
- Impact:
  - LOGIC should reuse state-machine and signal substrates instead of introducing another finite-state framework.
  - Rail/interlocking style controller content can later map into LOGIC packs while continuing to actuate MOB through process paths.
- Migration:
  - Reserve LOGIC state machines as data-defined assemblies that target existing actuator/process surfaces.

### 3) ELEC relay/protection behavior is domain-specific and must not define logic semantics
- Evidence:
  - `src/electric/protection/protection_engine.py` models `breaker`, `fuse`, `relay`, `gfci`, and `isolator` as electrical protection device kinds.
  - Protection settings carry electrical thresholds and coordination policies, which are legitimate ELEC carrier constraints but not universal control semantics.
- Impact:
  - Relay-like behavior exists today, but it is correctly scoped to ELEC carrier/protection semantics.
  - LOGIC-0 must prevent future drift where electrical thresholds or units become the meaning of logic itself.
- Migration:
  - Define carriers and transducers explicitly so electrical relays remain one implementation path, not the ontology.

### 4) SIG already owns message-carrier control and epistemic constraints
- Evidence:
  - `src/net/policies/policy_server_authoritative.py` routes decisions through authoritative policy, trust, observation, and receipt handling.
  - Existing registries already reserve `ref.logic_eval_engine` in `data/registries/reference_evaluator_registry.json`.
- Impact:
  - Message-based logic is already expected to be trust/receipt mediated, not omniscient.
  - LOGIC message carriers must stay coupled to SIG trust, encryption, and provenance policies.
- Migration:
  - Treat `signal.message` and `carrier.sig` as canonical logic primitives with SIG-owned transport/trust policy, not a separate network stack.

### 5) PROC already provides deterministic step-graph and budgeted control sequencing
- Evidence:
  - `src/process/software/pipeline_engine.py` uses `request_compute` from `src/meta/compute`.
  - PROC pipeline execution already serializes compile/test/deploy steps as deterministic stage graphs with canonical records.
- Impact:
  - Control sequencing, firmware flashing, and automation pipelines already have a lawful process substrate.
  - LOGIC-0 should route actuator commands through PROC/SYS process paths rather than introducing direct controller-side mutation.
- Migration:
  - Declare logic-to-actuator coupling as process-mediated and reserve firmware/control workflows for PROC-8/LOGIC integration.

### 6) Instrumentation and reference hooks for LOGIC already exist as stubs
- Evidence:
  - `data/registries/instrument_type_registry.json` already defines `instrument.logic_probe` and `instrument.logic_analyzer` with `next_series: LOGIC-4`.
  - `data/registries/reference_evaluator_registry.json` already defines `ref.logic_eval_engine` with `status: stub` and `next_series: LOGIC-4`.
- Impact:
  - The repo already expects diegetic logic observation and reference evaluation, but intentionally has not implemented them yet.
  - LOGIC-0 should bind new contracts to these surfaces instead of inventing new debug/reference channels.
- Migration:
  - Add constitutional and enforcement links that require future logic debugging to use instrumentation and future logic verification to use the registered reference evaluator.

### 7) Compute-budget integration point is present and must be mandatory for LOGIC
- Evidence:
  - `src/process/software/pipeline_engine.py` and `src/meta/compile/compile_engine.py` both call `request_compute(...)`.
  - `data/registries/instrumentation_surface_registry.json` already exposes `measure.proc.compute_instruction_units`, `measure.proc.compute_memory_units`, `measure.system.compute_instruction_units`, and `measure.system.compute_memory_units`.
- Impact:
  - Budget metering is already canonical and observable.
  - LOGIC evaluation must consume the same `instruction_units` and `memory_units` budget system; no side scheduler or free evaluation loop is acceptable.
- Migration:
  - Add LOGIC policies and enforcement that require compute-profile binding and instrumentation-backed debug/readout.

### 8) Naming conflict audit: no direct glossary collision found, but several glossary terms remain reserved
- Evidence:
  - `docs/canon/glossary_v1.md` defines binding meanings for `Truth`, `RenderModel`, `AuthorityContext`, and verification profiles (`FAST`, `STRICT`, `FULL`).
  - No reserved glossary entry currently claims `LOGIC`, `carrier`, `transducer`, or the requested signal-type tokens.
- Impact:
  - LOGIC terminology can be introduced cleanly.
  - New docs must continue to use existing glossary meanings for truth/render/profile/authority language.
- Migration:
  - Use `Truth` and `RenderModel` exactly as glossary-defined; do not overload them in logic docs.

## Integration Points

### Actuator ports
- ELEC protection/control surfaces through electrical devices and action templates.
- MOB route/signal/interlocking surfaces through mobility switch/signal state-machine pathways.
- FLUID/THERM/SYS/PROC actuator consequences must continue to route through process execution, not direct logic writes.

### Instrumentation surfaces
- Existing diegetic instrument stubs: `instrument.logic_probe`, `instrument.logic_analyzer`.
- Existing instrumentation baseline owners already expose compute-unit measurement patterns that LOGIC should mirror.

### Compute budget engine
- `src/meta/compute/compute_budget_engine.py` is the canonical metering surface.
- `request_compute(...)` is the required entry point for LOGIC evaluators, compiled controllers, and future ROI logic traces.

## Migration Plan

### Phase A: Constitution + vocabulary
- Define LOGIC as cybernetics over typed signals, state machines, schedules, and process-mediated actuation.
- Bind LOGIC timing to TEMP schedules/delay policy and forbid a new global clock subsystem.

### Phase B: Data contracts
- Add signal/carrier/transducer/policy schemas and registries.
- Add LOGIC tier/coupling/explain contracts plus instrumentation surface coverage.

### Phase C: Enforcement
- Add RepoX/AuditX/TestX checks for substrate agnosticism, compute budgeting, instrumentation-gated debug, and profile-only rule breaking.

## Acceptance Criteria for Audit Closure
- No bespoke LOGIC runtime is introduced in LOGIC-0.
- Electrical relay/protection behavior remains ELEC carrier semantics, not universal logic semantics.
- Message-carrier control remains SIG receipt/trust governed.
- All future logic mutation routes through Processes.
- Logic observation remains instrument-gated and non-omniscient.
