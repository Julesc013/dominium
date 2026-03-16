Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

## LOGIC5 Retro Audit

Status: complete  
Scope: LOGIC-1 delay policies, LOGIC-4 evaluation timing, TEMP mapping seams, pack-defined timing assumptions

### Existing timing surfaces reviewed

- `data/registries/signal_delay_policy_registry.json`
  - Existing delay policies already reserve `delay.none`, `delay.fixed_ticks`, `delay.temporal_domain`, and `delay.sig_delivery`.
  - Drift found: the `delay.none` registry description still implied current-tick visibility, while LOGIC-4 propagation already enforces next-tick visibility. LOGIC-5 corrects the registry wording to match canon.
- `src/logic/eval/propagate_engine.py`
  - Existing delay resolution was deterministic but partially local.
  - `delay.temporal_domain` was not yet routed through TEMP; it used edge extensions as a fallback tick offset.
- `src/logic/eval/logic_eval_engine.py`
  - Existing duplicate-tick refusal and loop-policy refusal already provide a timing-violation seam.
  - No oscillation classification or timing-constraint pass existed yet.
- `src/time/time_mapping_engine.py`
  - TEMP already exposes deterministic domain mapping, bounded cost, and deterministic fingerprints suitable for logic delay resolution.
- `packs/core/pack.core.logic_base/data/*`
  - Existing starter elements declare delay policies and explicit state vectors.
  - No oscillator, watchdog, or synchronizer behavior was hardcoded in engine code.

### TEMP and schedule usage audit

- Canonical logic timing already depends on canonical ticks, not wall clock.
- `delay.fixed_ticks` is already expressible through element and edge extensions.
- `delay.temporal_domain` existed as a declared policy but was not yet materially tied to `evaluate_time_mappings(...)`.
- Existing logic elements do not assume any global oscillator or free-running clock source.

### Implicit timing assumptions found

- `delay.none` wording drift in the signal delay registry.
- No current bounded replay artifact for oscillation detection or watchdog timeout evidence.
- No canonical network-level timing-constraint declaration or enforcement layer in LOGIC.

### Integration points confirmed

- TEMP seam:
  - `src/time/time_mapping_engine.py::evaluate_time_mappings`
  - `data/registries/temporal_domain_registry.json`
  - `data/registries/time_mapping_registry.json`
  - `data/registries/drift_policy_registry.json`
- LOGIC eval seam:
  - `src/logic/eval/logic_eval_engine.py`
  - `src/logic/eval/propagate_engine.py`
  - `src/logic/eval/runtime_state.py`
- META-COMPUTE seam:
  - `src/meta/compute/compute_budget_engine.py::request_compute`
  - `src/logic/element/compute_hooks.py`
- META-INSTR seam:
  - `data/registries/instrumentation_surface_registry.json`
  - `data/registries/instrument_type_registry.json`
- Proof/replay seam:
  - `src/control/proof/control_proof_bundle.py`
  - `tools/logic/tool_replay_logic_window.py`

### Timing-element audit

- Existing `logic.timer_delay` is pack-defined and deterministic.
- Existing element DSL can express:
  - timeout counters
  - latch stages
  - delay-based pattern templates
- That means watchdog and synchronizer patterns can remain pack-defined assemblies; no engine-only element behavior is required.

### Canon check

- No global free-running clock subsystem found in LOGIC.
- No wall-clock dependency found in LOGIC timing paths reviewed.
- No direct signal mutation bypass found in current LOGIC eval path; signal writes still flow through `process.signal_set` / `process.signal_emit_pulse`.
- No hidden timing state outside explicit runtime rows and state vectors was found; LOGIC-5 will extend those explicit rows instead of adding hidden caches.
