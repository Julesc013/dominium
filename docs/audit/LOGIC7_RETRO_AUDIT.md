Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

## LOGIC7 Retro Audit

Date: 2026-03-08
Scope: LOGIC-7 debugging and instrumentation alignment

### Existing Instrumentation Surfaces Reviewed

- `domain.elec`, `domain.therm`, `domain.fluid`, and `domain.poll` already use META-INSTR measurement/forensics surfaces with access-policy gating.
- `domain.logic`, `logic_element`, and `logic_network` already expose placeholder measurement and forensics points in `data/registries/instrumentation_surface_registry.json`.
- Existing logic read paths are routed through instrumentation helpers:
  - `src/logic/signal/observation.py`
  - `src/logic/element/instrumentation_binding.py`
  - `src/logic/network/instrumentation_binding.py`

### Current Logic Debug Surface Status

- `instrument.logic_probe` and `instrument.logic_analyzer` already exist as registry placeholders.
- Existing logic observations are measurement-based and do not directly expose omniscient truth.
- Compiled logic already has bounded introspection and forced-expand seams in `src/logic/compile/logic_compiler.py` and `src/logic/eval/logic_eval_engine.py`.

### Truth-Leak Audit

- No dedicated LOGIC debug UI/view layer currently bypasses instrumentation.
- Existing logic observations already require:
  - measurement-point resolution
  - instrument presence
  - access-policy validation
- Existing risks are drift risks, not active leaks:
  - no canonical `process.logic_probe`
  - no bounded trace session engine
  - no protocol sniffer stub for bus/protocol summaries

### Cross-Domain Fit

- ELEC/THERM/FLUID/POLL instrumentation patterns are compatible with LOGIC debug additions.
- LOGIC debug should remain measurement-derived and compactable, matching existing domain practice.
- Compiled/collapsed controllers must default to boundary observation unless a policy-gated expand path is used.

### Routing Changes Required

- Add canonical debug processes:
  - `process.logic_probe`
  - `process.logic_trace_start`
  - `process.logic_trace_tick`
  - `process.logic_trace_end`
- Route logic trace capture through a bounded runtime state instead of ad hoc test/tool reads.
- Route compiled internal inspection through explicit forced-expand or refusal.
- Add protocol-frame derived summaries without introducing a network stack.

### Integration Points

- META-INSTR:
  - instrumentation surface registry
  - instrument type registry
  - access policy enforcement
- META-COMPUTE:
  - per-request and per-tick debug sampling budget
- PROV:
  - derived, compactable trace artifacts
  - request classification hooks for ranked auditability
- SIG:
  - remote monitoring only through authorized message-carrier channels
- SYS / LOGIC-6:
  - compiled controller boundary-only debug by default
  - internal inspection via forced expand or refusal

### Glossary / Naming Check

- No direct conflict found with canon-reserved terms in the proposed names:
  - `logic_probe`
  - `logic_analyzer`
  - `protocol_sniffer_stub`
  - `debug_trace_artifact`
- Constraint to preserve:
  - do not use names implying omniscient truth access such as `truth_probe`, `god_view`, or `raw_truth_trace`.

### Conclusion

- The repo does not already contain a hardcoded standalone “logic debugger” subsystem.
- LOGIC-7 can be added as a bounded extension of the existing instrumentation and compiled-debug seams.
