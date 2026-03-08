# LOGIC-7 Debugging & Instrumentation Baseline

Status: final baseline for LOGIC-7

## Constitutional Summary

LOGIC-7 adds bounded, epistemic debugging for logic systems without introducing omniscient truth access, wall-clock dependence, or unmetered observer work. Debugging remains process-mediated through:

- `process.logic_probe`
- `process.logic_trace_start`
- `process.logic_trace_tick`
- `process.logic_trace_end`

All debug reads are constrained by META-INSTR measurement surfaces, access policies, and instrument type requirements. Internal inspection of compiled or collapsed controllers is not silent: boundary I/O remains available, while internal reads require explicit expand authorization and emit refusal or forced-expand artifacts.

## Instruments And Policies

Registered instruments:

- `instrument.logic_probe`
- `instrument.logic_analyzer`
- `instrument.protocol_sniffer_stub`

Registered sampling policies:

- `debug.sample.default`
- `debug.sample.rank_strict`
- `debug.sample.lab_high`

Registered explain contracts:

- `explain.logic_debug_refused`
- `explain.logic_debug_throttled`
- `explain.logic_debug_forced_expand`

## Throttling Behavior

Trace capture is bounded by sampling policy:

- `max_points`
- `max_ticks`
- `max_samples`
- `throttle_strategy`

Observer work is metered via META-COMPUTE. Under pressure, trace capture degrades deterministically by the declared throttle strategy rather than sampling opportunistically. Trace segments, protocol summaries, and probe artifacts are derived and compactable.

## Epistemic Constraints

- Probe reads require the matching measurement point and instrument type.
- Remote monitoring remains policy-gated and authorization-driven.
- Compiled controllers expose boundary summaries by default.
- Internal compiled inspection refuses unless force-expand is allowed and logged.
- No direct truth-model or render-model reads are introduced in LOGIC debug paths.

## Replay And Proof Surface

LOGIC-7 replay/proof coverage now includes:

- `logic_debug_request_hash_chain`
- `logic_debug_trace_hash_chain`
- `logic_protocol_summary_hash_chain`
- forced-expand hash chaining when debug requests expand compiled controllers

Reference tools:

- `tools/logic/tool_replay_trace_window.py`
- `tools/logic/tool_run_logic_debug_stress.py`

Stress artifact:

- `docs/audit/LOGIC7_DEBUG_STRESS.json`

## Readiness For LOGIC-8

Ready:

- bounded debug tracing is implemented
- protocol frame summaries are stubbed without network-stack semantics
- compiled-controller debug forcing is explicit and explainable
- replay hashes cover probe, trace, and protocol summary artifacts

Remaining for LOGIC-8:

- integrate deterministic noise/fault visualization into debug surfaces
- extend protocol interpretation beyond local frame summaries
- add fault-oriented analyzer views without expanding epistemic scope
